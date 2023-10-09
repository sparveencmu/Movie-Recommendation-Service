import unittest
import csv
import sys
from unittest.mock import MagicMock
# from data_processing.read_movie_data import MovieDataCSVGenerator
from data_processing.read_movie_data import GetDataByMovieId, MovieDataCSVGenerator


class TestMovieDataWriter(unittest.TestCase):

    def test1(self):

        with open('test1.csv', 'w', newline='') as csvfile:
            field_names_list = ['user_id', 'movie_name', 'year', 'movie_id']
            csv_writer = csv.DictWriter(
                csvfile,
                fieldnames=field_names_list,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
            )
            csv_writer.writeheader()
            movie1 = {}
            movie1['user_id'] = "user1"
            movie1['movie_id'] = "movie1"
            movie1['year'] = 1999
            movie1['movie_name'] = "movie1"

            movie2 = {}
            movie2['user_id'] = "user2"
            movie2['movie_id'] = "movie2"
            movie2['year'] = 1999
            movie2['movie_name'] = "movie2"

            movies = [movie1, movie2]
            csv_writer.writerows(movies)

        def side_effect_func(value):
            row = {}
            if value == "movie1":
                row['title'] = "test1-movie1"
            else:
                row['title'] = "test1-movie2"

            return row

        movieDataWriter = MovieDataCSVGenerator('test1.csv')
        movieDataWriter.get_movie_data_cached = MagicMock(side_effect=side_effect_func)
        movieDataWriter.run()
        titles_in_csv = []
        with open('movie_data_from_api.csv', 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                titles_in_csv.append(row['title'])
        self.assertEqual(titles_in_csv, ["test1-movie1", "test1-movie2"])

    def test_api_fetch(self):
        movie_fetcher = GetDataByMovieId("123")

        class MockResponse:
            def __init__(self, json, status_code):
                self.json_body = json
                self.status_code = status_code

            def json(self):
                return self.json_body

        def side_effect_func():
            json = {
                "budget": "200",
                "imdb_id": "123"
            }
            return MockResponse(json, 200)

        movie_fetcher.get_movie_from_api = MagicMock(side_effect=side_effect_func)
        row = movie_fetcher.get_data()
        self.assertEqual("200", row['budget'])
        self.assertEqual("", row["adult"])


if __name__ == '__main__':
    unittest.main()