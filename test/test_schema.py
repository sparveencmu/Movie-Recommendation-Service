import csv
import sys

from data_processing.csvvalidator import CSVValidator, number_range_inclusive, write_problems

field_names_user_movie = ('user_id', 'movie_name', 'year', 'movie_id')

field_names_user_movie_rating = ('user_id', 'movie_name', 'year', 'movie_id', 'rating')


validator = CSVValidator(field_names_user_movie)
validator_with_rate = CSVValidator(field_names_user_movie_rating)

# basic header and record length checks
validator.add_header_check('EX1', 'bad header')
validator.add_record_length_check('EX2', 'unexpected record length')

# some simple value checks
validator.add_value_check('user_id', int, 'EX3', 'user id must be an integer')
validator.add_value_check('movie_name', str, 'EX4', 'movie name must be an integer')
validator.add_value_check('year', int, 'EX5', 'year must be an integer')
validator.add_value_check('movie_id', str, 'EX6', 'movie id must be an string')


# basic header and record length checks for validator_with_minutes
validator_with_rate.add_header_check('EX1', 'bad header')
validator_with_rate.add_record_length_check('EX2', 'unexpected record length')

# some simple value checks
validator_with_rate.add_value_check('user_id', int, 'EX3', 'user id must be an integer')
validator_with_rate.add_value_check('movie_name', str, 'EX4', 'movie name must be an integer')
validator_with_rate.add_value_check('year', int, 'EX5', 'year must be an integer')
validator_with_rate.add_value_check('movie_id', str, 'EX6', 'movie id must be an string')
validator_with_rate.add_value_check(
    'rating', number_range_inclusive(1, 5, int), 'EX7', 'rating must be an int'
)


# validate the data and write problems to stdout
data = csv.reader('./data/user_movie.csv', delimiter=',')
problems = validator.validate(data)
write_problems(problems, sys.stdout)

# validate the data and write problems to stdout
data_minutes = csv.reader('./data/user_rate_movie.csv', delimiter=',')
problems_minutes = validator_with_rate.validate(data_minutes)
write_problems(problems_minutes, sys.stdout)
