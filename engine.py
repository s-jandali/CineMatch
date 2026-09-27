import pandas as pd
import streamlit as st
import joblib

@st.cache_data
def load_data():
    try:
        movies_data = joblib.load("Data/Movies_Data.pkl")
        user_data = joblib.load("Data/User_data.pkl")
        model_svd = joblib.load("Data/Model_SVD.pkl")
        cosine_sim = joblib.load("Data/Similarity.pkl")
        return movies_data, user_data, model_svd, cosine_sim
    except Exception as e:
        st.error(f"🚨 Not able to load the files due to {e}")
        return None, None, None, None

movies_data, user_data, model_svd, similarity = load_data()

def check_id(id):
    if id == "":
        return("🚨 Please prompt the ID")
        
    try:
        id_int = int(id)
    except ValueError:
        return("🚨 Please enter the digits of ID")
        
    if id_int not in user_data['User Id'].values:
        return("🚨 Kindly prompt the correct ID")
        

def recommendation(user_id, top=5, alpha=0.5):
    """
    alpha: controls the weight of content vs collaborative
        1.0 = pure content-based
        0.0 = pure collaborative (SVD)
    """

    # Get a list of all movies the user has ALREADY rated (to avoid re-recommending them)
    rated_movies = user_data[user_data['User Id'] == user_id]['Movie Title'].unique()

    # Find the user's highest-rated movie to seed the content component
    user_top_movies = user_data[user_data['User Id'] == user_id].sort_values(by='Rating', ascending=False)

    # Fallback for brand new users (Cold Start problem)
    # Give them top-rated global movies
    if user_top_movies.empty:
        return movies_data.sort_values(by='vote_average', ascending=False)

    # The most favorate movies we can relied on for our recommendation
    seed_movie = user_top_movies.iloc[0]['Movie Title'].strip().lower()
    # Discover if there is any mismatching between user data and movies data
    if seed_movie not in movies_data['title'].apply(lambda x: x.strip().lower()).values:
        return movies_data.sort_values(by='vote_average', ascending=False)
    
    idx = movies_data[movies_data["title"].apply(lambda x: x.strip().lower())==seed_movie].index[0]

    # Extract content similarity scores for all movies relative to the seed movie
    content_scores = similarity[idx]

    hybrid_scores = []
    rating_min = user_data['Rating'].min()
    rating_max = user_data['Rating'].max()

    for index, row in movies_data.iterrows():
        movie_title = row['title']
        # Skip movies the user has already watched
        if movie_title in rated_movies:
            continue

        c_score = content_scores[index]

        # Predict Collaborative Rating via SVD and normalize it to a [0, 1] range
        predicted_rating = model_svd.predict(str(user_id), movie_title).est # Surprise models internally store user and item IDs as strings during training
        svd_scores = (predicted_rating - rating_min) / (rating_max - rating_min)

        # Calculate weighted hybrid score (formula)
        final_score = (alpha * c_score) + ((1 - alpha) * svd_scores)
        hybrid_scores.append((index, final_score))

    # Sort and extract top items
    hybrid_scores = sorted(hybrid_scores, key=lambda x: x[1], reverse=True)[:top]
    scores = [x[1] for x in hybrid_scores]
    indices = [x[0] for x in hybrid_scores]
    
    #Build the final dataset
    recommendations = pd.DataFrame({
    'Movies': movies_data['title'].iloc[indices].values,
    'Confidence': [f"{s*100:.1f}%"for s in scores]
    })

    return recommendations.set_index('Movies')





if __name__ == "__main__":
    
    err = check_id(5)
    if err:
        print(err)
    else:
        print(recommendation(5))
    
    