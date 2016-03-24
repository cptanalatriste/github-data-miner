"""
Handles the storage of Github information on a database
"""

import sqlite3
import dbutils

DATABASE_FILE = "github.sqlite"
TAG_DDL = "CREATE TABLE release_tag " \
          "(repository TEXT, name TEXT, zipball_url TEXT, tarball_url TEXT, commit_sha TEXT ," \
          " commit_url TEXT, PRIMARY KEY (repository, name))"
COMMIT_DLL = "CREATE TABLE github_commit " \
             "(repository TEXT, sha TEXT, commit_author_name TEXT, commit_author_mail TEXT, commit_author_date TEXT, " \
             "commit_committer_name TEXT, commit_committer_mail TEXT, commit_committer_date TEXT, " \
             "commit_message TEXT, commit_tree_sha TEXT, commit_tree_url TEXT, commit_comment_count INTEGER," \
             "url TEXT PRIMARY KEY, html_url TEXT, comments_url TEXT, stats_total INTEGER, stats_additions INTEGER, " \
             "stats_deletions INTEGER)"
COMPARE_DDL = "CREATE TABLE git_compare " \
              "(repository TEXT, first_object TEXT, second_object TEXT, commit_url TEXT)"

TABLE_LIST = [TAG_DDL,
              COMMIT_DLL,
              COMPARE_DDL]


def load_compares(compare_list):
    """
    Inserts a list of comparisons into the database
    :param compare_list: List of comparisons, as tuples.
    :return: None
    """
    compare_insert = "INSERT INTO git_compare VALUES" \
                     " (?, ?, ?, ?)"
    dbutils.load_list(compare_insert, compare_list, DATABASE_FILE)


def load_tags(tag_list):
    """
    Inserts a list of tags into the database.
    :param tag_list: List containing tuples with tag information.
    :return: None.
    """

    tag_insert = "INSERT INTO release_tag VALUES" \
                 " (?, ?, ?, ?, ?, ?)"
    dbutils.load_list(tag_insert, tag_list, DATABASE_FILE)


def load_commits(commit_list):
    """
    Inserts a list of commits into the database
    :param commit_list: List containing tuples with commit information.
    :return: None
    """
    commit_insert = "INSERT OR REPLACE INTO github_commit VALUES " \
                    "(?, ? ,? ,? ,? ,? ,? ,? ,? ,? ,? ,? ,? ,? ,? ,? ,? ,?)"
    dbutils.load_list(commit_insert, commit_list, DATABASE_FILE)


def get_tags_and_dates(repository_name):
    """
    Returns a list of tag with the corresponding date.
    :param repository_name:  Name of the repository
    :return: Tag names with dates.
    """
    tags_query = "SELECT t.name, c.commit_author_date " \
                 "FROM github_commit c, release_tag t " \
                 "where t.commit_url = c.url and t.repository=?"
    return dbutils.execute_query(tags_query, (repository_name,), DATABASE_FILE)


def get_compares_by_commit(commit_url):
    """
    Returns all the compares involved on a commit
    :param commit_url: Commit URL
    :return: List of compare information.
    """
    compare_sql = "SELECT * from git_compare where commit_url=?"
    return dbutils.execute_query(compare_sql, (commit_url,), DATABASE_FILE)


def get_commits_by_repository(repository_name):
    """
    Returns commit information for a specific repository.
    :param repository_name: Repository name.
    :return: List of commits.
    """
    commit_sql = "SELECT * FROM github_commit WHERE repository=?"
    return dbutils.execute_query(commit_sql, (repository_name,), DATABASE_FILE)


def get_commit_by_url(commit_url):
    """
    Returns a commit related to its URL
    :param commit_url: Commit URL
    :return: List of commits
    """
    commit_sql = "SELECT * FROM github_commit WHERE url=?"
    return dbutils.execute_query(commit_sql, (commit_url,), DATABASE_FILE)


def get_commit_by_timerange(start, end):
    """
    Returns the list of commits in a time range
    :param start: Initial date as a string
    :param end: Final date as a string
    :return: List of commits.
    """
    commit_sql = "SELECT c.* FROM github_commit c WHERE " \
                 "substr(c.commit_committer_date, 0, 5) || substr(c.commit_committer_date, 6, 2) || substr(c.commit_committer_date, 9, 2) || " \
                 "substr(c.commit_committer_date, 12, 2) || substr(c.commit_committer_date, 15, 2) || substr(c.commit_committer_date, 18, 2) " \
                 "between ? and ?"
    print "commit_sql ", commit_sql

    return dbutils.execute_query(commit_sql, (start, end), DATABASE_FILE)


def get_repository_tags(repository_name):
    """
    Returns all the tags stored in the database for a repository
    :param repository_name: Repository name
    :return: List of tags
    """
    tags_query = "SELECT * FROM release_tag where repository=?"
    return dbutils.execute_query(tags_query, (repository_name,), DATABASE_FILE)


if __name__ == "__main__":
    dbutils.create_schema(TABLE_LIST, DATABASE_FILE)
