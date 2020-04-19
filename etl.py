from db_utils import db_run
from sql_queries import COPY_TABLE_QUERIES, INSERT_TABLE_QUERIES


def main() -> None:
    """
    Connect to database, insert data into tables, and close the connection.
    """
    db_run(commands=COPY_TABLE_QUERIES + INSERT_TABLE_QUERIES)


if __name__ == "__main__":
    main()
