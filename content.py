import streamlit as st
from google import genai

API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

st.cache_data()
def ask_gemini(movie):
    prompt = f"""
    Summarize the movie '{movie}' in 20 words. You MUST explicitly name its genre(s) 
    and highlight its core hook or thematic conflict. Keep the tone engaging and tailored as a personal recommendation.
"""
    try:
        response = client.models.generate_content(
        model="gemini-3.5-flash-lite", contents=prompt
        )
        if hasattr(response, "text") and response.text: # response object safely contains a text attribute and that its value is a non-empty string before attempting to use it
            return response.text
    except Exception as e:
        return f"Gemini Error: {e}"

