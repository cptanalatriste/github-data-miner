"""
This module makes priority and inflation calculations based on Git data
"""

import re

import datetime

from dateutil.tz import tzlocal
from collections import namedtuple

import gjdata
import gminer
import dateutil.parser

from bisect import bisect

TAG_NAME_INDEX = 3
SHA_INDEX = 3
TAG_DATE_INDEX = 3

COMMIT_DATE_INDEX = 8
COMMIT_DELETIONS = 3
COMMIT_LINES = 4
COMMIT_INSERTIONS = 5
COMMIT_FILES = 6
COMMITER_INDEX = 7
REPOSITORY_INDEX = 1


def get_version_position_git(project_id, tag_date, release_regex):
    """
    Returns the position of the tag in the list of sorted tags.
    :param project_id: JIRA project identifier
    :param tag_date:  Date of the tag.
    :param release_regex:  Regular expression for valid release names.
    :return: Tag position.
    """
    if tag_date:
        all_tags = gjdata.get_tags_by_project(project_id)
        tag_name_index = 2
        tag_date_index = 3

        tag_dates = sorted([dateutil.parser.parse(tag[tag_date_index]) for tag in all_tags if
                            re.match(release_regex, tag[tag_name_index])])

        return bisect(tag_dates, tag_date)
    else:
        return None


def get_release_distance_git(project_id, one_release, other_release, release_regex, unit="days"):
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
        one_release_date = get_release_date_git(project_id, one_release)
        other_release_date = get_release_date_git(project_id, other_release)

        one_release_value = get_version_position_git(project_id, one_release_date, release_regex)
        other_release_value = get_version_position_git(project_id, other_release_date, release_regex)

    if other_release_value and one_release_value:
        difference = other_release_value - one_release_value
        return difference

    return None


def get_tags_for_commits(project_id, commits, release_regex=gminer.RELEASE_REGEX):
    """
    Returns a list of tags for a list of commits, according to a version regular expression.
    :param project_id: JIRA Project identifier.
    :param commits: List of commits.
    :param release_regex: Regex to identify valid release names.
    :return: List of tag information.
    """
    tags_per_comit = []

    for commit in commits:
        tags = gjdata.get_tags_by_commit_sha(project_id, commit[SHA_INDEX])
        # Only including tags in release format
        release_tags = [tag for tag in tags if
                        re.match(release_regex, tag[TAG_NAME_INDEX])]

        if release_tags:
            tags_per_comit.append(release_tags)

    return tags_per_comit


def get_earliest_tag(tags_per_comit):
    """
    From the list of tags per commits, it returns the tag that happens earlier
    :param tags_per_comit: List of tags per several commits.
    :return: Earliest tag.
    """
    sorted_tags = []

    if tags_per_comit:
        tag_names = []
        for tag_list in tags_per_comit:
            tag_names.append([tag[TAG_NAME_INDEX] for tag in tag_list])

        # When no common tags found, select the minimum from all the available tags.
        tag_name_bag = set(tag_names[0]).union(*tag_names)

        # TODO This seems like a lot of work. And easier way must be possible
        flat_list = [tag for tag_list in tags_per_comit for tag in tag_list]
        tag_bag = []

        for tag_name in tag_name_bag:
            for tag in flat_list:
                if tag[TAG_NAME_INDEX] == tag_name:
                    tag_bag.append(tag)
                    break

        tag_date_index = 4
        sorted_tags = sorted(tag_bag, key=lambda tag: dateutil.parser.parse(tag[tag_date_index]))

    tag_name_index = 3
    earliest_tag = sorted_tags[0][tag_name_index] if len(sorted_tags) > 0 else ""

    return earliest_tag


def get_release_date_git(project_id, release_name):
    """
    Returns the date for an specific tag on Git.
    :param project_id: JIRA project identifier.
    :param release_name: Tag name
    :return: The date as a datetime.
    """

    date_from_git = gjdata.get_tag_information(project_id, release_name)

    if date_from_git and len(date_from_git) == 1:
        date_as_string = date_from_git[0][TAG_DATE_INDEX]
        result = dateutil.parser.parse(date_as_string)
        return result

    return None


def extract_version_number(release_name):
    """
    Extracts the release number in a release name.
    :param release_name: Release name.
    :return: Proper release number.
    """

    valid_regexs = ["(\d+\.\d+\.\d+)", "(\d+\.\d+)", "(\d+)"]
    for regex in valid_regexs:
        match = re.findall(regex, release_name)

        if match:
            found = match[0]
            return found


def get_closest_tag(created_date_parsed, project_id, release_regex):
    """
    Returns the closest release to an specific date.
    :param created_date_parsed: Specific date.
    :param project_id: Project identifier.
    :param release_regex: Valid release regular expression.
    :return: Closest tag.
    """
    all_tags = gjdata.get_tags_by_project(project_id)
    all_tags_sorted = sorted(all_tags, key=lambda tag: dateutil.parser.parse(tag[TAG_DATE_INDEX]))

    tag_name_index = 2
    all_tags_filtered = [tag for tag in all_tags_sorted if re.match(release_regex, tag[tag_name_index])]

    for tag in all_tags_filtered:
        if dateutil.parser.parse(tag[TAG_DATE_INDEX]) > created_date_parsed:
            return tag[tag_name_index]

    return None


def get_earliest_commit(project_id, key):
    """
    Returns the earliest commit related to a JIRA Issue, and the total line count and other aggregate commit metrics.
    :param project_id:
    :param key:
    :return:
    """
    commit_info, avg_lines, total_deletions, total_insertions, avg_files = None, None, None, None, None

    commits_per_issue = gjdata.get_commit_information(project_id, key)
    commits_sorted = sorted(commits_per_issue, key=lambda commit: commit[COMMIT_DATE_INDEX])

    if len(commits_sorted) > 0:
        commit_info = commits_sorted[0]

        avg_lines = sum([int(commit_info[COMMIT_LINES]) for commit_info in commits_per_issue]) / float(
            len(commits_per_issue))
        total_deletions = sum([int(commit_info[COMMIT_DELETIONS]) for commit_info in commits_per_issue])
        total_insertions = sum([int(commit_info[COMMIT_INSERTIONS]) for commit_info in commits_per_issue])
        avg_files = sum([int(commit_info[COMMIT_FILES]) for commit_info in commits_per_issue]) / float(
            len(commits_per_issue))

    return commit_info, avg_lines, total_deletions, total_insertions, avg_files


def get_github_metrics(project_id, key, release_regex, created_date):
    """
    Return the information extracted from GitHub
    :param project_id: JIRA's project identifier.
    :param key: JIRA's Issue Key.
    :param release_regex: Regex for valid release names,
    :param created_date: Creation date of the issue in a timestamp,
    :return: Earliest release tag, days between affected and fix tag, releases between affected and fix tag, number of commits for the issue,
    commits with release tags.
    """

    GitMetrics = namedtuple("GitMetrics", ['earliest_tag', 'distance', 'distance_releases', 'commits_len',
                                           'tags_per_commit_len',
                                           'closest_tag', 'commiter', 'commit_date', 'avg_lines', 'resolution_time',
                                           'repository',
                                           'total_deletions', 'total_insertions', 'avg_files'])

    commits = gjdata.get_commits_by_issue(project_id, key)
    tags_per_comit = get_tags_for_commits(project_id, commits, release_regex=release_regex)

    earliest_tag = get_earliest_tag(tags_per_comit)

    created_date_parsed = datetime.datetime.fromtimestamp(created_date / 1000, tz=tzlocal())
    closest_tag = get_closest_tag(created_date_parsed, project_id, release_regex)

    github_time_distance = get_release_distance_git(project_id, closest_tag,
                                                    earliest_tag, release_regex, unit="days")
    github_distance = github_time_distance.days if github_time_distance else None
    github_distance_releases = get_release_distance_git(project_id, closest_tag,
                                                        earliest_tag, release_regex,
                                                        unit="releases")

    earliest_commit, avg_lines, total_deletions, total_insertions, avg_files = get_earliest_commit(
        project_id, key)

    commiter = None
    repository = None
    commit_date = None
    resolution_time = None

    if earliest_commit:
        commiter = earliest_commit[COMMITER_INDEX]
        repository = earliest_commit[REPOSITORY_INDEX]
        if earliest_commit[COMMIT_DATE_INDEX]:
            commit_date = datetime.datetime.fromtimestamp(int(earliest_commit[COMMIT_DATE_INDEX]),
                                                          tz=tzlocal())
            resolution_time = (int(earliest_commit[COMMIT_DATE_INDEX]) - created_date / 1000) / (60 * 60)

    commits_len = len(commits)
    tags_per_commit_len = len(tags_per_comit)

    git_metrics = GitMetrics(earliest_tag=earliest_tag, distance=github_distance,
                             distance_releases=github_distance_releases, commits_len=commits_len,
                             tags_per_commit_len=tags_per_commit_len, closest_tag=closest_tag, commiter=commiter,
                             commit_date=commit_date, avg_lines=avg_lines, resolution_time=resolution_time,
                             repository=repository, total_deletions=total_deletions, total_insertions=total_insertions,
                             avg_files=avg_files)

    return git_metrics
