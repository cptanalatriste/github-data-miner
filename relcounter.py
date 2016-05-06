"""
Module for the calculation of the releases to fix field.
"""
from dateutil.tz import tzlocal

import datetime

import os
import git
import winsound

import jiracounter
import gitcounter
import loader
import jdata
import pandas as pd
import matplotlib.pyplot as plt

from pandas import DataFrame

ALL_BRANCHES_OPTION = "--all"
ONE_LINE_OPTION = "--pretty=oneline"

HEAD_OPTION = "-1"
DATE_FORMAT_OPTION = "--format=%ai"

# TODO(cgavidia): Move to JDATA module
KEY_INDEX = 31
ISSUE_ID_INDEX = 27

RESNAME_INDEX = 34
STATUS_INDEX = 35
PRIORNAME_INDEX = 36
CREATED_DATE = 15


def get_csv_file_name(project_id):
    filename = ".\\" + project_id + "\\Release_Counter_" + project_id + ".csv"
    return filename


def preprocess(project_id, release):
    # TODO(cgavidia): This looks awful. Refactor later.
    if project_id == "12313920":
        if release == "pre-4.0.0":
            return "3.0.0"
        elif release == "Future":
            return "5.0.0"

    return release


def get_fix_distance(jira_distance, github_distance):
    """
    Determines the criteria for selecting the information from Git or JIRA
    :param jira_distance:Distance from JIRA.
    :param github_distance: Distance from Git
    :return: Value for analysis.
    """
    if github_distance is not None:
        return github_distance

    if jira_distance >= 0:
        return jira_distance

    return None


def consolidate_information(project_id, release_regex):
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
        created_date = issue[CREATED_DATE]

        created_date_parsed = datetime.datetime.fromtimestamp(created_date / 1000, tz=tzlocal())

        # TODO This screams a refactor
        earliest_affected, latest_affected_name, earliest_fix_name, latest_fix_name, jira_distance, jira_distance_releases, closest_release_jira = jiracounter.get_JIRA_metrics(
            issue_id, project_id, created_date)
        earliest_affected_name = earliest_affected[jiracounter.VERSION_NAME_INDEX] if earliest_affected  else None

        earliest_tag, github_distance, github_distance_releases, commits, tags_per_comit, closest_tag = gitcounter.get_github_metrics(
            project_id, key, release_regex, created_date_parsed)

        github_jira_distance = None
        if jira_distance and github_distance:
            github_jira_distance = jira_distance - github_distance

        fix_distance = get_fix_distance(jira_distance, github_distance)
        fix_distance_releases = get_fix_distance(jira_distance_releases, github_distance_releases)

        csv_record = (
            key, resolution, status, priority, earliest_affected_name, latest_affected_name, earliest_fix_name,
            latest_fix_name, commits, tags_per_comit, earliest_tag, github_jira_distance, jira_distance,
            github_distance, fix_distance, jira_distance_releases, github_distance_releases, fix_distance_releases,
            created_date_parsed, closest_release_jira, closest_tag)
        print "Analizing Issue " + key
        records.append(csv_record)

    if tags_alert:
        print "WARNING: No tags were found as valid release names for each of the commits."

    return write_consolidated_file(project_id, records)


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
                     "Fix Distance in Releases", "Creation Date", "Closest Release JIRA", "Closest Tag Git"]
    issues_dataframe = DataFrame(records, columns=column_header)

    print "Writing " + str(len(records)) + " issues in " + get_csv_file_name(project_id)

    file_name = get_csv_file_name(project_id)
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))
    issues_dataframe.to_csv(file_name)

    return issues_dataframe


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


def priority_analysis(project_key, project_id, issues_dataframe, distance_column, file_prefix=""):
    """
    Generates charts regarding the relationship between priority and fix distance.
    :param project_key: Project key.
    :param project_id: Project identifier.
    :param issues_dataframe: Dataframe with project issues.
    :param distance_column: Dataframe series that contains the distance information.
    :param file_prefix: Prefix for the generated files.
    :return: None.
    """
    resolved_issues = issues_dataframe[~issues_dataframe[distance_column].isnull()]

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
    axes.get_figure().savefig(
        ".\\" + project_id + "\\" + file_prefix + "_Priority_Distribution_for_" + project_id + ".png")

    figure, axes = plt.subplots(1, 1, figsize=(10, 10))
    resolved_issues['Commits'].value_counts(normalize=True).sort_index().plot(kind='bar', ax=axes)
    axes.set_xlabel("Commits per issue")
    axes.set_ylabel(issues_percentage_label)
    axes.set_title("Number of Git Commits per JIRA issue: " + issues + issues_in_project_label + project_key)
    axes.get_figure().savefig(".\\" + project_id + "\\" + file_prefix +
                              "_Commits_Distribution_for_" + project_id + ".png")

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
        axes.get_figure().savefig(".\\" + project_id + "\\" + file_prefix +
                                  "_Priority_" + priority_value + "_" + project_id + ".png")

        priority_samples.append(priority_issues[distance_column])

    print "Generating consolidated priorities for project " + project_id
    issues = str(len(resolved_issues.index))

    figure, axes = plt.subplots(1, 1, figsize=(10, 10))
    axes.boxplot(priority_samples)
    axes.set_xticklabels(priority_list)
    axes.set_xlabel(priority_label)
    axes.set_ylabel(releases_label)
    axes.set_title(fix_distance_label + issues + issues_in_project_label + project_key)
    axes.get_figure().savefig(".\\" + project_id + "\\" + file_prefix +
                              "_All_Priorities_" + project_id + ".png")


def get_project_dataframe(project_id):
    """
    Returns a dataframe with the issues valid for analysis.
    :param project_id: JIRA's project identifier.
    :return: Dataframe
    """
    issues_dataframe = pd.read_csv(get_csv_file_name(project_id))

    resolved_issues = issues_dataframe[issues_dataframe['Status'].isin(['Closed', 'Implemented', 'Resolved'])]
    resolved_issues = issues_dataframe[issues_dataframe['Resolution'].isin(['Done', 'Fixed'])]
    resolved_issues = issues_dataframe[issues_dataframe['Commits'] > 0]

    return resolved_issues


def main():
    try:
        all_dataframes = []
        for config in loader.get_project_catalog():
            project_id = config['project_id']
            release_regex = config['release_regex']
            repositories = config['repositories']
            project_key = config['project_key']

            consolidate_information(project_id, release_regex)

            project_dataframe = get_project_dataframe(project_id)
            all_dataframes.append(project_dataframe)
            priority_analysis(project_key, project_id, project_dataframe, "JIRA Distance in Releases", "JIRA")
            priority_analysis(project_key, project_id, project_dataframe, "GitHub Distance in Releases", "GITHUB")
            priority_analysis(project_key, project_id, project_dataframe, "Fix Distance in Releases", "BOTH")

            commit_analysis(repositories, project_id, project_key)

        merged_dataframe = pd.concat(all_dataframes)
        priority_analysis("ALL", "", merged_dataframe, "JIRA Distance in Releases", "JIRA")
        priority_analysis("ALL", "", merged_dataframe, "GitHub Distance in Releases", "GITHUB")
        priority_analysis("ALL", "", merged_dataframe, "Fix Distance in Releases", "BOTH")
    finally:
        winsound.Beep(2500, 1000)
        pass


if __name__ == "__main__":
    main()
