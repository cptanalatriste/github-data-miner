"""
Module for storing the relationships between JIRA issues and GitHub commits.
"""

import dbutils

DATABASE_FILE = "jira_github.sqlite"

COMMITS_DDL = "CREATE TABLE issue_commit " \
              "(project_id TEXT, repository TEXT, issue_key TEXT, commit_sha TEXT," \
              " deletions INTEGER, lines INTEGER, insertions INTEGER, files INTEGER," \
              " PRIMARY KEY(project_id, repository, commit_sha, issue_key))"
TAGS_DDL = "CREATE TABLE commit_tag (project_id TEXT, repository TEXT, commit_sha TEXT, " \
           "tag_name TEXT, " \
           " PRIMARY KEY(project_id, repository, commit_sha, tag_name))"
TAG_TABLE_DDL = "CREATE TABLE git_tag (project_id TEXT, repository TEXT, tag_name TEXT, tag_date TEXT," \
                " PRIMARY KEY(project_id, repository, tag_name))"
COMMIT_TABLE_DDL = "CREATE TABLE git_commit (project_id TEXT, repository TEXT , commit_sha TEXT, " \
                   "deletions INTEGER, lines INTEGER, insertions INTEGER, files INTEGER," \
                   " PRIMARY KEY(project_id, repository, commit_sha))"


def get_tag_information(project_id, tag_name):
    """
    Returns the information of stored for a tag.
    :param project_id: JIRA's project identifier.
    :param tag_name: Tag name.
    :return:
    """
    tags_sql = "SELECT * FROM git_tag WHERE project_id=? and tag_name=?"
    tags = dbutils.execute_query(tags_sql, (project_id, tag_name), DATABASE_FILE)
    return tags


def create_schema():
    """
    Creates the tables for storing the Github-JIRA information.
    :return: None
    """
    dbutils.create_schema([COMMIT_TABLE_DDL], DATABASE_FILE)


def insert_git_tags(db_records):
    """
    Inserts tag information into the database.
    :param db_records:  List of tuples.
    :return: None.
    """
    insert_tag = "INSERT INTO git_tag VALUES (?, ?, ?, ?)"
    dbutils.load_list(insert_tag, db_records, DATABASE_FILE)


def insert_stats_per_commit(db_records):
    """
    Inserts a list of commit statistics into the database.
    :param db_records: List, containing tuples for commit stats.
    :return: None.
    """
    insert_commit = "INSERT INTO commit_stats VALUES (?, ?, ?, ?, ?, ?, ?)"
    dbutils.load_list(insert_commit, db_records, DATABASE_FILE)


def insert_commits_per_issue(db_records):
    """
    Inserts commit basic information, excluding stats.
    :param db_records: List of tuples.
    :return: None
    """
    insert_commit = "INSERT INTO issue_commit (project_id, repository, issue_key, commit_sha)" \
                    " VALUES (?, ?, ?, ?)"
    dbutils.load_list(insert_commit, db_records, DATABASE_FILE)


def insert_tags_per_commit(db_records):
    """
    Inserts a list of tuples with tag per commit information, excluding dates.
    :param db_records: List of tuples.
    :return: None.
    """
    insert_tag = "INSERT INTO commit_tag (project_id, repository, commit_sha, tag_name) VALUES (?, ?, ?, ?)"
    dbutils.load_list(insert_tag, db_records, DATABASE_FILE)


def get_commits_per_project(project_id):
    """
    Returns the commit sha's with the corresponding repository for an specific JIRA project.
    :param project_id: JIRA's project identifier.
    :return: List of commit SHA's
    """
    commits_sql = "SELECT DISTINCT commit_sha, repository FROM issue_commit WHERE project_id=?"
    commits = dbutils.execute_query(commits_sql, (project_id,), DATABASE_FILE)
    return commits


def get_commits_by_issue(project_id, key):
    commit_sql = "SELECT * FROM issue_commit WHERE project_id=? AND issue_key=?"
    return dbutils.execute_query(commit_sql, (project_id, key), DATABASE_FILE)


def get_tags_by_commit_sha(project_id, commit_sha):
    tag_sql = "SELECT * FROM commit_tag WHERE project_id=? AND commit_sha=?"
    return dbutils.execute_query(tag_sql, (project_id, commit_sha), DATABASE_FILE)


def get_tags_per_project(project_id):
    """
    Returns the tag names for an specific JIRA project. It only considers the tags related
    to the commits identified in Git.
    :param project_id: JIRA's project identifier.
    :return: List of tags.
    """
    tags_sql = "SELECT distinct tag_name, repository FROM commit_tag WHERE project_id=?"
    tags = dbutils.execute_query(tags_sql, (project_id,), DATABASE_FILE)
    return tags


if __name__ == "__main__":
    create_schema()
