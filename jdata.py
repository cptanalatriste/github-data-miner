"""
Module for accessing JIRA database information.
"""

import dbutils

DATABASE_FILE = "C:\Users\Carlos G. Gavidia\OneDrive\phd2\jira_db\issue_repository.db"


def get_issue_by_key(key):
    issue_sql = "SELECT * FROM Issue WHERE key=?"
    return dbutils.execute_query(issue_sql, (key,), DATABASE_FILE)
