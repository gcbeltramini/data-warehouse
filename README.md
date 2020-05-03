# ETL - Data Warehouse

## Introduction

A music streaming startup, `Sparkify`, has grown their user base and song database and want to move
their processes and data onto the cloud. Their data resides in S3, in a directory of JSON logs on
user activity on the app, as well as a directory with JSON metadata on the songs in their app.

The goal is to build an ETL pipeline that:

1. extracts their data from S3;
1. stages them in Redshift; and
1. transforms the data into a set of dimensional tables for their analytics team to continue finding
insights in what songs their users are listening to.

## Project datasets

There are two datasets that reside in S3:

- Song data: `s3://udacity-dend/song_data`
- Log data: `s3://udacity-dend/log_data`

Log data json path: `s3://udacity-dend/log_json_path.json`.

### Song dataset

- Subset of real data from the [Million Song Dataset](https://labrosa.ee.columbia.edu/millionsong/).
- Each file is in JSON format and contains metadata about a song and the artist of that song.
- The files are partitioned by the first three letters of each song's track ID. For example, here
are filepaths to two files in this dataset:
  - `song_data/A/B/C/TRABCEI128F424C983.json`
  - `song_data/A/A/B/TRAABJL12903CDCF1A.json`
- Example of the song file `song_data/A/A/B/TRAABCL128F4286650.json` (it's possible to view it in
the web browser: <http://udacity-dend.s3.amazonaws.com/song_data/A/A/B/TRAABCL128F4286650.json>):

  ```json
  {
    "artist_id": "ARC43071187B990240",
    "artist_latitude": null,
    "artist_location": "Wisner, LA",
    "artist_longitude": null,
    "artist_name": "Wayne Watson",
    "duration": 245.21098,
    "num_songs": 1,
    "song_id": "SOKEJEJ12A8C13E0D0",
    "title": "The Urgency (LP Version)",
    "year": 0
  }
  ```

### Log dataset

- Log files in JSON format generated by [this event simulator](https://github.com/Interana/eventsim)
based on the songs in the dataset above. These simulate app activity logs from an imaginary music
streaming app based on configuration settings.
- The log files in the dataset are partitioned by year and month. For example, here are filepaths to
two files in this dataset:
  - `log_data/2018/11/2018-11-12-events.json`
  - `log_data/2018/11/2018-11-13-events.json`
- Example of two lines in log file `log_data/2018/11/2018-11-01-events.json (it's possible to view
it in the web browser: <http://udacity-dend.s3.amazonaws.com/log_data/2018/11/2018-11-01-events.json>):

  ```text
  {"artist":null,"auth":"Logged In","firstName":"Kaylee","gender":"F","itemInSession":2,"lastName":"Summers","length":null,"level":"free","location":"Phoenix-Mesa-Scottsdale, AZ","method":"GET","page":"Upgrade","registration":1540344794796.0,"sessionId":139,"song":null,"status":200,"ts":1541106132796,"userAgent":"\"Mozilla\/5.0 (Windows NT 6.1; WOW64) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/35.0.1916.153 Safari\/537.36\"","userId":"8"}
  {"artist":"Mr Oizo","auth":"Logged In","firstName":"Kaylee","gender":"F","itemInSession":3,"lastName":"Summers","length":144.03873,"level":"free","location":"Phoenix-Mesa-Scottsdale, AZ","method":"PUT","page":"NextSong","registration":1540344794796.0,"sessionId":139,"song":"Flat 55","status":200,"ts":1541106352796,"userAgent":"\"Mozilla\/5.0 (Windows NT 6.1; WOW64) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/35.0.1916.153 Safari\/537.36\"","userId":"8"}
  ```

## Schema for song play analysis

The goal is to create a star schema optimized for queries on song play analysis using the song and
event datasets. This includes the following tables.

### Staging tables

They are temporary tables to stage the data before loading them into the star schema tables. They
shouldn't be used for analytical purposes.

### Fact table

1. **songplays**: records in event data associated with song plays, i.e., records with page
`NextSong`
   - `songplay_id`, `start_time`, `user_id`, `level`, `song_id`, `artist_id`, `session_id`,
   `location`, `user_agent`

### Dimension tables

1. **users**: users in the app
   - `user_id`, `first_name`, `last_name`, `gender`, `level`
1. **songs**: songs in music database
   - `song_id`, `title`, `artist_id`, `year`, `duration`
1. **artists**: artists in music database
   - `artist_id`, `name`, `location`, `latitude`, `longitude`
1. **time**: timestamps of records in **songplays** broken down into specific units
   - `start_time`, `hour`, `day`, `week`, `month`, `year`, `weekday`

## Project structure

```text
├── README.md: this file
├── create_sql.py: contains functions to create all SQL statements (DROP TABLE, CREATE TABLE, ...)
├── create_tables.py: script that drops and creates all tables (staging tables, and fact and
                      dimension tables) on Redshift
├── db_utils.py: auxiliary functions related to the database (read config file, connect to the
                 database, ...)
├── docs
│   ├── aws_redshift.md: instructions to start the Redshift cluster
│   └── tests_debug.md: instructions to debug and run tests
├── dwh.cfg: configuration information (cluster and data source)
├── etl.py: script that copies data from S3 into staging tables on Redshift and processes that data
            into analytics tables (fact and dimension tables) on Redshift
├── requirements
│   ├── requirements.txt: project requirements (Python libraries)
│   ├── requirements_dev.txt: additional requirements used for development
│   └── requirements_test.txt: additional requirements to run unit tests
├── sql_queries.py: SQL statements (DROP TABLE, CREATE TABLE, COPY, INSERT)
├── test_create_sql.py: unit tests for functions in create_sql.py
├── test_data_sanity_checks.ipynb: jupyter notebook for data sanity checks
├── test_db_utils.py: unit tests for functions in db_utils.py
└── test_sql_queries_debug.ipynb: jupyter notebook to view the queries generated programmatically
```

## Run the ETL

1. [Create an AWS Redshift cluster](docs/aws_redshift.md).
1. Add Redshift and IAM role to `dwh.cfg`.
1. Run the Python scripts:

   ```bash
   conda create -yn etl-env python=3.7 --file requirements/requirements.txt
   conda activate etl-env
   python create_tables.py
   python etl.py
   conda deactivate
   ```

1. [Run Python unit tests, queries, debug problems](docs/tests_debug.md).
1. When finished, delete the Redshift cluster and remove the Python environment:
`conda env remove -n etl-env`.
