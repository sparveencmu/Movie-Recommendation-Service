import csv
from collections import defaultdict

from tqdm import tqdm


class StreamData:
    def __init__(self, user, movie, time):
        self.user = user
        self.movie = movie
        self.time = time


def extract_movie_name_from_url(url, include_minute=False):
    if '/rate/' in url:
        s = url.split('/')
        movieidwithRating = s[2]
        movieidRating = movieidwithRating.split('=')
        movieid = movieidRating[0]
        rating = movieidRating[1]
        movienametemp = movieid.split('+')
        year = movienametemp[-1]
        movie_name = ' '.join(movienametemp[:-1])
        return (movie_name, movieid, rating, year)
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


def get_user_from_row(row):
    return row[1]


def get_movie_from_row(row):
    return extract_movie_name_from_url(row[2])


def get_time_from_row(row):
    return row[0]


def data_row_to_class(row):
    return StreamData(get_user_from_row(row), get_movie_from_row(row), get_time_from_row(row))


class UserMovieCSVGenerator:
    limit = -1
    kafka_log_csv_path = ''
    movies = set()
    user_watch_movies = defaultdict(set)
    user_rates_movies = defaultdict(set)
    user_watch_movies_minute = defaultdict(dict)
    users = set()
    start_row = 0
    end_row = -1
    file_name = 'user_movie'

    def write_movies_to_csv(self):
        with open('movies.csv', 'w', newline='') as csvfile:
            for movie_name, movieid, year in self.movies:
                csvfile.write(movie_name + ',' + year)
                csvfile.write('\n')

    def write_user_movie_to_csv(self):
        with open(self.file_name, 'w', newline='') as csvfile:
            field_names_list = ['user_id', 'movie_name', 'year', 'movie_id']
            csv_writer = csv.DictWriter(
                csvfile,
                fieldnames=field_names_list,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
            )
            csv_writer.writeheader()

            row_count = 0
            loop_flag = True
            outdata = []
            print('Writing CSV ...')
            for user, movies in tqdm(self.user_watch_movies.items()):
                if not loop_flag:
                    break
                for movie_name, movieid, year in movies:
                    d = {}
                    d['user_id'] = user
                    d['movie_id'] = movieid
                    d['year'] = year
                    d['movie_name'] = movie_name
                    outdata.append(d)
                    if self.limit != -1 and row_count > self.limit:
                        loop_flag = False
                        break
                    row_count += 1
            csv_writer.writerows(outdata)

    def write_user_movie_with_minute_to_csv(self):
        with open(self.file_name, 'w', newline='') as csvfile:
            field_names_list = ['user_id', 'movie_name', 'year', 'movie_id', 'minute']
            csv_writer = csv.DictWriter(
                csvfile,
                fieldnames=field_names_list,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
            )
            csv_writer.writeheader()

            row_count = 0
            loop_flag = True
            outdata = []
            print('Writing CSV ...')
            for user, movies in tqdm(self.user_watch_movies_minute.items()):
                if not loop_flag:
                    break
                for (movie_name, movieid, year), minute in movies.items():
                    d = {}
                    d['user_id'] = user
                    d['movie_id'] = movieid
                    d['year'] = year
                    d['movie_name'] = movie_name
                    d['minute'] = minute
                    outdata.append(d)
                    if self.limit != -1 and row_count > self.limit:
                        loop_flag = False
                        break
                    row_count += 1
            csv_writer.writerows(outdata)

    def write_user_rating_to_csv(self):
        with open(self.file_name_2, 'w', newline='') as csvfile:
            field_names_list = ['user_id', 'movie_name', 'year', 'movie_id', 'rating']
            csv_writer = csv.DictWriter(
                csvfile,
                fieldnames=field_names_list,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
            )
            csv_writer.writeheader()

            row_count = 0
            loop_flag = True
            outdata = []
            for user, movies in self.user_rates_movies.items():
                if not loop_flag:
                    break
                for movie_name, movieid, rating, year in movies:
                    d = {}
                    d['user_id'] = user
                    d['movie_id'] = movieid
                    d['year'] = year
                    d['movie_name'] = movie_name
                    d['rating'] = rating
                    outdata.append(d)
                    if self.limit != -1 and row_count > self.limit:
                        loop_flag = False
                        break
                    row_count += 1
            csv_writer.writerows(outdata)

    def read_from_log_csv(self, include_minute=False):
        line_number = 0
        with open(self.kafka_log_csv_path, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            print('Reading Kafka log file ...')
            for row in tqdm(spamreader):
                line_number += 1
                if line_number < self.start:
                    continue
                if line_number > self.end and self.end != -1:
                    break

                if len(data_row_to_class(row).movie) == 0:
                    # print('need to handle recommened requests')
                    pass
                elif len(data_row_to_class(row).movie) == 4:
                    user_rates_movies = data_row_to_class(row)
                    self.user_rates_movies[user_rates_movies.user].add(user_rates_movies.movie)
                else:
                    if not include_minute:
                        user_watches_movie = data_row_to_class(row)
                        self.users.add(user_watches_movie.user)
                        self.movies.add(user_watches_movie.movie)
                        self.user_watch_movies[user_watches_movie.user].add(
                            user_watches_movie.movie
                        )
                    else:
                        # save minute
                        movie, minute = extract_movie_name_from_url(row[2], True)
                        user = get_user_from_row(row)
                        self.user_watch_movies_minute[user][movie] = minute

    def __init__(self, kafka_log_file_path, limit=-1, start=0, end=-1):
        self.kafka_log_csv_path = kafka_log_file_path
        self.limit = limit
        self.start = start
        self.end = end
        self.file_name = 'user_movie_' + str(start) + '_' + str(end) + '.csv'
        self.file_name_2 = 'user_rate_movie_' + str(start) + '_' + str(end) + '.csv'


# new = UserMovieCSVGenerator('kafka_log.csv', 2000000, 0, 2000000)
# new.read_from_log_csv()
# new.write_user_rating_to_csv()
# new.write_user_movie_to_csv()
