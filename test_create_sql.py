from pytest import mark

from create_sql import (get_drop_statement, get_create_statement,
                        get_copy_statement, get_insert_statement, Column)


@mark.parametrize('table, expected', [
    ('foo_table', 'DROP TABLE IF EXISTS foo_table CASCADE;'),
    ('bar123', 'DROP TABLE IF EXISTS bar123 CASCADE;'),
])
def test_get_drop_statement(table, expected):
    result = get_drop_statement(table)
    assert result == expected


@mark.parametrize('table_name, columns, primary_keys, expected', [
    ('table_name',
     [Column('c1', 't1', ''), Column('c2', 't2', '')],
     None,
     'CREATE TABLE IF NOT EXISTS table_name (\n  c1 t1,\n  c2 t2);'),
    ('my_table',
     [Column('c1', 't1', 'NOT NULL'), Column('c2', 't2', '')],
     ['c1'],
     'CREATE TABLE IF NOT EXISTS my_table (\n  c1 t1 NOT NULL,\n  c2 t2,\n'
     '  PRIMARY KEY (c1));'),
])
def test_get_create_statement(table_name, columns, primary_keys, expected):
    result = get_create_statement(table_name, columns, primary_keys)
    assert result == expected


@mark.parametrize(
    'table_name, data_source, iam_role, json_path, region, expected', [
        ('my_table', 's3://path/to/files', 'my-arn', None, 'my-region',
         "COPY my_table\nFROM 's3://path/to/files'\nIAM_ROLE 'my-arn'\n"
         "REGION 'my-region'\nFORMAT JSON AS 'auto'\nEMPTYASNULL\n"
         "BLANKSASNULL;"),
        ('another_table', 's3://bucket/files', 'arn:', 's3://bucket/file.json',
         'region-name',
         "COPY another_table\nFROM 's3://bucket/files'\nIAM_ROLE 'arn:'\n"
         "REGION 'region-name'\nFORMAT JSON AS 's3://bucket/file.json'\n"
         "EMPTYASNULL\nBLANKSASNULL;"),
    ])
def test_get_copy_statement(table_name, data_source, iam_role, json_path,
                            region, expected):
    result = get_copy_statement(table_name, data_source, iam_role, json_path,
                                region)
    assert result == expected


@mark.parametrize('table_name, table_info, query, expected', [
    ('my_table', [Column('foo', 'VARCHAR'), Column('bar', 'INT', 'NOT NULL')],
     'SELECT FROM',
     'INSERT INTO my_table (foo, bar)\nSELECT FROM;'),
    ('another_table', [Column('c1', 'anything'), Column('c2', 'my_type')],
     'SELECT <statement>',
     'INSERT INTO another_table (c1, c2)\nSELECT <statement>;'),
    ('another_table', [Column('c1', 'anything'),
                       Column('c2', 'my_type', 'IDENTITY(0, 1) NOT NULL')],
     'SELECT <statement>',
     'INSERT INTO another_table (c1)\nSELECT <statement>;'),
])
def test_get_insert_statement(table_name, table_info, query, expected):
    result = get_insert_statement(table_name, table_info, query)
    assert result == expected
