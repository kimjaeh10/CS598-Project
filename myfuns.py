import pandas as pd
import requests

# Define the URL for movie data
myurl = "https://liangfgithub.github.io/MovieData/movies.dat?raw=true"

# Fetch the data from the URL
response = requests.get(myurl)

# Split the data into lines and then split each line using "::"
movie_lines = response.text.split('\n')
movie_data = [line.split("::") for line in movie_lines if line]

# Create a DataFrame from the movie data
movies = pd.DataFrame(movie_data, columns=['movie_id', 'title', 'genres'])
movies['movie_id'] = movies['movie_id'].astype(int)

genres = list(
    sorted(set([genre for genres in movies.genres.unique() for genre in genres.split("|")]))
)

def get_displayed_movies():
    return movies.head(100)

def get_recommended_movies(new_user_ratings):
    return movies.head(10)

def get_popular_movies(genre: str):
    ratings = pd.read_csv('Rmat.csv', index_col=0)

    # Replace 'm' in column names
    ratings.columns = ratings.columns.str.replace('m', '')

    # Replace 'u' in index names
    ratings.index = ratings.index.str.replace('u', '')

    def calculate_popularity(avg_rating, num_rating, total_ratings):
        return avg_rating * 0.7 + (num_rating / total_ratings) * 0.3

    avg_ratings = ratings.mean().to_dict()
    num_ratings = ratings.count().to_dict()

    # Filter movies by genre
    genre_movies = movies[movies['genres'].str.contains(genre)]

    # Calculate popularity for each movie in the genre
    movie_scores = {}
    for _, row in genre_movies.iterrows():
        movie_id = str(row['movie_id'])
        if movie_id in avg_ratings and movie_id in num_ratings:
            movie_scores[movie_id] = calculate_popularity(avg_ratings[movie_id], num_ratings[movie_id], ratings.shape[0])

    # Sort movies by popularity
    sorted_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)

    # Return the top 10 movies in the genre
    top_movies = [movies[movies['movie_id'] == int(movie_id)] for movie_id, _ in sorted_movies[:10]]
    return pd.concat(top_movies)