"""
This module makes priority and inflation calculations based on Git data
"""

import re

import gjdata
import gminer
import dateutil.parser

from bisect import bisect

TAG_NAME_INDEX = 3
SHA_INDEX = 3
TAG_DATE_INDEX = 3


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


def get_github_metrics(project_id, key, release_regex, earliest_affected_git):
    """
    Return the information extracted from GitHub
    :param project_id: JIRA's project identifier.
    :param key: JIRA's Issue Key.
    :param release_regex: Regex for valid release names,
    :param earliest_affected_git: The earliest affected tag in git format.
    :return: Earliest release tag, days between affected and fix tag, releases between affected and fix tag, number of commits for the issue,
    commits with release tags.
    """
    commits = gjdata.get_commits_by_issue(project_id, key)
    tags_per_comit = get_tags_for_commits(project_id, commits, release_regex=release_regex)

    earliest_tag = get_earliest_tag(tags_per_comit)

    github_time_distance = get_release_distance_git(project_id, earliest_affected_git,
                                                    earliest_tag, release_regex, unit="days")
    github_distance = github_time_distance.days if github_time_distance else None
    github_distance_releases = get_release_distance_git(project_id, earliest_affected_git,
                                                        earliest_tag, release_regex, unit="releases")
    return earliest_tag, github_distance, github_distance_releases, len(commits), len(tags_per_comit)
