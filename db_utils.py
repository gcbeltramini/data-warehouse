import configparser
from typing import List

import psycopg2
from psycopg2.extensions import connection, cursor

CONFIG_FILE = 'dwh.cfg'

CONFIG = configparser.ConfigParser()
CONFIG.read(CONFIG_FILE)


def get_cluster_info() -> configparser.SectionProxy:
    """
    Read cluster configuration parameters.

    Returns
    -------
    configparser.SectionProxy
        Cluster information (database host address, name, ...).
    """
    return CONFIG['CLUSTER']


def trim_value(val: str) -> str:
    """
    Remove quotes (single or double) around string.

    Parameters
    ----------
    val : str
        Value to be trimmed.

    Returns
    -------
    str
    """
    return val.strip("'").strip('"')


def db_connect() -> (connection, cursor):
    """
    Create a new database connection and cursor.

    Returns
    -------
    psycopg2.extensions.connection, psycopg2.extensions.cursor
        Database connection and cursor.
    """
    cluster_info = get_cluster_info()
    conn = psycopg2.connect(host=trim_value(cluster_info['HOST']),
                            dbname=trim_value(cluster_info['DB_NAME']),
                            user=trim_value(cluster_info['DB_USER']),
                            password=trim_value(cluster_info['DB_PASSWORD']),
                            port=trim_value(cluster_info['DB_PORT']))
    cur = conn.cursor()
    return conn, cur


def execute_operation(cur: cursor,
                      conn: connection,
                      commands: List[str]) -> None:
    """
    Execute database operation.

    Parameters
    ----------
    cur : psycopg2.extensions.cursor
        Database cursor.
    conn : psycopg2.extensions.connection
        Database connection.
    commands : list[str]
        Commands or queries to be executed in the database.
    """
    for c in commands:
        cur.execute(c)
        conn.commit()


def db_run(commands: List[str]) -> None:
    """
    Connect to database, execute database operations and close the connection.

    Parameters
    ----------
    commands : list[str]
        Commands or queries to be executed in the database.
    """
    conn, cur = db_connect()
    execute_operation(cur, conn, commands=commands)
    conn.close()
