from data_processing.clean_input_stream import UserMovieCSVGenerator
from data_processing.read_movie_data import MovieDataCSVGenerator
from data_processing.read_user_data import UserDataCSVGenerator

# create user <-> movie_id csv
# limit controls the number of lines written to csv (-1 if you want to use start/end instead)
# start/end controls the lines of log being read/written to the csv
log_generator = UserMovieCSVGenerator('./data/kafka_log_7m.csv', start=0, end=1000000)
log_generator.read_from_log_csv()
log_generator.write_user_movie_to_csv()
log_generator.write_user_rating_to_csv()

# log_generator.read_from_log_csv(include_minute=True)
# log_generator.write_user_movie_with_minute_to_csv()

# # create movie_id <-> movie data csv
# print('Get Movie data from API ...')
# movie_data_generator = MovieDataCSVGenerator('../data/user_movie_1500k.csv')
# movie_data_generator.run()
# # create user_id <-> user data csv
# print('Get User data from API ...')
# user_data_generator = UserDataCSVGenerator('../data/user_movie_1500k.csv')
# user_data_generator.run()