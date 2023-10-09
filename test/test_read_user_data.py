import unittest
import csv
from unittest.mock import MagicMock

from data_processing.read_user_data import UserDataCSVGenerator, GetDataByUserId


class MyTestCase(unittest.TestCase):
    def test_something(self):

        with open('test2.csv', 'w', newline='') as csvfile:
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
            if value == "user1":
                row['age'] = "11"
            else:
                row['age'] = "22"

            return row

        user_data_writer = UserDataCSVGenerator("test2.csv")
        user_data_writer.get_user_data_cached = MagicMock(side_effect=side_effect_func)
        user_data_writer.run()
        titles_in_csv = []
        with open('users_1.csv', 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                titles_in_csv.append(row['age'])
        with open('users_2.csv', 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                titles_in_csv.append(row['age'])
        self.assertEqual(titles_in_csv, ["11", "22"])

    def test_api_fetch(self):
        user_fetcher = GetDataByUserId('user1')

        class MockResponse:
            def __init__(self, json, status_code):
                self.json_body = json
                self.status_code = status_code

            def json(self):
                return self.json_body

        def side_effect_func():
            json = {
                "gender": "M",
                "occupation": "student"
            }
            return MockResponse(json, 200)

        user_fetcher.get_user_from_api = MagicMock(side_effect=side_effect_func)
        row = user_fetcher.get_data()
        print(row)
        self.assertEqual("M", row['gender'])
        self.assertEqual("student", row["occupation"])


if __name__ == '__main__':
    unittest.main()
