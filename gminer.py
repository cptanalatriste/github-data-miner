"""
Module for information retrieval from GitHub API.
"""
from github import Github
import re
import sys

import config
import gdata

PER_PAGE = 100
APACHE_USER = 'apache'
RELEASE_REGEX = r"^(\d+\.)?(\d+\.)?(\*|\d+)$"

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def store_repository_tags(repository):
    """
    Retrieves all the tags of a repository and stores them in the database.
    :param repository: Reposiory instance.
    :return: None.
    """
    # Tags URL: https://api.github.com/repos/apache/cloudstack/tags
    repository_name = repository.name
    print "Getting tags from GitHub for repository " + repository_name
    tags = repository.get_tags()

    tag_list = []
    for index, tag in enumerate(tags):
        name = tag.name
        zipball_url = tag.zipball_url
        tarball_url = tag.tarball_url

        tag_commit = tag.commit
        commit_sha = tag_commit.sha
        commit_url = tag_commit.url

        tag_list.append((repository_name, name, zipball_url, tarball_url, commit_sha, commit_url))

    print "Writing tags into database for repository " + repository_name
    gdata.load_tags(tag_list)


def from_commit_to_tuple(repository_name, commit):
    sha = commit.sha
    commit_author_name = commit.commit.author.name
    commit_author_mail = commit.commit.author.email
    commit_author_date = commit.commit.author.date
    commit_committer_name = commit.commit.committer.name
    commit_committer_mail = commit.commit.committer.email
    commit_committer_date = commit.commit.committer.date
    commit_message = commit.commit.message
    commit_tree_sha = commit.commit.tree.sha
    commit_tree_url = commit.commit.tree.url

    # TODO(cgavidia): The version of pygithub I have installed doesn't cover that field
    # commit_comment_count = tag_commit.commit.comment_count
    commit_comment_count = 0

    url = commit.url
    html_url = commit.html_url
    comments_url = commit.comments_url
    stats_total = commit.stats.total
    stats_additions = commit.stats.additions
    stats_deletions = commit.stats.deletions

    return (repository_name, sha, commit_author_name, commit_author_mail, str(commit_author_date),
            commit_committer_name, commit_committer_mail, str(commit_committer_date),
            commit_message, commit_tree_sha, commit_tree_url, commit_comment_count,
            url, html_url, comments_url, stats_total, stats_additions, stats_deletions)


def store_commits_per_tag(repository):
    repository_name = repository.name

    print "Getting tags from database for repository " + repository_name
    stored_tags = gdata.get_repository_tags(repository_name)
    commit_sha_index = 4
    name_index = 1

    print "Getting commits from GitHub for repository " + repository_name
    commit_list = []
    for tag in stored_tags:
        commit_sha = tag[commit_sha_index]

        print "Getting commit for tag ", tag[name_index]
        tag_commit = repository.get_commit(commit_sha)

        commit_list.append(from_commit_to_tuple(repository_name, tag_commit))

    print "Writing commmits into database for repository " + repository_name
    gdata.load_commits(commit_list)


def store_repository_commits(repository):
    repository_name = repository.name
    print "Getting commits from GitHub from repository " + repository_name

    commit_list = []
    index = 0

    try:
        commits = repository.get_commits()

        buffer_size = 500
        for index, commit in enumerate(commits):
            if len(gdata.get_commit_by_url(commit.url)) > 0:
                print "Index ", index, ": Commit already stored: ", commit.url
                continue

            commit_as_tuple = from_commit_to_tuple(repository_name, commit)
            commit_list.append(commit_as_tuple)

            if len(commit_list) == buffer_size:
                print "Commit ", index, ": Writing ", buffer_size, " commits into database"
                gdata.load_commits(commit_list)
                commit_list = []

        print "Writing last batch of commits into database for repository " + repository_name
        gdata.load_commits(commit_list)
    except Exception as e:
        print >> sys.stderr, e
        print "An exception was thrown on commit ", index, " from ", repository_name
        print "Writing the commits stored so far ..."
        gdata.load_commits(commit_list)


def store_commits_between_tags(repository):
    tag_name_index = 0
    repository_name = repository.name
    tags_and_dates = [tag_date for tag_date in gdata.get_tags_and_dates(repository_name) if
                      re.match(RELEASE_REGEX, tag_date[tag_name_index])]

    # I'm not interested in the changes between time
    # tags_and_dates = sorted(tags_and_dates, key=lambda tag: datetime.datetime.strptime(tag[1], DATE_FORMAT),
    #                         reverse=True)

    tags_and_dates = sorted(tags_and_dates, key=lambda tag: tag[tag_name_index],
                            reverse=True)

    for index, current_tag in enumerate(tags_and_dates):
        tag_name = current_tag[tag_name_index]
        if re.match(RELEASE_REGEX, tag_name) and (index + 1) < len(tags_and_dates):
            previous_tag = tags_and_dates[index + 1]

            print "Getting commits between ", previous_tag[tag_name_index], " and ", current_tag[tag_name_index]
            comparison = repository.compare(previous_tag[tag_name_index], current_tag[tag_name_index])
            commit_list = []

            for commit in comparison.commits:
                commit_list.append(from_commit_to_tuple(repository_name, commit))

            url_index = 12
            compare_list = [
                (repository_name, previous_tag[tag_name_index], current_tag[tag_name_index], commit[url_index])
                for commit in commit_list]

            print "Storing commits ..."
            gdata.load_commits(commit_list)

            print "Storing compares ..."
            gdata.load_compares(compare_list)


def main():
    client = Github(config.get_github_token(), per_page=PER_PAGE)
    user = client.get_user(APACHE_USER)

    # TODO(cgavidia): Temporarly, we're only dealing with a single repository
    # Repo URL: https://api.github.com/repos/apache/cloudstack
    repository_name = 'cloudstack'
    repository = user.get_repo(repository_name)
    print 'client.rate_limiting ', client.rate_limiting

    # store_repository_tags(repository)
    # store_commits_per_tag(repository)
    # store_commits_between_tags(repository)

    store_repository_commits(repository)


if __name__ == "__main__":
    main()
