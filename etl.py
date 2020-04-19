from db_utils import db_run
from sql_queries import copy_table_queries, insert_table_queries


def main() -> None:
    """
    Connect to database, insert data into tables, and close the connection.
    """
    db_run(commands=copy_table_queries + insert_table_queries)


if __name__ == "__main__":
    main()
