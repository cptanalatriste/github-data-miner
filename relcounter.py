"""
Module for the calculation of the releases to fix field.
"""
import re
import git
from dateutil.tz import tzlocal

import loader
import jdata
import gjdata
import gminer
import pandas as pd
import matplotlib.pyplot as plt
import pprint
import dateutil.parser
import datetime

from pandas import DataFrame

ALL_BRANCHES_OPTION = "--all"
ONE_LINE_OPTION = "--pretty=oneline"

HEAD_OPTION = "-1"
DATE_FORMAT_OPTION = "--format=%ai"

# TODO(cgavidia): Move to JDATA module
KEY_INDEX = 31
ISSUE_ID_INDEX = 27
VERSION_NAME_INDEX = 6
SHA_INDEX = 3
TAG_NAME_INDEX = 3
RESNAME_INDEX = 34
STATUS_INDEX = 35
PRIORNAME_INDEX = 36
CREATED_DATE = 15


def get_first_last_version(versions):
    version_names = [version[VERSION_NAME_INDEX] for version in versions]
    version_names = sorted(version_names)
    earliest_version = version_names[0] if len(version_names) > 0 else ""
    latest_version = version_names[-1] if len(version_names) > 0 else ""
    return earliest_version, latest_version


def get_tags_for_commits(project_id, commits, release_regex=gminer.RELEASE_REGEX):
    """
    Returns a list of tags for a list of commits, according to a version regular expression.
    :param project_id: JIRA Project identifier.
    :param commits: List of commits.
    :param release_regex: Regex to identify valid release names.
    :return: List of tags.
    """
    tags_per_comit = []

    for commit in commits:
        tags = gjdata.get_tags_by_commit_sha(project_id, commit[SHA_INDEX])
        # Only including tags in release format
        release_tags = [tag[TAG_NAME_INDEX] for tag in tags if
                        re.match(release_regex, tag[TAG_NAME_INDEX])]

        if release_tags:
            tags_per_comit.append(release_tags)

    return tags_per_comit


def get_csv_file_name(project_id):
    return "Release_Counter_" + project_id + ".csv"


def write_consolidated_file(project_id, records):
    """
    Creates a Dataframe with the consolidated fix distance information and writes it to a CSV file.
    :param project_id: Project identifier in JIRA.
    :param records: Records to be included in the CSV file.
    :return: The created Dataframe.
    """
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


def get_release_date(project_id, release_name):
    """
    Returns the date for an specific release. First, it looks on Git and then on JIRA.
    :param project_id: JIRA project identifier.
    :param release_name: Release name.
    :return: The date as a datetime.
    """
    date_from_git = gjdata.get_tag_information(project_id, release_name)

    # We are addressing the case where the release tag is present in one repository.
    if date_from_git and len(date_from_git) == 1:
        date_as_string = date_from_git[0][3]
        result = dateutil.parser.parse(date_as_string)
        return result

    date_from_jira = jdata.get_version_by_name(project_id, release_name)
    if date_from_jira and date_from_jira[0][3]:
        date_as_timestamp = date_from_jira[0][3] / 1000
        result = datetime.datetime.fromtimestamp(date_as_timestamp, tz=tzlocal())
        return result

    return None


def get_release_distance(project_id, one_release, other_release, unit="days"):
    """
    Calculates the release distance between two releases.
    :param project_id: JIRA's project identifier.
    :param one_release: Release name.
    :param other_release: Another release name.
    :return: Distance between the two releases.
    """
    if not one_release or not other_release:
        return None

    if unit == "days":
        one_release_date = get_release_date(project_id, one_release)
        other_release_date = get_release_date(project_id, other_release)

        if other_release_date and one_release_date:
            difference = other_release_date - one_release_date
            return difference.days
    elif unit == "releases":
        # TODO: Complete this method implementation
        github_releases = []
        jira_versions = []

    return None


def get_earliest_tag(tags_per_comit):
    """
    From the list of tags per commits, it returns the tag that happens earlier
    :param tags_per_comit: List of tags per several commits.
    :return: Earliest tag.
    """
    sorted_tags = []

    if tags_per_comit:
        tag_bag = None
        if not tag_bag:
            # When no common tags found, select the minimum from all the available tags.
            tag_bag = set(tags_per_comit[0]).union(*tags_per_comit)

        sorted_tags = sorted(list(tag_bag))

    earliest_tag = sorted_tags[0] if len(sorted_tags) > 0 else ""
    return earliest_tag


def get_fix_distance(jira_distance, github_distance):
    if github_distance is not None:
        return github_distance

    return jira_distance


def consolidate_information(project_id, release_regex, jira_to_git_release):
    """
    Generetes a consolidated CSV report for the fix distance calculation.
    :param project_id: Project identifier in JIRA
    :return: A Dataframe with the consolidated information.
    """
    print "Generating consolidated file for project: ", project_id
    project_issues = jdata.get_project_issues(project_id)

    records = []
    for issue in project_issues:
        key = issue[KEY_INDEX]
        issue_id = issue[ISSUE_ID_INDEX]
        resolution = issue[RESNAME_INDEX]
        status = issue[STATUS_INDEX]
        priority = issue[PRIORNAME_INDEX]
        create_timestamp = issue[CREATED_DATE]

        # Apparently, the stored timestamp is in milliseconds
        creation_date = datetime.datetime.fromtimestamp(create_timestamp / 1000, tz=tzlocal())

        affected_versions = jdata.get_affected_versions(issue_id)
        earliest_affected, latest_affected = get_first_last_version(affected_versions)
        fix_versions = jdata.get_fix_versions(issue_id)
        earliest_fix, latest_fix = get_first_last_version(fix_versions)

        commits = gjdata.get_commits_by_issue(project_id, key)
        tags_per_comit = get_tags_for_commits(project_id, commits, release_regex=release_regex)
        earliest_tag = get_earliest_tag(tags_per_comit)

        # if len(commits) > 0:
        #     print 'earliest_affected ', earliest_affected, ' earliest_fix ', earliest_fix, ' earliest_tag ', earliest_tag

        github_jira_distance = get_release_distance(project_id, earliest_fix, earliest_tag)
        jira_distance = get_release_distance(project_id, earliest_affected, earliest_fix)
        github_distance = get_release_distance(project_id, jira_to_git_release(earliest_affected), earliest_tag)

        # print "jira_distance ", earliest_affected, earliest_fix, jira_distance
        # print "github_distance ", jira_to_git_release(earliest_affected), earliest_tag, github_distance

        fix_distance = get_fix_distance(jira_distance, github_distance)

        csv_record = (
            key, resolution, status, priority, earliest_affected, latest_affected, earliest_fix, latest_fix,
            len(commits), len(tags_per_comit),
            earliest_tag, github_jira_distance, jira_distance, github_distance, fix_distance)
        print "Analizing Issue " + key
        records.append(csv_record)

    return write_consolidated_file(project_id, records)


def commit_analysis(repository_location, project_id, project_key):
    print "Analizing commits for project ", project_id
    git_client = git.Git(repository_location)

    log_lines = git_client.log(ALL_BRANCHES_OPTION, ONE_LINE_OPTION).splitlines()
    total_commits = len(log_lines)

    messages = [log_line.partition(' ')[2] for log_line in log_lines]
    with_jira_reference = sum(1 for message in messages if project_key in message) / float(total_commits)
    non_jira_commits = [message for message in messages if project_key not in message]

    print "non_jira_commits ", pprint.pprint(non_jira_commits)
    print "Total commits: ", total_commits
    print "Commits with project key: ", with_jira_reference

    labels = ["Contain JIRA key (" + str(with_jira_reference * 100) + " %)",
              "Does not contain JIRA key (" + str((1 - with_jira_reference) * 100) + " %)"]
    sizes = [with_jira_reference, 1 - with_jira_reference]

    figure, axes = plt.subplots(1, 1, figsize=(10, 10))

    patches, texts = plt.pie(sizes)
    plt.legend(patches, labels, loc="best")
    plt.savefig("Commits_with_JIRA_key_for_" + project_id + ".png")


def priority_analysis(project_id):
    """
    Generates charts regarding the relationship between priority and fix distance.
    :param project_id: Project identifier.
    :return: None.
    """
    issues_dataframe = pd.read_csv(get_csv_file_name(project_id))

    distance_column = 'Fix distance'
    resolved_issues = issues_dataframe[issues_dataframe['Status'].isin(['Closed', 'Resolved'])]
    resolved_issues = issues_dataframe[issues_dataframe['Resolution'].isin(['Done', 'Fixed'])]
    resolved_issues = resolved_issues[~issues_dataframe[distance_column].isnull()]

    priority_list = ['Blocker', 'Critical', 'Major', 'Minor', 'Trivial']

    priority_column = 'Priority'
    print "Generating histograms for project ", project_id

    figure, axes = plt.subplots(1, 1, figsize=(10, 10))
    resolved_issues[priority_column].value_counts(normalize=True).plot(kind='bar', ax=axes)
    axes.set_xlabel("Priority")
    axes.set_ylabel("% of issues")
    axes.get_figure().savefig("Priority_Distribution_for_" + project_id + ".png")

    figure, axes = plt.subplots(1, 1, figsize=(10, 10))
    resolved_issues['Commits'].value_counts(normalize=True).sort_index().plot(kind='bar', ax=axes)
    axes.set_xlabel("Commits per issue")
    axes.set_ylabel("% of issues")
    axes.get_figure().savefig("Commits_Distribution_for_" + project_id + ".png")

    priority_samples = []

    for priority_value in priority_list:
        priority_issues = resolved_issues[resolved_issues[priority_column] == priority_value]

        figure, axes = plt.subplots(1, 1, figsize=(10, 10))
        priority_issues[distance_column].hist(ax=axes)
        axes.set_xlabel("Fix distance")
        axes.set_ylabel("% of " + str(priority_value) + " issues")
        axes.get_figure().savefig("Priority_" + priority_value + "_" + project_id + ".png")

        priority_samples.append(priority_issues[distance_column])

    print "Generating consolidated priorities for project " + project_id

    figure, axes = plt.subplots(1, 1, figsize=(10, 10))
    axes.boxplot(priority_samples)
    axes.set_xticklabels(priority_list)
    axes.set_xlabel("Priorities")
    axes.set_ylabel("Fix distance")
    axes.get_figure().savefig("All_Priorities_" + project_id + ".png")


def main():
    for config in loader.get_project_catalog():
        project_id = config['project_id']
        release_regex = config['release_regex']
        jira_to_git_release = config['jira_to_git_release']

        consolidate_information(project_id, release_regex, jira_to_git_release)
        priority_analysis(project_id)
        # commit_analysis(repository_location, project_id, project_key)


if __name__ == "__main__":
    main()
