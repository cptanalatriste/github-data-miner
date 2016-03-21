"""
Handles the storage of Github information on a database
"""

import sqlite3

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


def load_list(sql_insert, row_list):
    """
    Inserts a list of items into the database.
    :param sql_insert: SQL for inserting a row.
    :param row_list: List containing tuples with tag information.
    :return: None.
    """
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    for row in row_list:
        cursor.execute(sql_insert, row)

    connection.commit()
    connection.close()


def load_compares(compare_list):
    """
    Inserts a list of comparisons into the database
    :param compare_list: List of comparisons, as tuples.
    :return: None
    """
    compare_insert = "INSERT INTO git_compare VALUES" \
                     " (?, ?, ?, ?)"
    load_list(compare_insert, compare_list)


def load_tags(tag_list):
    """
    Inserts a list of tags into the database.
    :param tag_list: List containing tuples with tag information.
    :return: None.
    """

    tag_insert = "INSERT INTO release_tag VALUES" \
                 " (?, ?, ?, ?, ?, ?)"
    load_list(tag_insert, tag_list)


def load_commits(commit_list):
    """
    Inserts a list of commits into the database
    :param commit_list: List containing tuples with commit information.
    :return: None
    """
    commit_insert = "INSERT OR REPLACE INTO github_commit VALUES " \
                    "(?, ? ,? ,? ,? ,? ,? ,? ,? ,? ,? ,? ,? ,? ,? ,? ,? ,?)"
    load_list(commit_insert, commit_list)


def get_tags_and_dates(repository_name):
    """
    Returns a list of tag with the corresponding date.
    :param repository_name:  Name of the repository
    :return: Tag names with dates.
    """
    tags_query = "SELECT t.name, c.commit_author_date " \
                 "FROM github_commit c, release_tag t " \
                 "where t.commit_url = c.url and t.repository=?"
    return execute_query(tags_query, (repository_name,))


def get_commit_by_url(commit_url):
    """
    Returns a commit related to its URL
    :param commit_url: Commit URL
    :return: List of commits
    """
    commit_sql = "SELECT * FROM github_commit WHERE url=?"
    return execute_query(commit_sql, (commit_url,))


def execute_query(sql_query, parameters):
    """
    Executes a query on the database
    :param sql_query: SQL Query
    :param parameters: Parameters for the query
    :return: Query results as a List
    """
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    cursor.execute(sql_query, parameters)
    results = cursor.fetchall()
    connection.close()

    return results


def get_repository_tags(repository_name):
    """
    Returns all the tags stored in the database for a repository
    :param repository_name: Repository name
    :return: List of tags
    """
    tags_query = "SELECT * FROM release_tag where repository=?"
    return execute_query(tags_query, (repository_name,))


def create_schema():
    """
    Creates the SQLite tables
    :return: None
    """
    print "Starting schema creation ..."
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    for table_ddl in TABLE_LIST:
        cursor.execute(table_ddl)

    connection.commit()
    connection.close()

    print "Schema creation finished"


if __name__ == "__main__":
    create_schema()
