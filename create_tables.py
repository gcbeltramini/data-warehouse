import configparser
from typing import List

import psycopg2
from psycopg2.extensions import connection, cursor

from sql_queries import create_table_queries, drop_table_queries


def execute_command(cur: cursor,
                    conn: connection,
                    commands: List[str]) -> None:
    """
    Execute commands in database.

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


def main() -> None:
    """
    Connect to database (parameters in file `dwh.cfg`), drop tables, create
    tables and close the connection.
    """

    # Read cluster configuration parameters
    config = configparser.ConfigParser()
    config.read('dwh.cfg')
    cluster_info = config['CLUSTER']

    # Create a new database connection and cursor
    conn = psycopg2.connect(host=cluster_info['HOST'],
                            dbname=cluster_info['DB_NAME'],
                            user=cluster_info['DB_USER'],
                            password=cluster_info['DB_PASSWORD'],
                            port=cluster_info['DB_PORT'])
    cur = conn.cursor()

    # Drop and create all tables
    execute_command(cur, conn, commands=drop_table_queries)
    execute_command(cur, conn, commands=create_table_queries)

    # Close the connection
    conn.close()


if __name__ == "__main__":
    main()
