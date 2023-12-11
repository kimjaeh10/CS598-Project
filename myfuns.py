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
    file_name = 'top_10_movies_' + genre + '.csv'

    try:
        # Read the CSV file for the specified genre
        top_movies = pd.read_csv(file_name)
        
        top_movies.rename(columns={"MovieID": "movie_id"}, inplace=True)

        top_movies['Genres'] = top_movies['Genres'].apply(lambda x: '|'.join(eval(x)))

        transformed_df = top_movies[['movie_id', 'Title', 'Genres']].rename(columns={"Title": "title", "Genres": "genres"})
        
        return transformed_df

    except FileNotFoundError:
        print(f"No data available for genre: {genre}")
        return pd.DataFrame()
