"""
This module makes priority and inflation calculations based on JIRA data
"""
import jdata

from bisect import bisect
from dateutil.tz import tzlocal
from collections import namedtuple

import datetime

VERSION_NAME_INDEX = 6
VERSION_ID_INDEX = 4
VERSION_DATE_INDEX = 3

AUTHOR_INDEX = 1
CREATED_INDEX = 0

TO_STRING_INDEX = 8
FROM_STRING_INDEX = 6
CHANGE_FIELD_INDEX = 3

VALID_RESOLUTION_VALUES = ['Done', 'Implemented', 'Fixed']


def get_version_position_jira(project_id, version_date):
    """
    Returns the position of the release in the list of sorted releases.
    :param project_id: JIRA project identifier
    :param version_date:  Version date.
    :return: Version position.
    """
    all_versions = jdata.get_versions_by_project(project_id)
    version_timestamps = sorted([version[VERSION_DATE_INDEX] for version in all_versions])

    return bisect(version_timestamps, version_date)


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
        one_release_value = get_version_position_jira(project_id, one_release[VERSION_DATE_INDEX])
        other_release_value = get_version_position_jira(project_id, other_release[VERSION_DATE_INDEX])

    if other_release_value and one_release_value:
        difference = other_release_value - one_release_value
        return difference

    return None


def get_release_date_jira(version_id):
    """
    Returns the date for an specific release on the JIRA Database.
    :param version_id: JIRA version identifier.
    :return: The date as a datetime.
    """

    date_from_jira = jdata.get_version_by_id(version_id)
    if date_from_jira and date_from_jira[0][VERSION_DATE_INDEX]:
        date_as_timestamp = date_from_jira[0][VERSION_DATE_INDEX] / 1000
        result = datetime.datetime.fromtimestamp(date_as_timestamp, tz=tzlocal())
        return result

    return None


def get_first_last_version(versions):
    """
    Returns the first and last items from a list of versions after sorting.
    :param versions: List of versions.
    :return: First and last versions as tuples.
    """
    sorted_versions = sorted(versions, key=lambda version: version[VERSION_DATE_INDEX])
    earliest_version = sorted_versions[0] if len(sorted_versions) > 0 else None
    latest_version = sorted_versions[-1] if len(sorted_versions) > 0 else None
    return earliest_version, latest_version


def get_closest_release(created_date, project_id):
    """
    Returns the release that is closer to a specific point in time.
    :param created_date: Date as timestamp.
    :param project_id: JIRA's Project Identifier.
    :return: Version tuple
    """
    all_versions = jdata.get_versions_by_project(project_id)
    all_versions_sorted = sorted(all_versions, reverse=True, key=lambda version: version[VERSION_DATE_INDEX])

    for version in all_versions_sorted:
        if version[VERSION_DATE_INDEX] > created_date:
            return version

    return None


def get_resolution_log(log_items):
    """
    Returns Resolution Log information. That is, the latest resolution log item to a valid resolution value.
    :param log_items: List of change log items.
    :return: Tuple with log information.
    """
    log = None

    sorted_log_items = sorted(log_items, reverse=True, key=lambda item: item[CREATED_INDEX])

    for log_item in sorted_log_items:
        if log_item[CHANGE_FIELD_INDEX] == "resolution" and log_item[TO_STRING_INDEX] in VALID_RESOLUTION_VALUES:
            return log_item

    return None


def get_last_priority_log(log_items):
    """
    Returns the last change on the priority of an issue.
    :param log_items: List of change log items.
    :return: Last priority change log item.
    """
    log = None

    sorted_log_items = sorted(log_items, reverse=True, key=lambda item: item[CREATED_INDEX])

    for log_item in sorted_log_items:
        if log_item[CHANGE_FIELD_INDEX] == "priority":
            return log_item

    return None


def get_reopen_logs(log_items):
    """
    Returns the change log items corresponding to Reopens
    :param log_items:
    :return: List of reopen log items.
    """

    return [log_item for log_item in log_items if
            log_item[CHANGE_FIELD_INDEX] == "status" and log_item[TO_STRING_INDEX] == "Reopened"]


def get_JIRA_metrics(issue_id, project_id, created_date):
    """
    Gathers issue inflation information from the JIRA database.
    :param issue_id: JIRA issue identifier.
    :param project_id: JIRA project identifier.
    :param created_date: Timestamp were the JIRA issue was created..
    :return: Earliest and latest affected versions, Earliest and latest fix versions, distance between earliest and
    latest affected versions in days, distance between earliest and latest affected versions in releases.
    """

    JiraMetrics = namedtuple("JiraMetrics",
                             ['earliest_affected', 'latest_affected_name', 'earliest_fix_name', 'latest_fix_name',
                              'distance',
                              'distance_releases', 'closest_release_name', 'resolved_by', 'resolution_date_parsed',
                              'resolution_time',
                              'issue_comments_len', 'priority_changed_by', 'priority_changed_to',
                              'priority_change_from', 'change_log_len', 'reopen_len'])

    fix_versions = jdata.get_fix_versions(issue_id)
    earliest_fix, latest_fix = get_first_last_version(fix_versions)
    earliest_fix_name = earliest_fix[VERSION_NAME_INDEX] if earliest_fix else None
    latest_fix_name = latest_fix[VERSION_NAME_INDEX] if latest_fix else None

    affected_versions = jdata.get_affected_versions(issue_id)
    earliest_affected, latest_affected = get_first_last_version(affected_versions)
    latest_affected_name = latest_affected[VERSION_NAME_INDEX] if latest_affected else None

    closest_release = get_closest_release(created_date, project_id)

    jira_time_distance = get_release_distance_jira(project_id, closest_release, earliest_fix, unit="days")
    jira_distance = jira_time_distance.days if jira_time_distance else None
    jira_distance_releases = get_release_distance_jira(project_id, closest_release, earliest_fix, unit="releases")
    closest_release_name = closest_release[VERSION_NAME_INDEX] if closest_release else None

    resolved_by = None
    resolution_date_parsed = None
    resolution_time = None

    log_items = jdata.get_change_log(issue_id)
    resolution_log = get_resolution_log(log_items)

    if resolution_log:
        resolved_by = resolution_log[AUTHOR_INDEX]
        resol_timestamp = resolution_log[CREATED_INDEX]
        resolution_date_parsed = datetime.datetime.fromtimestamp(resol_timestamp / 1000, tz=tzlocal())
        resolution_time = (resol_timestamp - created_date) / (1000 * 60 * 60)  # In hours

    priority_changed_by = None
    priority_changed_to = None
    priority_change_from = None

    priority_log = get_last_priority_log(log_items)
    if priority_log:
        priority_changed_by = priority_log[AUTHOR_INDEX]
        priority_changed_to = priority_log[TO_STRING_INDEX]
        priority_change_from = priority_log[FROM_STRING_INDEX]

    reopen_logs = get_reopen_logs(log_items)

    issue_comments = jdata.get_issue_comments(issue_id)

    jira_metrics = JiraMetrics(earliest_affected=earliest_affected, latest_affected_name=latest_affected_name,
                               earliest_fix_name=earliest_fix_name, latest_fix_name=latest_fix_name,
                               distance=jira_distance,
                               distance_releases=jira_distance_releases, closest_release_name=closest_release_name,
                               resolved_by=resolved_by, resolution_date_parsed=resolution_date_parsed,
                               resolution_time=resolution_time, issue_comments_len=len(issue_comments),
                               priority_changed_by=priority_changed_by, priority_changed_to=priority_changed_to,
                               priority_change_from=priority_change_from, change_log_len=len(log_items),
                               reopen_len=len(reopen_logs))

    return jira_metrics
