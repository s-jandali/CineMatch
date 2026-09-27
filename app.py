import streamlit as st
from engine import check_id, recommendation
from poster import get_movie_poster
from content import ask_gemini


# Set webpage configuration
st.set_page_config(
    page_title='CineMatch | Movie Recommender',
    page_icon='🎬',
    layout='wide'
)

st.sidebar.header('⚙️ Engine Settings')
num_recommendations = st.sidebar.slider('Number of recommendations', min_value=3, max_value=15, value=5)
alpha = st.sidebar.slider(
    'Engine Balance', min_value=0.0, max_value=1.0, value=0.5,
    help="1.0 focuses entirely on movie attributes. 0.0 focuses entirely on community behavior."
)
st.sidebar.markdown("---")

# Main Page Headers
st.title('🎬 CineMatch')
st.subheader('Hybrid Movie Recommendation Engine')
st.write('Type the user ID and will recommend the best choices for you')

# User input UI elements
col1, col2 = st.columns([2,2], vertical_alignment="bottom")

with col1:
    user_id = st.text_input("Enter your user ID ", help="Press find recommendation button", placeholder="Enter the user ID number")
with col2:
    search_clicked = st.button("Find Recommendations", use_container_width=True, type='primary')

# Excution and results display
if search_clicked:
    with st.spinner("Analyzing cinematic metadata patterns..."):
        error_id = check_id(user_id)
        if error_id:
            st.error(error_id)
        else:
            user_id = int(user_id)
            recomm = recommendation(user_id, top=num_recommendations, alpha=alpha)
            posters = []
            summaries = []
            for x, row in recomm.iterrows():
                poster = get_movie_poster(x)
                posters.append(poster)
                summary = ask_gemini(x)
                summaries.append(summary)
            recomm['posters'] = posters
            recomm['summaries'] = summaries

        MOVIES_PER_ROW = 5

        for i, (movie_title, row) in enumerate(recomm.iterrows()):
            # Creat a new row of 6 columns at index 0, 6, 12, etc
            if i % MOVIES_PER_ROW == 0:
                cols = st.columns(MOVIES_PER_ROW)

            # Determine column position within the current row (0 to 5)
            col_index = i % MOVIES_PER_ROW
            

            with cols[col_index]:
                poster_url = row['posters']
                if poster_url:
                    st.image(poster_url, width=150)
                else:
                    st.image("https://via.placeholder.com/150x225?text=No+Poster", width=150)

                st.markdown(f"**{movie_title}**")
                st.markdown(f"{row['summaries']}")
                st.caption(f"Match: {row['Confidence']}")




            


    

