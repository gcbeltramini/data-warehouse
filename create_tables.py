from db_utils import db_run
from sql_queries import create_table_queries, drop_table_queries


def main() -> None:
    """
    Connect to database, drop and create tables, and close the connection.
    """
    db_run(commands=drop_table_queries + create_table_queries)


if __name__ == "__main__":
    main()
