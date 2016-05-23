"""
Module for accessing JIRA database information.
"""

import dbutils

DATABASE_FILE = "C:\Users\Carlos G. Gavidia\OneDrive\phd2\jira_db\issue_repository.db"


def get_issue_by_key(key):
    issue_sql = "SELECT * FROM Issue WHERE key=?"
    return dbutils.execute_query(issue_sql, (key,), DATABASE_FILE)


def get_issue_comments(issue_id):
    """
    Returns all the comments for a JIRA Issue
    :param issue_id: JIRA Issue Identifier.
    :return: List of comments
    """
    comment_sql = "SELECT * FROM Comment WHERE issueId = ?"
    return dbutils.execute_query(comment_sql, (issue_id,), DATABASE_FILE)


def get_change_log(issue_id):
    """
    Return all the change log items for a JIRA issue.
    :param issue_id: JIRA issue id.
    :return: Log item list.
    """
    log_sql = "SELECT h.created, h.authorId, c.* FROM Issue i, History h, " \
              "ChangeLogItem c WHERE i.id = ? AND i.id  = h.issueId AND h.id = c.historyId"
    return dbutils.execute_query(log_sql, (issue_id,), DATABASE_FILE)


def get_versions_by_project(project_id):
    """
    Return version information by project id.
    :param project_id: JIRA project identifier.
    :return: Tuple with version information.
    """
    version_sql = "SELECT * FROM Version WHERE projectId=?"
    return dbutils.execute_query(version_sql, (project_id,), DATABASE_FILE)


def get_version_by_name(project_id, version_name):
    """
    Return version information by version name.
    :param project_id: JIRA project identifier.
    :param version_name: Version name.
    :return: Tuple with version information.
    """
    version_sql = "SELECT * FROM Version WHERE projectId=? AND name =?"
    return dbutils.execute_query(version_sql, (project_id, version_name), DATABASE_FILE)


def get_version_by_id(version_id):
    """
    Return version information by version id.
    :param version_id: JIRA version identifier.
    :return: Tuple with version information.
    """
    version_sql = "SELECT * FROM Version WHERE id=?"
    return dbutils.execute_query(version_sql, (version_id,), DATABASE_FILE)


def get_affected_versions(issue_id):
    version_sql = "SELECT v.* FROM Version v, Issue i ,VersionPerIssue vi " \
                  "WHERE i.id = vi.issueId AND vi.versionId = v.id AND i.id =?"

    return dbutils.execute_query(version_sql, (issue_id,), DATABASE_FILE)


def get_fix_versions(issue_id):
    version_sql = "SELECT v.* FROM Version v, Issue i , FixVersionPerIssue vi " \
                  "WHERE i.id = vi.issueId AND vi.versionId = v.id AND i.id =?"

    return dbutils.execute_query(version_sql, (issue_id,), DATABASE_FILE)


def get_project_issues(project_id):
    issue_sql = "SELECT i.* , r.name resname, s.name statname, p.name priorname " \
                "FROM Issue i " \
                "LEFT OUTER JOIN Resolution r ON i.resolutionId = r.id " \
                "LEFT OUTER JOIN Status s ON i.statusId = s.id " \
                "LEFT OUTER JOIN Priority p on i.priorityId = p.id " \
                "WHERE i.projectId=?"

    return dbutils.execute_query(issue_sql, (project_id,), DATABASE_FILE)
