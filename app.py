import pickle
import streamlit as st
import requests
import pandas as pd
import os


st.set_page_config(layout="wide", page_title="Movie Recommender", page_icon="🎬")


# -------------------- API KEY --------------------



try:
    API_KEY = st.secrets["TMDB_API_KEY"]
except KeyError:
    st.error("API Key not found! Please configure .streamlit/secrets.toml properly.")
    st.stop()


# -------------------- HUGGING FACE: SIMILARITY --------------------
@st.cache_data(show_spinner=True)
def load_similarity():
    url = "https://huggingface.co/datasets/mohammadzubair5/similarity-data/resolve/main/similarity.pkl"
    filename = "artifacts/similarity.pkl"

    os.makedirs("artifacts", exist_ok=True)

    if not os.path.exists(filename):
        with st.spinner("Downloading recommendation model (first run only)..."):
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

    with open(filename, "rb") as f:
        return pickle.load(f)


# -------------------- HUGGING FACE: MOVIES --------------------
@st.cache_data(show_spinner=True)
def load_movies():
    url = "https://huggingface.co/datasets/mohammadzubair5/similarity-data/resolve/main/movie_dict.pkl"
    filename = "artifacts/movie_dict.pkl"

    os.makedirs("artifacts", exist_ok=True)

    if not os.path.exists(filename):
        with st.spinner("Downloading movie dataset (first run only)..."):
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

    with open(filename, "rb") as f:
        return pickle.load(f)






# -------------------- CSS--------------------



st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0B0B0B;
    color: #f8fafc;
}

/* Title Gradient */
h1 {
    font-weight: 800 !important;
    background: -webkit-linear-gradient(45deg, #f43f5e, #8b5cf6) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    padding-bottom: 20px;
    text-align: center;
}

.stButton > button {
    background: linear-gradient(90deg, #f43f5e, #e11d48);
    color: white;
    border: none;
    border-radius: 8px;
    height: 50px;
    width: 250px;
    font-weight: 600;
    font-size: 16px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(225, 29, 72, 0.2);
    display: block;
    margin: 0 auto;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(225, 29, 72, 0.4);
    color: white;
}

/* Netflix-Style Movie Card Container */
.movie-card {
    background-color: #141414;
    border-radius: 12px;
    padding: 12px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    border: 1px solid rgba(255,255,255,0.05);
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border 0.3s ease;
    cursor: pointer;
    margin-bottom: 20px;
    height: 100%;
}

/* Clean shadow simulation on hover */
.movie-card:hover {
    transform: scale(1.03) translateY(-3px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.15);
    z-index: 10;
}

.poster-box {
    width: 100%;
    aspect-ratio: 2/3;
    overflow: hidden;
    border-radius: 8px;
    margin-bottom: 12px;
}

.poster-box img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease, filter 0.3s ease;
}

.movie-card:hover .poster-box img {
    transform: scale(1.02);
    filter: brightness(1.1);
}

.movie-card-title {
    font-size: 16px;
    font-weight: 800;
    color: #ffffff;
    text-align: center;
    margin-bottom: 5px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.3;
}

.movie-card-meta {
    font-size: 14px;
    font-weight: 600;
    color: #a3a3a3;
    display: flex;
    justify-content: center;
    gap: 12px;
    align-items: center;
}

/* Mobile responsiveness: reduce font size slightly on small screens */
@media (max-width: 768px) {
    .movie-card-title {
        font-size: 13px !important;
    }
    .movie-card-meta {
        font-size: 11px !important;
    }
    h1 {
        font-size: 24px !important;
    }
}

/* Selectbox */
div[data-baseweb="select"] > div {
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
}

/* Footer Styling */
.footer {
    position: relative;
    margin-top: 80px;
    padding-top: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    text-align: center;
    font-size: 14px;
    color: #94a3b8;
    padding-bottom: 20px;
}

.footer a {
    color: #f43f5e;
    text-decoration: none;
    font-weight: 600;
    transition: color 0.3s ease;
}

.footer a:hover {
    color: #e11d48;
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)




# -------------------- FETCH POSTER --------------------



def fetch_poster(movie_id):
    
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    try:
        data = requests.get(url, timeout=30)  # Set a timeout for the request
        data.raise_for_status()  # Raise an exception for bad status codes
        data = data.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
    # Return a placeholder if the poster is not found or an error occurs
    return "https://placehold.co/500x750/333/FFFFFF?text=No+Poster"





# -------------------- RECOMMEND --------------------



def recommend(movie):
    """Recommends 5 similar movies based on the selected movie."""
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Movie not found in the dataset. Please select another one.")
        return [], [], [], []
        
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_years = []
    recommended_movie_ratings = []

    for i in distances[1:6]:
        # fetch the movie details
        movie_id = movies.iloc[i[0]].movie_id
        
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_years.append(movies.iloc[i[0]].year)
        recommended_movie_ratings.append(movies.iloc[i[0]].vote_average)

    return recommended_movie_names, recommended_movie_posters, recommended_movie_years, recommended_movie_ratings



# -------------------- TITLE --------------------



st.markdown("<h1 style='text-align: center;'>Movie Recommender System 🎬</h1>", unsafe_allow_html=True)
st.caption("Deployed on Streamlit Cloud ☁️")




# -------------------- LOAD DATA --------------------


movies_dict = load_movies()
movies = pd.DataFrame(movies_dict)

similarity = load_similarity()




# -------------------- UI --------------------



movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    with st.spinner('Finding recommendations...'):
        recommended_movie_names, recommended_movie_posters, recommended_movie_years, recommended_movie_ratings = recommend(selected_movie)
    
    if recommended_movie_names:
        st.markdown("<h2 style='text-align: left; padding-top: 20px; font-weight: 800; color: #ffffff;'>Recommended Movies</h2>", unsafe_allow_html=True)
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                year = recommended_movie_years[i]
                year_str = f"{int(year)}" if pd.notna(year) else "N/A"
                rating = recommended_movie_ratings[i]
                
                card_html = f'''
                <div class="movie-card">
                    <div class="poster-box">
                        <img src="{recommended_movie_posters[i]}" alt="{recommended_movie_names[i]}">
                    </div>
                    <div class="movie-card-title" title="{recommended_movie_names[i]}">{recommended_movie_names[i]}</div>
                    <div class="movie-card-meta">
                        <span>{year_str}</span>
                        <span>{rating:.1f} ⭐</span>
                    </div>
                </div>
                '''
                st.markdown(card_html, unsafe_allow_html=True)





# -------------------- FOOTER --------------------


st.markdown("""
<div class="footer">
    <p>Designed & Developed by Mohammad Zubair | <a href="https://github.com/mohammadzubair-2543/movie-recommendation-system.git" target="_blank" rel="noopener noreferrer">GitHub Repository</a></p>
</div>
""", unsafe_allow_html=True)