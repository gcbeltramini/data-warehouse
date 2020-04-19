from db_utils import db_run
from sql_queries import CREATE_TABLE_QUERIES, DROP_TABLE_QUERIES


def main() -> None:
    """
    Connect to database, drop and create tables, and close the connection.
    """
    db_run(commands=DROP_TABLE_QUERIES + CREATE_TABLE_QUERIES)


if __name__ == "__main__":
    main()
