"""
Module for storing the relationships between JIRA issues and GitHub commits.
"""

import dbutils

DATABASE_FILE = "jira_github.sqlite"

COMMITS_DDL = "CREATE TABLE issue_commit " \
              "(project_id TEXT, issue_key TEXT, commit_sha TEXT," \
              " PRIMARY KEY(project_id, commit_sha, issue_key))"
TAGS_DDL = "CREATE TABLE commit_tag (project_id TEXT, commit_sha TEXT, tag_name TEXT," \
           " PRIMARY KEY(project_id, commit_sha, tag_name))"
STATS_DDL = "CREATE TABLE commit_stats " \
            "(project_id TEXT, commit_sha TEXT," \
            " deletions INTEGER, lines INTEGER, insertions INTEGER, files INTEGER," \
            " PRIMARY KEY(project_id, commit_sha))"


def create_schema():
    """
    Creates the tables for storing the Github-JIRA information.
    :return: None
    """
    dbutils.create_schema([STATS_DDL], DATABASE_FILE)


def get_commits_by_issue(project_id, key):
    commit_sql = "SELECT * FROM issue_commit WHERE project_id=? AND issue_key=?"
    return dbutils.execute_query(commit_sql, (project_id, key), DATABASE_FILE)


def get_tags_by_commit_sha(project_id, commit_sha):
    tag_sql = "SELECT * FROM commit_tag WHERE project_id=? AND commit_sha=?"
    return dbutils.execute_query(tag_sql, (project_id, commit_sha), DATABASE_FILE)


def insert_commits_per_issue(db_records):
    insert_commit = "INSERT INTO issue_commit VALUES (?, ?, ?)"
    dbutils.load_list(insert_commit, db_records, DATABASE_FILE)


def insert_stats_per_commit(db_records):
    """
    Inserts a list of commit statistics into the database.
    :param db_records: List, containing tuples for commit stats.
    :return: None.
    """
    insert_commit = "INSERT INTO commit_stats VALUES (?, ?, ?, ?, ?, ?)"
    dbutils.load_list(insert_commit, db_records, DATABASE_FILE)


def get_commits_per_project(project_id):
    """
    Returns the commit sha's for an specific JIRA project.
    :param project_id: JIRA's project identifier.
    :return: List of commit SHA's
    """
    commits_sql = "SELECT DISTINCT commit_sha FROM issue_commit WHERE project_id=?"
    commits = dbutils.execute_query(commits_sql, (project_id,), DATABASE_FILE)
    return commits


def insert_tags_per_commit(db_records):
    insert_tag = "INSERT INTO commit_tag VALUES (?, ?, ?)"
    dbutils.load_list(insert_tag, db_records, DATABASE_FILE)


if __name__ == "__main__":
    create_schema()
