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
