# Kafka Demo for Machine Learning in Production (17-445/17-645/17-745)
from apiendpoint.main import get_recommendations


### Connect to Kafka Broker Server

"""
ssh -o ServerAliveInterval=60 -L 9092:localhost:9092 tunnel@128.2.204.215 -NTf

pass: seaitunnel

To kill connection at port:

lsof -ti:9092 | xargs kill -9

python -m pip install kafka-python
"""

from os import path
import sys, os
from datetime import datetime
from json import dumps, loads
from time import sleep
from random import randint
import numpy as np
# ssh -o ServerAliveInterval=60 -L 9092:localhost:9092 tunnel@128.2.204.215 -NTf
from kafka import KafkaConsumer, KafkaProducer

# team no 1
topic = 'movielog1'

# we don't need to write to the stream

"""
# Create a producer to write data to kafka
# Ref: https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html
# producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
#                         value_serializer=lambda x: dumps(x).encode('utf-8'),
#                         )
# cities = ['Pittsburgh','New York','London','Bangalore','Shanghai','Tokyo','Munich']
# # Write data via the producer
# print("Writing to Kafka Broker")
# for i in range(10):
#     data = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")},{cities[randint(0,len(cities)-1)]},{randint(18, 32)}ºC'
#     print(f"Writing: {data}")
#     producer.send(topic=topic, value=data)
#     sleep(1)
"""

### Consumer Mode -> Reads Data from Broker
# Ref: https://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html
consumer = KafkaConsumer(
    topic,
    bootstrap_servers=['localhost:9092'],
    # Read from the start of the topic; Default is latest
    auto_offset_reset='earliest',
    # auto_offset_reset='latest',
    # group_id='team13',
    # Commit that an offset has been read
    enable_auto_commit=True,
    # How often to tell Kafka, an offset has been read
    # auto_commit_interval_ms=1000
)

print('Reading Kafka Broker')

def extract_movie_name_from_url(url, include_minute=False):
    if '/rate/' in url:
        comma_split = url.split(",")
        user_id = comma_split[1]
        s = url.split('/')
        movieidwithRating = s[2]
        movieidRating = movieidwithRating.split('=')
        movieid = movieidRating[0]
        rating = int(movieidRating[1])
        movienametemp = movieid.split('+')
        year = movienametemp[-1]
        movie_name = ' '.join(movienametemp[:-1])
        return (movie_name, movieid, rating, year, user_id, movienametemp)
    elif 'recommendation request' in url:
        # print('request')
        return ()
    else:
        u = url.split('/')
        movieid = u[3]

        s = movieid.split('+')
        year = s[-1]
        movie_name = ' '.join(s[:-1])

        if include_minute:
            minute = u[4].split('.')[0]
            return (movie_name, movieid, year), minute

        return (movie_name, movieid, year)

with open('telemetry.txt', 'w') as f:
    f.write('0 0')

total_score = 0
rating_cnt = 0
for message in consumer:
    message = message.value.decode('utf-8')
    # Default message.value type is bytes!
    # print(loads(message))
    # os.system(f"echo {message} >> kafka_log1.csv")
    extracted = extract_movie_name_from_url(message)
    if len(extracted) == 6:
        user_id = extracted[4]
        movie_name = extracted[5]
        rating = extracted[2]
        year = extracted[3]
        user_recommendations = get_recommendations(user_id)
        # print(movie_name)
        m = "+".join(movie_name)
        movie_in_recommendation = m in user_recommendations.split(",")

        score = (3 - rating)

        if movie_in_recommendation:
            score *= -1
        total_score = 0
        rating_cnt = 0
        with open('telemetry.txt', 'r') as f:
            for line in f:
                total_score, rating_cnt = line.split(" ")
                total_score = int(total_score)
                rating_cnt = int(rating_cnt)

        total_score = int(total_score) + score
        rating_cnt = int(rating_cnt) + 1
        with open('telemetry.txt', 'w') as f:
            f.write(str(total_score) + " " + str(rating_cnt))
        # print(os.environ.get("TOTAL_SCORE"), os.environ.get("RATING_CNT"))

#