from create_sql import (get_drop_statement, get_create_statement,
                        get_copy_statement, get_insert_statement, Column)
from db_utils import trim_value, CONFIG

# Get the latest values of the user from table "staging_events":
query_users = '''
SELECT
  e.userId AS user_id,
  e.firstName AS first_name,
  e.lastName AS last_name,
  e.gender AS gender,
  e.level AS level
FROM staging_events AS e
INNER JOIN (SELECT userId AS user_id, MAX(ts) AS latest_ts
            FROM staging_events
            WHERE userId IS NOT NULL
            GROUP BY 1) AS last_update
            ON last_update.user_id = e.userId
            AND last_update.latest_ts = e.ts'''

# If there is a conflict in column "song_id" of table "staging_songs", get the
# largest value of the attributes (arbitrary decision to choose one line per
# song):
query_songs = '''
SELECT
  song_id,
  MAX(title) AS title,
  MAX(artist_id) AS artist_id,
  MAX(year) AS year,
  MAX(duration) AS duration
FROM staging_songs
WHERE song_id IS NOT NULL
GROUP BY song_id'''

# If there is a conflict in column "artist_id" of table "staging_songs", get
# the largest value of the attributes (arbitrary decision to choose one line
# per artist):
query_artists = '''
SELECT
  artist_id,
  MIN(artist_name) AS name,
  MAX(artist_location) AS location,
  MAX(artist_latitude) AS latitude,
  MAX(artist_longitude) AS longitude
FROM staging_songs
WHERE artist_id IS NOT NULL
GROUP BY artist_id'''

# Select only distinct values of the timestamp in table "staging_events" and
# convert Unix timestamp into timestamp, using the trick described here
# https://docs.aws.amazon.com/redshift/latest/dg/r_Dateparts_for_datetime_functions.html.
# Reference for the time parts: https://docs.aws.amazon.com/redshift/latest/dg/r_Dateparts_for_datetime_functions.html.
query_time = '''
SELECT
  e.t AS start_time,
  EXTRACT(HOUR FROM e.t) AS hour,
  EXTRACT(DAY FROM e.t) AS day,
  EXTRACT(WEEK FROM e.t) AS week,
  EXTRACT(MONTH FROM e.t) AS month,
  EXTRACT(YEAR FROM e.t) AS year,
  EXTRACT(WEEKDAY FROM e.t) AS weekday
FROM (SELECT DISTINCT TIMESTAMP 'EPOCH' + ts/1000 * INTERVAL '1 SECOND' AS t
      FROM staging_events
      WHERE ts IS NOT NULL AND page = 'NextSong') AS e'''

# Get all values from the staging tables. Since there is no song ID nor artist
# ID in table "staging_events", we need to join both tables using song title,
# artist name and song duration, which should uniquely describe a song. And
# this is the best we can do, because there is no other information about the
# songs in "staging_events".
query_songplays = '''
SELECT
  TIMESTAMP 'EPOCH' + e.ts/1000 * INTERVAL '1 SECOND' AS start_time,
  e.userId AS user_id,
  e.level,
  s.song_id,
  s.artist_id,
  e.sessionId AS session_id,
  e.location,
  e.userAgent AS user_agent
FROM staging_events AS e
INNER JOIN staging_songs AS s
   ON (s.title = e.song AND s.artist_name = e.artist)
WHERE e.page = 'NextSong'
  AND e.userId IS NOT NULL
  AND e.ts IS NOT NULL'''

# Data types:
# https://docs.aws.amazon.com/redshift/latest/dg/c_Supported_data_types.html
tables = ({'name': 'staging_events',
           'columns': [
               Column('artist', 'VARCHAR'),
               Column('auth', 'VARCHAR'),
               Column('firstName', 'VARCHAR'),
               Column('gender', 'CHAR(1)'),  # "M", "F"
               Column('itemInSession', 'SMALLINT'),
               Column('lastName', 'VARCHAR'),
               Column('length', 'DOUBLE PRECISION'),
               Column('level', 'CHAR(4)'),  # "free", "paid"
               Column('location', 'VARCHAR'),
               Column('method', 'VARCHAR(6)'),
               # "POST", "GET", "PUT", "PATCH", "DELETE"
               Column('page', 'VARCHAR'),
               Column('registration', 'INT8'),
               Column('sessionId', 'INT4'),
               Column('song', 'VARCHAR'),
               Column('status', 'INT2'),  # 1xx-5xx
               Column('ts', 'INT8'),
               Column('userAgent', 'VARCHAR'),
               Column('userId', 'INT4'),  # comes as text
           ],
           'source': trim_value(CONFIG['S3']['LOG_DATA']),
           'json_path': trim_value(CONFIG['S3']['LOG_JSONPATH'])},
          {'name': 'staging_songs',
           'columns': [
               Column('num_songs', 'INT2'),
               Column('artist_id', 'VARCHAR(64)'),
               Column('artist_latitude', 'DOUBLE PRECISION'),
               Column('artist_longitude', 'DOUBLE PRECISION'),
               Column('artist_location', 'VARCHAR'),
               Column('artist_name', 'VARCHAR'),
               Column('song_id', 'VARCHAR(64)'),
               Column('title', 'VARCHAR'),
               Column('duration', 'DOUBLE PRECISION'),
               Column('year', 'INT2'),
           ],
           'source': trim_value(CONFIG['S3']['SONG_DATA'])},
          {'name': 'users',
           'columns': [
               Column('user_id', 'INT4'),
               Column('first_name', 'VARCHAR'),
               Column('last_name', 'VARCHAR'),
               Column('gender', 'CHAR(1)'),
               Column('level', 'CHAR(4)'),
           ],
           'pkeys': ['user_id'],
           'query': query_users},
          {'name': 'songs',
           'columns': [
               Column('song_id', 'VARCHAR(64)'),
               Column('title', 'VARCHAR'),
               Column('artist_id', 'VARCHAR(64)'),
               Column('year', 'INT2'),
               Column('duration', 'DOUBLE PRECISION'),
           ],
           'pkeys': ['song_id'],
           'query': query_songs},
          {'name': 'artists',
           'columns': [
               Column('artist_id', 'VARCHAR(64)'),
               Column('name', 'VARCHAR'),
               Column('location', 'VARCHAR'),
               Column('latitude', 'DOUBLE PRECISION'),
               Column('longitude', 'DOUBLE PRECISION'),
           ],
           'pkeys': ['artist_id'],
           'query': query_artists},
          {'name': 'time',
           'columns': [
               Column('start_time', 'TIMESTAMP'),
               Column('hour', 'INT2', 'NOT NULL'),
               Column('day', 'INT2', 'NOT NULL'),
               Column('week', 'INT2', 'NOT NULL'),
               Column('month', 'INT2', 'NOT NULL'),
               Column('year', 'INT2', 'NOT NULL'),
               Column('weekday', 'INT2', 'NOT NULL'),
           ],
           'pkeys': ['start_time'],
           'query': query_time},
          {'name': 'songplays',
           'columns': [
               Column('songplay_id', 'INT4', 'IDENTITY(0, 1)'),
               Column('start_time', 'TIMESTAMP', 'NOT NULL'),
               Column('user_id', 'INT4', 'NOT NULL'),
               Column('level', 'CHAR(4)'),
               Column('song_id', 'VARCHAR(64)'),
               Column('artist_id', 'VARCHAR(64)'),
               Column('session_id', 'INT4'),
               Column('location', 'VARCHAR'),
               Column('user_agent', 'VARCHAR'),
           ],
           'pkeys': ['songplay_id'],
           'query': query_songplays},
          )

DROP_TABLE_QUERIES = [get_drop_statement(t['name']) for t in tables]

CREATE_TABLE_QUERIES = [get_create_statement(t['name'],
                                             t['columns'],
                                             t.get('pkeys'))
                        for t in tables]

COPY_TABLE_QUERIES = [get_copy_statement(t['name'],
                                         data_source=t['source'],
                                         json_path=t.get('json_path'))
                      for t in tables if t['name'].startswith('staging_')]

INSERT_TABLE_QUERIES = [get_insert_statement(t['name'],
                                             t['columns'],
                                             t['query'])
                        for t in tables
                        if not t['name'].startswith('staging_')]
