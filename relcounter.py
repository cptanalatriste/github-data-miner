"""
Module for the calculation of the releases to fix field.
"""

import git
import dbutils
import jdata

COMMITS_DDL = "CREATE TABLE issue_commit " \
              "(project_id TEXT, issue_key TEXT, commit_sha TEXT," \
              " PRIMARY KEY(project_id, commit_sha, issue_key))"
TAGS_DDL = "CREATE TABLE commit_tag (project_id TEXT, commit_sha TEXT, tag_name TEXT," \
           " PRIMARY KEY(project_id, commit_sha, tag_name))"
DATABASE_FILE = "jira_github.sqlite"
PATTERN_OPTION = "--grep="
FORMAT_SHA_OPTION = "--pretty=%H"
CONTAINS_OPTION = "--contains"
KEY_INDEX = 31


def create_schema():
    dbutils.create_schema([COMMITS_DDL,
                           TAGS_DDL], DATABASE_FILE)


def get_tags_per_commit(repository_location, project_id):
    commits_sql = "SELECT DISTINCT commit_sha FROM issue_commit WHERE project_id=?"
    commits = dbutils.execute_query(commits_sql, (project_id,), DATABASE_FILE)

    git_client = git.Git(repository_location)
    insert_tag = "INSERT INTO commit_tag VALUES (?, ?, ?)"

    for commit in commits:
        tags = git_client.tag(CONTAINS_OPTION, commit).split("\n")
        db_records = [(project_id, commit[0], tag) for tag in tags if tag]

        if db_records:
            print "Writing ", len(db_records), " tags for commit ", commit
            dbutils.load_list(insert_tag, db_records, DATABASE_FILE)
        else:
            print "No tags found for commit: ", commit


def get_issues_and_commits(repository_location, project_id):
    git_client = git.Git(repository_location)

    project_issues = jdata.get_project_issues(project_id)
    print "Issues in project: ", len(project_issues)
    insert_commit = "INSERT INTO issue_commit VALUES (?, ?, ?)"

    for issue in project_issues:
        key = issue[KEY_INDEX]
        commit_shas = git_client.log(PATTERN_OPTION + key, FORMAT_SHA_OPTION).split("\n")
        db_records = [(project_id, key, sha) for sha in commit_shas if sha]
        if (db_records):
            print "Writing ", len(db_records), " commits for Issue ", key
            dbutils.load_list(insert_commit, db_records, DATABASE_FILE)
        else:
            print "No commits found for Issue ", key


def main():
    # Configuration for CLOUDSTACK
    repository_location = "C:\Users\Carlos G. Gavidia\git\cloudstack"
    project_id = "12313920"

    create_schema()
    get_issues_and_commits(repository_location, project_id)
    get_tags_per_commit(repository_location, project_id)


if __name__ == "__main__":
    main()
