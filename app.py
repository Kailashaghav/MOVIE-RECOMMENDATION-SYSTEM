import streamlit as st
import pickle
import pandas as pd
import requests
import os
import gdown

# ── Auto-download similarity.pkl from Google Drive if not present ──
if not os.path.exists('similarity.pkl'):
    with st.spinner('Downloading similarity data for the first time... please wait ⏳'):
        url = 'https://drive.google.com/uc?id=1tJ5uqsk3MyCQLIpx7QOxIKLmhBFIEL_B'
        gdown.download(url, 'similarity.pkl', quiet=False)

# ── Load data ──
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ── Fetch movie poster from TMDB ──
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.get(url, timeout=10)
        data = response.json()

        if 'poster_path' in data and data['poster_path'] is not None:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"

    except:
        return "https://via.placeholder.com/500x750?text=Error"

# ── Recommendation logic ──
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

# ── Streamlit UI ──
st.title("🎬 Movie Recommendation System")

movie_list = movies['title'].values

selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button("Show Recommendation"):
    with st.spinner('Fetching recommendations...'):
        names, posters = recommend(selected_movie)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])