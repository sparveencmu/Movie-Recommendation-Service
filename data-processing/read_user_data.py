"""Read data from http://128.2.204.215:8080/user/<userid>
and save it in a csv file
"""

import csv
import json
import xml.etree.ElementTree as ET

from collections import defaultdict
from functools import lru_cache

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm


class UserDataCSVGenerator:
    user_descriptions = defaultdict(dict)
    outdata = []
    kafka_log_file_path = ''

    @lru_cache(10)
    def get_user_data_cached(self, user_id):
        user_data = GetDataByUserId(user_id).get_data()

        return user_data

    def populate_outdata(self):
        for _, data in self.user_descriptions.items():
            if len(data) == 0:
                continue
            self.outdata.append(data)

    def write_to_csv(self, outfile):
        with open(outfile, 'w', newline='') as new_csv_file:
            field_names_list = ['user_id', 'gender', 'occupation', 'age']
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
                user_id = row[0]
                user_info = self.get_user_data_cached(user_id)
                self.user_descriptions[user_id] = user_info

    def read_from_kafka_csv_unique(self):
        df = pd.read_csv(self.kafka_log_file_path, header=None)
        df = df.rename(columns={0: 'user_id', 1: 'movie_title', 2: 'year', 3: 'movie_id'})
        users = pd.Series(df['user_id'].unique())

        # Split data into 10 batches and save to csv after each batch
        batches = np.array_split(users, 10)
        for i in range(len(batches)):
            if i == 0:
                continue

            print('User batch ' + str(i) + ' ...')

            self.user_descriptions = defaultdict(dict)
            self.outdata = []

            batch = batches[i].reset_index(drop=True)
            for j in tqdm(range(len(batch))):
                user_id = str(batch[j])
                user_info = self.get_user_data_cached(user_id)
                self.user_descriptions[user_id] = user_info
            self.populate_outdata()
            self.write_to_csv('users_' + str(i) + '.csv')

            print('Saved!')

    def run(self):
        self.read_from_kafka_csv_unique()

    def __init__(self, kafka_log_file_path):
        self.kafka_log_file_path = kafka_log_file_path


from data_processing.constants import api_endpoint


class GetDataByUserId:
    api_endpoint = ''

    def get_user_from_api(self):
        return requests.get(f'{self.api}')

    def get_data(self):
        response = self.get_user_from_api()
        if response.status_code == 200:
            row = {}
            myjson = response.json()
            row['user_id'] = myjson['user_id'] if 'user_id' in myjson else ''
            row['gender'] = myjson['gender'] if 'gender' in myjson else ''
            row['occupation'] = myjson['occupation'] if 'occupation' in myjson else ''
            row['age'] = myjson['age'] if 'age' in myjson else ''
            return row
        else:
            print(f'{response.status_code} error with your request')
            return {}

    def formatted_print(self, obj):
        text = json.dumps(obj, sort_keys=True, indent=4)
        print(text)

    def __init__(self, user_id):

        self.api_endpoint = api_endpoint + '/user/' + user_id


if __name__ == '__main__':
    # api_call = GetDataByUserId(api_endpoint + "/user/39269")
    UserDataCSVGenerator('user_movie.csv')
