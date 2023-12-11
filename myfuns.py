import numpy as np
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

N_MOVIES = 3706

genres = list(
    sorted(set([genre for genres in movies.genres.unique() for genre in genres.split("|")]))
)

def get_displayed_movies():
    return movies.head(100)

def get_recommended_movies(new_user_ratings):
    # new_user_ratings has this format: {1: 1, 2: 1}
    # have to convert it to like this: [ 3.  4. nan ...  3. nan  2.]
    user_ratings_list = [np.nan] * N_MOVIES
    
    for movie_index, rating in new_user_ratings.items():
        if movie_index <= N_MOVIES:
            user_ratings_list[movie_index - 1] = rating  # Subtract 1 because list indices start at 0
            
    user_ratings_list = np.array(user_ratings_list)
    
    recommended_movies = myIBCF(user_ratings_list)
    recommended_movies_df = pd.Series(recommended_movies).reset_index()
    recommended_movies_df.columns = ['movie_id', 'rating']
    
    recommended_movies_df['movie_id'] = recommended_movies_df['movie_id'].str.replace('m', '').astype(int)
    
    # Merge the datasets on movie_id
    merged_dataset = pd.merge(recommended_movies_df, movies, on='movie_id', how='left')
    merged_dataset.drop('rating', axis=1, inplace=True)
    
    return merged_dataset

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

def myIBCF(newuser):
    """
    Perform item-based collaborative filtering for a new user.
    """
    top_S_df = pd.read_csv('similarity_matrix.csv', index_col=0)
    ci_ratings = pd.read_csv('ci_ratings.csv', index_col=0)
    ci_ratings = ci_ratings.iloc[:, 0]
    
    movies_index=top_S_df.columns
    
    user_rated_indices = np.argwhere(~np.isnan(newuser)).flatten()
    predictions = pd.Series(data=np.zeros(N_MOVIES), index=movies_index, name="rating")

    for i in range(N_MOVIES):
        movie_ratings = top_S_df.iloc[i]
        common_indices = np.intersect1d(user_rated_indices, np.argwhere(~np.isnan(movie_ratings)).flatten())

        if len(common_indices) > 0:
            numerator = np.sum(movie_ratings[common_indices] * newuser[common_indices])
            denominator = np.sum(movie_ratings[common_indices])

            if denominator != 0:
                predictions[i] = numerator / denominator

    predictions = predictions[predictions > 0].sort_values(ascending=False)
    top_recommended = predictions[:10]

    if len(top_recommended) < 10:
        additional_movies = (ci_ratings[~predictions.index.isin(top_recommended.index) & np.isnan(newuser)]
                             .sort_values(ascending=False)[:10 - len(top_recommended)])
        top_recommended = pd.concat([top_recommended, additional_movies])

    return top_recommended
