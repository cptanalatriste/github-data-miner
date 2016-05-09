"""
Module reads information from Git and JIRA and moves it to the Database
"""

import git
import winsound

import catalog
import jdata
import gjdata
import platform

import jiracounter
import relcounter

WORD_BOUNDARY = r'\b'
PATTERN_OPTION = "--grep="
ALL_BRANCHES_OPTION = "--all"
FORMAT_SHA_OPTION = "--pretty=%H"
CONTAINS_OPTION = "--contains"

HEAD_OPTION = "-1"
DATE_FORMAT_OPTION = "--format=%ai"

# TODO(cgavidia): Move to JDATA module
KEY_INDEX = 31

REPO_LOCATION = 'C:\\Users\\Carlos G. Gavidia\\git\\'


def get_issues_and_commits(repositories, project_id):
    """
    Per each of the repositories, it searches commits containing JIRA's project key.
    :param repositories: List of repository locations.
    :param project_id: JIRA's Project Identifier.
    :return: None
    """

    project_issues = jdata.get_project_issues(project_id)
    print "Issues in project: ", len(project_issues)

    for issue in project_issues:

        key = issue[KEY_INDEX]

        for repository in repositories:
            repository_location = REPO_LOCATION + repository
            git_client = git.Git(repository_location)

            commit_shas = git_client.log(ALL_BRANCHES_OPTION, PATTERN_OPTION + WORD_BOUNDARY + key + WORD_BOUNDARY,
                                         FORMAT_SHA_OPTION).split("\n")
            db_records = [(project_id, repository, key, sha) for sha in commit_shas if sha]
            if db_records:
                print "Writing ", len(db_records), " commits for Issue ", key, " found on repo ", repository
                gjdata.insert_commits_per_issue(db_records)
            else:
                print "No commits found for Issue ", key, " in repository ", repository_location


def get_tags_per_commit(project_id):
    """
    For an specific project, it obtains the tags for all the commits of the project and stores them on the database.
    :param project_id: JIRA's project identifier.
    :return: None.
    """
    commits = gjdata.get_commits_per_project(project_id)

    for commit_sha, repository in commits:
        repository_location = REPO_LOCATION + repository
        git_client = git.Git(repository_location)

        tags = git_client.tag(CONTAINS_OPTION, commit_sha).split("\n")
        db_records = [(project_id, repository, commit_sha, tag) for tag in tags if tag]

        if db_records:
            print "Writing ", len(db_records), " tags for commit ", commit_sha
            gjdata.insert_tags_per_commit(db_records)
        else:
            print "No tags found for commit: ", commit_sha


def get_tags(project_id, repositories):
    """
    Retrieves and stores tag information.
    :param project_id: Project identifier.
    :param repositories: List of repositories.
    :return: None.
    """
    db_records = []

    for repository in repositories:
        repository_location = REPO_LOCATION + repository

        git_client = git.Git(repository_location)
        all_tags = git_client.tag().split("\n")

        for tag_name in all_tags:
            print "tag_name ", tag_name, " repository ", repository
            tag_date = git_client.log(HEAD_OPTION, DATE_FORMAT_OPTION, tag_name)

            print "Date for tag ", tag_name, " is ", tag_date
            db_records.append((project_id, repository, tag_name, tag_date))

    print "Updating ", len(db_records), " tag dates for project ", project_id
    gjdata.insert_git_tags(db_records)


def get_stats_per_commit(project_id):
    """
    Retrieves and stores commit stats in the database.
    :param project_id: JIRA project identifier.
    :return: None.
    """

    # To avoid the "too many open files" error
    # TODO The error persists. Waiting for a response from the community.
    if platform.system() == 'Windows':
        print "Changing the max files parameter..."
        import win32file
        win32file._setmaxstdio(2048)

    print "Retrieving stat information for commits on project " + project_id

    commits = gjdata.get_commits_per_project(project_id)
    db_records = []

    print "Reviewing ", len(commits), " commits..."
    for commit_sha, repository in commits:
        repository_location = REPO_LOCATION + repository
        repository = git.Repo(repository_location)
        commit = repository.rev_parse(commit_sha)

        print "Stats obtained for commit ", commit_sha
        total_stats = commit.stats.total
        db_records.append(
            (project_id, repository, commit_sha, total_stats['deletions'], total_stats['lines'],
             total_stats['insertions'],
             total_stats['files']))

        del total_stats
        del repository

    print "Storing ", len(db_records), " records in the database."
    gjdata.insert_stats_per_commit(db_records)


def main():
    try:
        for config in catalog.get_project_catalog():
            repositories = config['repositories']
            project_id = config['project_id']

            get_issues_and_commits(repositories, project_id)
            get_tags_per_commit(project_id)
            get_tags(project_id, repositories)
            # get_stats_per_commit(project_id)
    finally:
        winsound.Beep(2500, 1000)


if __name__ == "__main__":
    main()
