"""
Module for accessing JIRA database information.
"""

import dbutils

DATABASE_FILE = "C:\Users\Carlos G. Gavidia\OneDrive\phd2\jira_db\issue_repository.db"


def get_issue_by_key(key):
    issue_sql = "SELECT * FROM Issue WHERE key=?"
    return dbutils.execute_query(issue_sql, (key,), DATABASE_FILE)


def get_affected_versions(issue_id):
    version_sql = "SELECT v.* FROM Version v, Issue i ,VersionPerIssue vi " \
                  "WHERE i.id = vi.issueId AND vi.versionId = v.id AND i.id =?"

    return dbutils.execute_query(version_sql, (issue_id,), DATABASE_FILE)


def get_project_issues(project_id):
    issue_sql = "SELECT * FROM Issue WHERE projectId=?"
    return dbutils.execute_query(issue_sql, (project_id,), DATABASE_FILE)
