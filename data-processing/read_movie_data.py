"""Read data from http://128.2.204.215:8080/movie/<movieid>
and save it in a csv file
"""

import csv
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
from functools import lru_cache

import pandas as pd
import requests
from data_processing.constants import api_endpoint
from tqdm import tqdm


class MovieDataCSVGenerator:
    movie_descriptions = defaultdict(dict)
    outdata = []
    kafka_log_file_path = ''

    @lru_cache(10)
    def get_movie_data_cached(self, movie_id):
        movie_data = GetDataByMovieId(movie_id).get_data()
        return movie_data

    def populate_outdata(self):
        for _, data in self.movie_descriptions.items():
            if len(data) == 0:
                continue
            self.outdata.append(data)

    def write_to_csv(self):
        with open('movie_data_from_api.csv', 'w', newline='') as new_csv_file:
            field_names_list = [
                'adult',
                'budget',
                'genres',
                'movieid',
                'imdb_id',
                'original_language',
                'original_title',
                'overview',
                'popularity',
                'release_date',
                'revenue',
                'runtime',
                'status',
                'title',
                'tmdb_id',
                'vote_average',
                'vote_count',
            ]
            csv_writer = csv.DictWriter(
                new_csv_file,
                fieldnames=field_names_list,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
            )
            csv_writer.writeheader()
            csv_writer.writerows(self.outdata)

    def read_from_kafka_csv(self):
        with open(self.kafka_log_file_path, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                print(row)
                movie_id = row[3]
                movie_info = self.get_movie_data_cached(movie_id)
                print(movie_id, movie_info)
                self.movie_descriptions[movie_id] = movie_info

    def read_from_kafka_csv_unique(self):
        df = pd.read_csv(self.kafka_log_file_path, header=None)
        df = df.rename(columns={0: 'user_id', 1: 'movie_title', 2: 'year', 3: 'movie_id'})
        movies = pd.Series(df['movie_id'].unique())
        for i in tqdm(range(len(movies))):
            if movies[i] == "movie_id":
                continue
            movie_info = self.get_movie_data_cached(movies[i])
            self.movie_descriptions[movies[i]] = movie_info
            
    def run(self):
        self.read_from_kafka_csv_unique()
        self.populate_outdata()
        self.write_to_csv()
        
    def __init__(self, kafka_log_file_path):
        self.kafka_log_file_path = kafka_log_file_path
        

from data_processing.constants import api_endpoint


class GetDataByMovieId:
    api = ''

    def get_movie_from_api(self):
        return requests.get(f'{self.api}')
    
    def get_data(self):
        response = self.get_movie_from_api()
        if response.status_code == 200:
            myjson = response.json()
            row = {}
            row['adult'] = myjson['adult'] if 'adult' in myjson else ''
            row['budget'] = myjson['budget'] if 'budget' in myjson else ''

            if 'genres' in myjson:
                genre_list = []
                for g in myjson['genres']:
                    genre_list.append(g['name'])
                row['genres'] = ','.join(genre_list)
            else:
                row['genres'] = ''

            row['movieid'] = myjson['id'] if 'id' in myjson else ''
            row['imdb_id'] = myjson['imdb_id'] if 'imdb_id' in myjson else ''
            row['original_language'] = (
                myjson['original_language'] if 'original_language' in myjson else ''
            )
            row['original_title'] = myjson['original_title'] if 'original_title' in myjson else ''
            row['overview'] = myjson['overview'] if 'overview' in myjson else ''
            row['popularity'] = myjson['popularity'] if 'popularity' in myjson else ''
            row['release_date'] = myjson['release_date'] if 'release_date' in myjson else ''
            row['revenue'] = myjson['revenue'] if 'revenue' in myjson else ''
            row['runtime'] = myjson['runtime'] if 'runtime' in myjson else ''
            row['status'] = myjson['status'] if 'status' in myjson else ''
            row['title'] = myjson['title'] if 'title' in myjson else ''
            row['tmdb_id'] = myjson['tmdb_id'] if 'tmdb_id' in myjson else ''
            row['vote_average'] = myjson['vote_average'] if 'vote_average' in myjson else ''
            row['vote_count'] = myjson['vote_count'] if 'vote_count' in myjson else ''
            # TODO
            # Not added production_countries, production_companies,
            # spoken_languages, belongs_to_collection
            return row

        else:
            print(f'{response.status_code} error with your request')
            return {}


    def formatted_print(self, obj):
        text = json.dumps(obj, sort_keys=True, indent=4)
        print(text)

    def __init__(self, api):

        self.api = api_endpoint + '/movie/' + api


if __name__ == '__main__':
    # api_call = GetDataByMovieId("http://128.2.204.215:8080/movie/goldeneye+1995")
    MovieDataCSVGenerator('user_movie.csv')
