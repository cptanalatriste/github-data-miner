"""
Module for the calculation of the releases to fix field.
"""
import re
import csv
import git
import dbutils
import jdata
import gminer

COMMITS_DDL = "CREATE TABLE issue_commit " \
              "(project_id TEXT, issue_key TEXT, commit_sha TEXT," \
              " PRIMARY KEY(project_id, commit_sha, issue_key))"
TAGS_DDL = "CREATE TABLE commit_tag (project_id TEXT, commit_sha TEXT, tag_name TEXT," \
           " PRIMARY KEY(project_id, commit_sha, tag_name))"
DATABASE_FILE = "jira_github.sqlite"
PATTERN_OPTION = "--grep="
FORMAT_SHA_OPTION = "--pretty=%H"
CONTAINS_OPTION = "--contains"

# TODO(cgavidia): Move to JDATA module
KEY_INDEX = 31
ISSUE_ID_INDEX = 27
VERSION_NAME_INDEX = 6
SHA_INDEX = 2
TAG_NAME_INDEX = 2


def create_schema():
    dbutils.create_schema([COMMITS_DDL,
                           TAGS_DDL], DATABASE_FILE)


def get_tags_per_commit(repository_location, project_id):
    # TODO(cgavidia): Refactor ALL SQL to methods. And probably to a module.
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


def get_commits_by_issue(project_id, key):
    commit_sql = "SELECT * FROM issue_commit WHERE project_id=? AND issue_key=?"
    return dbutils.execute_query(commit_sql, (project_id, key), DATABASE_FILE)


def get_tags_by_commit_sha(project_id, commit_sha):
    tag_sql = "SELECT * FROM commit_tag WHERE project_id=? AND commit_sha=?"
    return dbutils.execute_query(tag_sql, (project_id, commit_sha), DATABASE_FILE)


def consolidate_information(project_id):
    project_issues = jdata.get_project_issues(project_id)

    records = []
    for issue in project_issues:
        key = issue[KEY_INDEX]
        issue_id = issue[ISSUE_ID_INDEX]
        affected_versions = jdata.get_affected_versions(issue_id)
        affected_versions = [version[VERSION_NAME_INDEX] for version in affected_versions]
        affected_versions = sorted(affected_versions)
        earliest_affected = affected_versions[0] if len(affected_versions) > 0 else ""
        latest_affected = affected_versions[-1] if len(affected_versions) > 0 else ""

        commits = get_commits_by_issue(project_id, key)
        unique_tags = set()

        for commit in commits:
            tags = get_tags_by_commit_sha(project_id, commit[SHA_INDEX])
            # Only including tags in release format
            unique_tags.update(
                [tag[TAG_NAME_INDEX] for tag in tags if re.match(gminer.RELEASE_REGEX, tag[TAG_NAME_INDEX])])

        sorted_tags = sorted(list(unique_tags))
        earliest_tag = sorted_tags[0] if len(sorted_tags) > 0 else ""

        csv_record = (key, earliest_affected, latest_affected, len(commits), len(unique_tags), earliest_tag)
        print csv_record
        records.append(csv_record)

    with open("Release_Counter_" + project_id + ".csv", "wb") as release_file:
        csv_writer = csv.writer(release_file)
        csv_writer.writerow(("Issue Key", "Earliest Version", "Latest Version", "Commits", "Tags", "Earliest Tag"))
        for record in records:
            csv_writer.writerow(record)


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

    # create_schema()
    # get_issues_and_commits(repository_location, project_id)
    # get_tags_per_commit(repository_location, project_id)
    consolidate_information(project_id)


if __name__ == "__main__":
    main()
