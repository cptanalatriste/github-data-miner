"""
Module for the calculation of the releases to fix field.
"""
import re
from bisect import bisect

import os
import git
import winsound

from dateutil.tz import tzlocal

import loader
import jdata
import gjdata
import gminer
import pandas as pd
import matplotlib.pyplot as plt
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
VERSION_ID_INDEX = 4
VERSION_NAME_INDEX = 6
SHA_INDEX = 3
TAG_NAME_INDEX = 3
RESNAME_INDEX = 34
STATUS_INDEX = 35
PRIORNAME_INDEX = 36
CREATED_DATE = 15


def get_first_last_version(versions):
    """
    Returns the first and last items from a list of versions after sorting.
    :param versions: List of versions.
    :return: First and last versions as tuples.
    """
    sorted_versions = sorted(versions, key=lambda version: version[VERSION_NAME_INDEX])
    earliest_version = sorted_versions[0] if len(sorted_versions) > 0 else None
    latest_version = sorted_versions[-1] if len(sorted_versions) > 0 else None
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
    filename = ".\\" + project_id + "\\Release_Counter_" + project_id + ".csv"
    return filename


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
                     "Fix distance", "JIRA Distance in Releases", "GitHub Distance in Releases",
                     "Fix Distance in Releases"]
    issues_dataframe = DataFrame(records, columns=column_header)

    print "Writing " + str(len(records)) + " issues in " + get_csv_file_name(project_id)

    file_name = get_csv_file_name(project_id)
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))
    issues_dataframe.to_csv(file_name)

    return issues_dataframe


def preprocess(project_id, release):
    # TODO(cgavidia): This looks awful. Refactor later.
    if project_id == "12313920":
        if release == "pre-4.0.0":
            return "3.0.0"
        elif release == "Future":
            return "5.0.0"

    return release


def get_release_date_jira(version_id):
    """
    Returns the date for an specific release on the JIRA Database.
    :param version_id: JIRA version identifier.
    :return: The date as a datetime.
    """

    date_from_jira = jdata.get_version_by_id(version_id)
    if date_from_jira and date_from_jira[0][3]:
        date_as_timestamp = date_from_jira[0][3] / 1000
        result = datetime.datetime.fromtimestamp(date_as_timestamp, tz=tzlocal())
        return result

    return None


def get_version_position_jira(project_id, version_name):
    """
    Returns the position of the release in the list of sorted releases.
    :param project_id: JIRA project identifier
    :param version_name:  Version name.
    :return: Version position.
    """
    all_versions = jdata.get_versions_by_project(project_id)
    version_names = sorted([version[VERSION_NAME_INDEX] for version in all_versions])

    return bisect(version_names, version_name)


def get_version_position_git(project_id, tag_name):
    """
    Returns the position of the tag in the list of sorted tags.
    :param project_id: JIRA project identifier
    :param tag_name:  Version name.
    :return: Tag position.
    """
    all_tags = gjdata.get_tags_by_project(project_id)
    tag_name_index = 2
    tag_names = sorted([tag[tag_name_index] for tag in all_tags])

    return bisect(tag_names, tag_name)


def get_release_distance_jira(project_id, one_release, other_release, unit="days"):
    """
    Calculates the release distance between two releases using information stored in JIRA.
    :param project_id: JIRA Project Identifier.
    :param one_release: Version information.
    :param other_release: Another version information.
    :return: Distance between the two releases.
    """
    if not one_release or not other_release:
        return None

    if unit == "days":
        one_release_value = get_release_date_jira(one_release[VERSION_ID_INDEX])
        other_release_value = get_release_date_jira(other_release[VERSION_ID_INDEX])

    if unit == "releases":
        one_release_value = get_version_position_jira(project_id, one_release[VERSION_NAME_INDEX])
        other_release_value = get_version_position_jira(project_id, other_release[VERSION_NAME_INDEX])

    if other_release_value and one_release_value:
        difference = other_release_value - one_release_value
        return difference

    return None


def get_release_distance_git(project_id, one_release, other_release, unit="days"):
    """
    Calculates the release distance between two releases using information stored in Git.
    :param project_id: JIRA Project Identifier.
    :param one_release: Tag name.
    :param other_release: Another tag name.
    :return: Distance between the two releases.
    """
    if not one_release or not other_release:
        return None

    if unit == "days":
        one_release_value = get_release_date_git(project_id, one_release)
        other_release_value = get_release_date_git(project_id, other_release)

    if unit == "releases":
        one_release_value = get_version_position_git(project_id, one_release)
        other_release_value = get_version_position_git(project_id, other_release)

    if other_release_value and one_release_value:
        difference = other_release_value - one_release_value
        return difference

    return None


def get_release_date_git(project_id, release_name):
    """
    Returns the date for an specific tag on Git.
    :param project_id: JIRA project identifier.
    :param release_name: Tag name
    :return: The date as a datetime.
    """
    date_from_git = gjdata.get_tag_information(project_id, release_name)

    if date_from_git and len(date_from_git) == 1:
        date_as_string = date_from_git[0][3]
        result = dateutil.parser.parse(date_as_string)
        return result

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
    :param release_regex: Regular expression for valid releases.
    :param jira_to_git_release: A function to convert a JIRA release into a Git one.
    :return: A Dataframe with the consolidated information.
    """
    print "Generating consolidated file for project: ", project_id
    project_issues = jdata.get_project_issues(project_id)

    records = []
    tags_alert = True

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
        tags_per_comit = get_tags_for_commits(project_id, commits, release_regex=release_regex)
        if len(tags_per_comit) > 0:
            tags_alert = False

        earliest_tag = get_earliest_tag(tags_per_comit)

        jira_time_distance = get_release_distance_jira(project_id, earliest_affected, earliest_fix, unit="days")
        jira_distance = jira_time_distance.days if jira_time_distance else None
        jira_distance_releases = get_release_distance_jira(project_id, earliest_affected, earliest_fix, unit="releases")

        github_time_distance = get_release_distance_git(project_id, jira_to_git_release(earliest_affected),
                                                        earliest_tag, unit="days")
        github_distance = github_time_distance.days if github_time_distance else None
        github_distance_releases = get_release_distance_git(project_id, jira_to_git_release(earliest_affected),
                                                            earliest_tag, unit="releases")

        github_jira_distance = None
        if jira_distance and github_distance:
            github_jira_distance = jira_distance - github_distance

        fix_distance = get_fix_distance(jira_distance, github_distance)
        fix_distance_releases = get_fix_distance(jira_distance_releases, github_distance_releases)

        earliest_affected_name = earliest_affected[VERSION_NAME_INDEX] if earliest_affected  else None
        latest_affected_name = latest_affected[VERSION_NAME_INDEX] if latest_affected else None
        earliest_fix_name = earliest_fix[VERSION_NAME_INDEX] if earliest_fix else None
        latest_fix_name = latest_fix[VERSION_NAME_INDEX] if latest_fix else None

        csv_record = (
            key, resolution, status, priority, earliest_affected_name, latest_affected_name, earliest_fix_name,
            latest_fix_name, len(commits), len(tags_per_comit), earliest_tag, github_jira_distance, jira_distance,
            github_distance, fix_distance, jira_distance_releases, github_distance_releases, fix_distance_releases)
        print "Analizing Issue " + key
        records.append(csv_record)

    if tags_alert:
        print "WARNING: No tags were found as valid release names for each of the commits."

    return write_consolidated_file(project_id, records)


def commit_analysis(repositories, project_id, project_key):
    print "Analizing commits for project ", project_id

    total_commits = 0
    with_jira_reference = 0
    for repository in repositories:
        # TODO I don't like this dependency either ...
        repository_location = loader.REPO_LOCATION + repository

        git_client = git.Git(repository_location)

        log_lines = git_client.log(ALL_BRANCHES_OPTION, ONE_LINE_OPTION).splitlines()
        total_commits += len(log_lines)

        messages = [log_line.partition(' ')[2] for log_line in log_lines]
        with_jira_reference += sum(1 for message in messages if project_key in message) / float(total_commits)

    print "Total commits: ", total_commits
    print "Commits with project key: ", with_jira_reference

    labels = ["Contain JIRA key (" + str(with_jira_reference * 100) + " %)",
              "Does not contain JIRA key (" + str((1 - with_jira_reference) * 100) + " %)"]
    sizes = [with_jira_reference, 1 - with_jira_reference]

    figure, axes = plt.subplots(1, 1, figsize=(10, 10))

    patches, texts = plt.pie(sizes)
    axes.set_title(
        "Git commit messages containing JIRA key: " + str(total_commits) + " commits for Project " + project_key)
    plt.legend(patches, labels, loc="best")
    plt.savefig(".\\" + project_id + "\\Commits_with_JIRA_key_for_" + project_id + ".png")


def priority_analysis(project_key, project_id, resolved_issues):
    """
    Generates charts regarding the relationship between priority and fix distance.
    :param project_id: Project identifier.
    :param resolved_issues: Dataframe with project issues.
    :return: None.
    """

    # distance_column = 'Fix distance'
    distance_column = "Fix Distance in Releases"
    priority_list = ['Blocker', 'Critical', 'Major', 'Minor', 'Trivial']

    priority_column = 'Priority'
    print "Generating histograms for project ", project_key

    priority_label = "Priority"
    issues_percentage_label = "% of issues"
    releases_label = "Number of releases"
    fix_distance_label = "Distance between affected release and fix release: "
    issues_in_project_label = " Issues in Project "

    figure, axes = plt.subplots(1, 1, figsize=(10, 10))
    resolved_issues[priority_column].value_counts(normalize=True).plot(kind='bar', ax=axes)
    issues = str(len(resolved_issues.index))
    axes.set_xlabel(priority_label)
    axes.set_ylabel(issues_percentage_label)
    axes.set_title("Priority Distribution for " + issues + issues_in_project_label + project_key)
    axes.get_figure().savefig(".\\" + project_id + "\\Priority_Distribution_for_" + project_id + ".png")

    figure, axes = plt.subplots(1, 1, figsize=(10, 10))
    resolved_issues['Commits'].value_counts(normalize=True).sort_index().plot(kind='bar', ax=axes)
    axes.set_xlabel("Commits per issue")
    axes.set_ylabel(issues_percentage_label)
    axes.set_title("Number of Git Commits per JIRA issue: " + issues + issues_in_project_label + project_key)
    axes.get_figure().savefig(".\\" + project_id + "\\Commits_Distribution_for_" + project_id + ".png")

    priority_samples = []

    for priority_value in priority_list:
        priority_issues = resolved_issues[resolved_issues[priority_column] == priority_value]

        figure, axes = plt.subplots(1, 1, figsize=(10, 10))
        priority_issues[distance_column].hist(ax=axes, normed=True)

        issues = str(len(priority_issues.index))
        axes.set_xlabel(releases_label)
        axes.set_ylabel(issues_percentage_label)
        axes.set_title(fix_distance_label + issues + " " + priority_value +
                       issues_in_project_label + project_key)
        axes.get_figure().savefig(".\\" + project_id + "\\Priority_" + priority_value + "_" + project_id + ".png")

        priority_samples.append(priority_issues[distance_column])

    print "Generating consolidated priorities for project " + project_id
    issues = str(len(resolved_issues.index))

    figure, axes = plt.subplots(1, 1, figsize=(10, 10))
    axes.boxplot(priority_samples)
    axes.set_xticklabels(priority_list)
    axes.set_xlabel(priority_label)
    axes.set_ylabel(releases_label)
    axes.set_title(fix_distance_label + issues + issues_in_project_label + project_key)
    axes.get_figure().savefig(".\\" + project_id + "\\All_Priorities_" + project_id + ".png")


def get_project_dataframe(project_id):
    """
    Returns a dataframe with the issues valid for analysis.
    :param project_id: JIRA's project identifier.
    :return: Dataframe
    """
    issues_dataframe = pd.read_csv(get_csv_file_name(project_id))

    # distance_column = 'Fix distance'
    distance_column = "Fix Distance in Releases"

    resolved_issues = issues_dataframe[issues_dataframe['Status'].isin(['Closed', 'Implemented', 'Resolved'])]
    resolved_issues = issues_dataframe[issues_dataframe['Resolution'].isin(['Done', 'Fixed'])]
    resolved_issues = resolved_issues[~issues_dataframe[distance_column].isnull()]

    return resolved_issues


def main():
    try:
        for config in loader.get_project_catalog():
            project_id = config['project_id']
            release_regex = config['release_regex']
            jira_to_git_release = config['jira_to_git_release']
            repositories = config['repositories']
            project_key = config['project_key']

            # consolidate_information(project_id, release_regex, jira_to_git_release)

            project_dataframe = get_project_dataframe(project_id)
            priority_analysis(project_key, project_id, project_dataframe)
            commit_analysis(repositories, project_id, project_key)
    finally:
        # winsound.Beep(2500, 1000)
        pass


if __name__ == "__main__":
    main()
