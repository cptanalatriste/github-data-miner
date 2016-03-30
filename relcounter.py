"""
Module for the calculation of the releases to fix field.
"""
import re
import git
import gjdata
import jdata
import gminer
import pandas as pd
import matplotlib.pyplot as plt

from pandas import DataFrame

WORD_BOUNDARY = r'\b'
PATTERN_OPTION = "--grep="
ALL_BRANCHES_OPTION = "--all"
FORMAT_SHA_OPTION = "--pretty=%H"
CONTAINS_OPTION = "--contains"

# TODO(cgavidia): Move to JDATA module
KEY_INDEX = 31
ISSUE_ID_INDEX = 27
VERSION_NAME_INDEX = 6
SHA_INDEX = 2
TAG_NAME_INDEX = 2
RESNAME_INDEX = 34
STATUS_INDEX = 35
PRIORNAME_INDEX = 36


def get_tags_per_commit(repository_location, project_id):
    commits = gjdata.get_commits_per_project(project_id)

    git_client = git.Git(repository_location)

    for commit in commits:
        tags = git_client.tag(CONTAINS_OPTION, commit).split("\n")
        db_records = [(project_id, commit[0], tag) for tag in tags if tag]

        if db_records:
            print "Writing ", len(db_records), " tags for commit ", commit
            gjdata.insert_tags_per_commit(db_records)
        else:
            print "No tags found for commit: ", commit


def get_first_last_version(versions):
    version_names = [version[VERSION_NAME_INDEX] for version in versions]
    version_names = sorted(version_names)
    earliest_version = version_names[0] if len(version_names) > 0 else ""
    latest_version = version_names[-1] if len(version_names) > 0 else ""
    return earliest_version, latest_version


def get_tags_for_commits(project_id, commits):
    tags_per_comit = []

    for commit in commits:
        tags = gjdata.get_tags_by_commit_sha(project_id, commit[SHA_INDEX])
        # Only including tags in release format
        release_tags = [tag[TAG_NAME_INDEX] for tag in tags if re.match(gminer.RELEASE_REGEX, tag[TAG_NAME_INDEX])]
        if release_tags:
            tags_per_comit.append(release_tags)

    return tags_per_comit


def get_csv_file_name(project_id):
    return "Release_Counter_" + project_id + ".csv"


def write_consolidated_file(project_id, records):
    column_header = ["Issue Key", "Resolution", "Status", "Priority", "Earliest Version", "Latest Version",
                     "Earliest Fix Version", "Latest Fix Version", "Commits",
                     "Commits with Tags", "Earliest Tag", "JIRA/GitHub Distance", "JIRA Distance", "GitHub distance",
                     "Fix distance"]
    issues_dataframe = DataFrame(records, columns=column_header)

    print "Writing " + str(len(records)) + " issues in " + get_csv_file_name(project_id)
    issues_dataframe.to_csv(get_csv_file_name(project_id))

    return issues_dataframe


def preprocess(project_id, release):
    # TODO(cgavidia): This looks awful. Refactor later.
    if project_id == "12313920":
        if release == "pre-4.0.0":
            return "3.0.0"
        elif release == "Future":
            return "5.0.0"

    return release


def get_release_distance(project_id, one_release, other_release):
    if not one_release or not other_release:
        return None

    separator = "."
    one_release_tokens = preprocess(project_id, one_release).split(separator)
    other_release_tokens = preprocess(project_id, other_release).split(separator)

    per_major = 7
    major_index = 0
    one_major = int(one_release_tokens[major_index])
    other_major = int(other_release_tokens[major_index])
    if one_major != other_major:
        return (other_major - one_major) * per_major

    per_minor = 3
    minor_index = 1
    one_minor = int(one_release_tokens[minor_index])
    other_minor = int(other_release_tokens[minor_index])
    if one_minor != other_minor:
        return (other_minor - one_minor) * per_minor

    per_patch = 1
    patch_index = 2
    one_patch = int(one_release_tokens[patch_index])
    other_patch = int(other_release_tokens[patch_index])
    if one_patch != other_patch:
        return (other_patch - one_patch) * per_patch

    return 0


def get_earliest_tag(tags_per_comit):
    sorted_tags = []

    if tags_per_comit:
        tag_bag = set(tags_per_comit[0]).intersection(*tags_per_comit)
        if not tag_bag:
            # When no common tags found, select the minimum from all the available tags.
            tag_bag = set(tags_per_comit[0]).union(*tags_per_comit)

        sorted_tags = sorted(list(tag_bag))

        # Minimum from Union
        # all_tags = set(tags_per_comit[0]).union(*tags_per_comit)
        # sorted_tags = sorted(list(all_tags))

        # Long lived only
        # long_lived_commit = max(tags_per_comit, key=len)
        # sorted_tags = sorted(list(long_lived_commit))

        # Intersection only
        # common_tags = set(tags_per_comit[0]).intersection(*tags_per_comit)
        # sorted_tags = sorted(list(common_tags))

    earliest_tag = sorted_tags[0] if len(sorted_tags) > 0 else ""
    return earliest_tag


def get_fix_distance(jira_distance, github_distance):
    if github_distance is not None:
        return github_distance

    return jira_distance


def consolidate_information(project_id):
    project_issues = jdata.get_project_issues(project_id)

    records = []
    for issue in project_issues:
        key = issue[KEY_INDEX]
        issue_id = issue[ISSUE_ID_INDEX]
        resolution = issue[RESNAME_INDEX]
        status = issue[STATUS_INDEX]
        priority = issue[PRIORNAME_INDEX]

        affected_versions = jdata.get_affected_versions(issue_id)
        earliest_affected, latest_affected = get_first_last_version(affected_versions)
        fix_versions = jdata.get_fix_versions(issue_id)
        earliest_fix, latest_fix = get_first_last_version(fix_versions)

        commits = gjdata.get_commits_by_issue(project_id, key)
        tags_per_comit = get_tags_for_commits(project_id, commits)
        earliest_tag = get_earliest_tag(tags_per_comit)

        github_jira_distance = get_release_distance(project_id, earliest_fix, earliest_tag)
        jira_distance = get_release_distance(project_id, earliest_affected, earliest_fix)
        github_distance = get_release_distance(project_id, earliest_affected, earliest_tag)

        fix_distance = get_fix_distance(jira_distance, github_distance)

        csv_record = (
            key, resolution, status, priority, earliest_affected, latest_affected, earliest_fix, latest_fix,
            len(commits), len(tags_per_comit),
            earliest_tag, github_jira_distance, jira_distance, github_distance, fix_distance)
        print "Analizing Issue " + key
        records.append(csv_record)

    return write_consolidated_file(project_id, records)


def get_issues_and_commits(repository_location, project_id):
    git_client = git.Git(repository_location)

    project_issues = jdata.get_project_issues(project_id)
    print "Issues in project: ", len(project_issues)

    for issue in project_issues:
        key = issue[KEY_INDEX]
        commit_shas = git_client.log(ALL_BRANCHES_OPTION, PATTERN_OPTION + WORD_BOUNDARY + key + WORD_BOUNDARY,
                                     FORMAT_SHA_OPTION).split(
            "\n")
        db_records = [(project_id, key, sha) for sha in commit_shas if sha]
        if db_records:
            print "Writing ", len(db_records), " commits for Issue ", key
            gjdata.insert_commits_per_issue(db_records)
        else:
            print "No commits found for Issue ", key


def priority_analysis(project_id):
    issues_dataframe = pd.read_csv(get_csv_file_name(project_id))

    distance_column = 'Fix distance'
    resolved_issues = issues_dataframe[issues_dataframe['Status'].isin(['Closed', 'Resolved'])]
    resolved_issues = resolved_issues[~issues_dataframe[distance_column].isnull()]

    priority_list = ['Blocker', 'Critical', 'Major', 'Minor', 'Trivial']

    print "Generating histograms for project ", project_id
    for priority_value in priority_list:
        priority_column = 'Priority'
        priority_issues = resolved_issues[resolved_issues[priority_column] == priority_value]
        priority_issues.hist(column=distance_column, normed=True)
        plt.savefig("Priority_" + priority_value + "_" + project_id + ".png")


def main():
    # Configuration for CLOUDSTACK
    repository_location = "C:\Users\Carlos G. Gavidia\git\cloudstack"
    project_id = "12313920"

    # create_schema()
    # get_issues_and_commits(repository_location, project_id)
    # get_tags_per_commit(repository_location, project_id)
    # consolidate_information(project_id)

    priority_analysis(project_id)


if __name__ == "__main__":
    main()
