from collections import namedtuple
from typing import Optional, Sequence

from db_utils import CONFIG, trim_value

Column = namedtuple('Column', ('name', 'type', 'extra'))


def get_drop_statement(table: str) -> str:
    """
    Generate SQL DROP TABLE statement.

    Parameters
    ----------
    table : str
        Table name.

    Returns
    -------
    str
        DROP TABLE statement.

    References
    ----------
    - https://docs.aws.amazon.com/redshift/latest/dg/r_DROP_TABLE.html
    """
    return f'DROP TABLE IF EXISTS {table:s} CASCADE;'


def get_create_statement(table_name: str,
                         columns: Sequence[Column],
                         primary_keys: Optional[Sequence[str]] = None) -> str:
    """
    Generate SQL CREATE TABLE statement.

    Parameters
    ----------
    table_name : str
        Table name.
    columns : Sequence[Column]
        Collection of columns, each with name, type and extra parameters.
    primary_keys : Sequence[str], optional
        Column(s) used as primary key.

    Returns
    -------
    str
        CREATE TABLE statement.

    References
    ----------
    - https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_TABLE_NEW.html
    """
    create = f'CREATE TABLE IF NOT EXISTS {table_name:s}'
    separator = ',\n  '

    cols_list = [(c.name + ' ' + c.type +
                  (' ' * int(len(c.extra) > 1)) + c.extra)
                 for c in columns]
    cols = '  ' + separator.join(cols_list)

    if primary_keys is not None:
        pkey_cols = ', '.join(primary_keys)
        pkeys = f'{separator:s}PRIMARY KEY ({pkey_cols:s})'
    else:
        pkeys = ''

    return f'{create:s} (\n{cols:s}{pkeys:s});'


def get_copy_statement(table_name: str,
                       data_source: str,
                       iam_role: str = trim_value(CONFIG['IAM_ROLE']['ARN']),
                       json_path: Optional[str] = None,
                       region: str = 'us-west-2'):
    """
    Generate SQL COPY statement.

    Parameters
    ----------
    table_name : str
        Table name.
    data_source : str
        Data source, e.g., an AWS S3 prefix.
    iam_role : str, optional
        AWS IAM role with permission to access the data source.
    json_path : str, optional
        Specify the column name and order, mapping the source data fields to
        the target columns. Default behavior: field values are inserted into
        the target table's columns in the same order as the fields occur in the
        data files.
    region : str, optional
        AWS region.

    Returns
    -------
    str
        COPY statement.

    References
    ----------
    - https://docs.aws.amazon.com/redshift/latest/dg/r_COPY.html
    - https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-format.html#copy-json-jsonpaths
    """
    json_path = json_path if json_path is not None else 'auto'
    return (f"COPY {table_name:s}\n"
            f"FROM '{data_source:s}'\n"
            f"IAM_ROLE '{iam_role:s}'\n"
            f"REGION '{region:s}'\n"
            f"FORMAT JSON AS '{json_path:s}'"
            f"EMPTYASNULL"
            f"BLANKSASNULL;")


def get_insert_statement(table_name: str,
                         columns: Sequence[Column],
                         query: str) -> str:
    """
    Generate SQL INSERT command.

    Parameters
    ----------
    table_name : str
        Table name.
    columns : Sequence[Column]
        Collection of columns, each with name, type and extra parameters.
    query : str
        All rows produced by the query are inserted into the table. The column
        names don't have to match.

    Returns
    -------
    str
        INSERT statement.

    References
    ----------
    - https://docs.aws.amazon.com/redshift/latest/dg/r_INSERT_30.html
    """
    return ('INSERT INTO {table:s} ({columns:s})\n{query:s};'
            ''.format(table=table_name,
                      columns=', '.join([c.name for c in columns]),
                      query=query.strip().rstrip(';')))
