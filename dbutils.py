"""
Module that contain utilities for dealing with sqlite databases..
"""

import sqlite3


def execute_query(sql_query, parameters, db_file):
    """
    Executes a query on the database
    :param sql_query: SQL Query
    :param parameters: Parameters for the query
    :param db_file: File of the SQLite database
    :return: Query results as a List
    """
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute(sql_query, parameters)
    results = cursor.fetchall()
    connection.close()

    return results


def create_schema(table_list, db_file):
    """
    Creates the SQLite tables
    :return: None
    """
    print "Starting schema creation ..."
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    for table_ddl in table_list:
        cursor.execute(table_ddl)

    connection.commit()
    connection.close()

    print "Schema creation finished"


def load_list(sql_insert, row_list, db_file):
    """
    Inserts a list of items into the database.
    :param sql_insert: SQL for inserting a row.
    :param row_list: List containing tuples with tag information.
    :return: None.
    """
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    for row in row_list:
        cursor.execute(sql_insert, row)

    connection.commit()
    connection.close()
