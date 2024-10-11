from flask import Flask, request, render_template, flash, redirect, url_for
import pickle
import pandas as pd
import requests
import time
import gdown

app = Flask(__name__)
app.secret_key = "supersecretkey"

API_KEY = '8265bd1679663a7ea12ac168da84d2e8'

# Load the movie data and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# URL for the file from Google Drive
url = 'https://drive.google.com/uc?id=1973jZbAIkoJUNcwutQ6EEuxIfked4GYS'
output = 'similarity.pkl'

# Download the file from Google Drive
gdown.download(url, output, quiet=False)
# Load the pickle file
with open('similarity.pkl', 'rb') as f:
    similarity = pickle.load(f)

# Function to fetch movie details from TMDB
def fetch_movie_details(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US')
    data = response.json()

    poster_url = "https://via.placeholder.com/500x750?text=No+Image+Available"
    if 'poster_path' in data and data['poster_path']:
        poster_url = "https://image.tmdb.org/t/p/w500/" + data['poster_path']

    movie_details = {
        'poster': poster_url,
        'title': data.get('title', 'Title not available'),
        'overview': data.get('overview', 'No overview available'),
        'release_date': data.get('release_date', 'Unknown'),
        'rating': data.get('vote_average', 'No rating'),
        'genres': [genre['name'] for genre in data.get('genres', [])],
        'runtime': data.get('runtime', 'Unknown'),
    }
    return movie_details

# Function to recommend movies
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return []

    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        movie_details = fetch_movie_details(movie_id)
        recommended_movies.append(movie_details)
    return recommended_movies

# Route for the main page
@app.route('/')
def index():
    movie_titles = movies['title'].values
    return render_template('index.html', movies=movie_titles)

# Route for recommendations
@app.route('/recommend', methods=['POST'])
def recommend_movies():
    selected_movie = request.form.get('movie')

    if not selected_movie:
        flash("Please select a movie!", "error")
        return redirect(url_for('index'))

    flash("Fetching recommendations for you...", "loading")
    
    # Simulate loading time
    time.sleep(2)

    recommendations = recommend(selected_movie)

    if not recommendations:
        flash("No recommendations found for the selected movie.", "error")

    return render_template('index.html', movies=movies['title'].values, selected_movie=selected_movie, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
