# Movie-Recommendation-Service

group-project-f22-popcorntime created by GitHub Classroom

Overview: Movie Recommendations

In this project, we will implement, evaluate, operate, monitor, and evolve a recommendation service for a scenario of a movie streaming service.
Data:
1 million customers (10 lakhs)
27,000 movies

## Installation

clone:

```
$ git clone https://github.com/cmu-seai/group-project-f22-popcorntime.git
# Open the terminal and make sure you are in the folder "group-project-f22-popcorntime"

```

create & activate virtual env then install dependency:

with venv/virtualenv + pip:

```
$ python -m venv env_kafka  # use `virtualenv env` for Python2, use `python3 ...` for Python3 on Linux & macOS
$ source env_kafka/bin/activate  # use `env\Scripts\activate` on Windows
$ pip install -r requirements.txt

```

Prerequisites

```
* Make sure .env is added in .gitignore and we don't check-in the .env file in the github
```
CD to the repo root directory and setup the git hooks in your local repo:
```
pre-commit install
```

Remove virtual environment :

```
Deactivate
rm -r env_kafka/
```

## Generate Data

```
python3 data_processing/main.py
```

To change the size of input, change the second argument on `data_processing/main.py` line 6

run:

```
python main.py
```

Test account:

- add details if any

## Generate Test

We are using `unittest` and are storing all of the tests in the (./test) directory.

For all test files, we need to name the files `test-[file_name].py`

We need to install the following packages:

```
pip3 install unittest-xml-reporting
pip3 instal coverage
```

Then we can generate xml report by 
```
python -m xmlrunner discover -o ./test-report/junit-reports
```
The reports will be located in `./test-report/junit-reports`

We can generate the coverage report by
```
python3 -m coverage run -m unittest
python3 -m coverage report
python3 -m coverage xml 
```
The report will be in `./coverage.xml`

## Recommendation

To get the data needed for inference, download `data_for_inference.zip` from the shared drive in `Data` folder. Unzip the file and put the data into `data` directory right underneath the project root folder. The folder structure should look like this:
```
group-poject-f22-popcorntime
├── apiendpoint
├── data
│   ├── als.npz
│   ├── idx_to_mid.1500k.pkl
│   ├── movies_top_100k.csv
│   ├── uid_to_idx_1500k.pkl
│   └── X_1500k.npz
├── data_processing
├── ...
├── recommend.py
└── ...
```

Function for getting movie recommendation is in `recommendation.py`.
```
get_recommendations(54948)  # returns movie ids for user 54948
```
