"""
This Module contains information about the Apache Projects considered for analysis.
"""


def get_cloudstack():
    """
    The Cloudstack project: and old friend. GitHub looks nice, but JIRA is full of negative distances.
    :return:Project configuration.
    """
    return {'project_key': "CLOUDSTACK",
            'project_id': "12313920",
            'release_regex': r"^(\d+\.)?(\d+\.)?(\*|\d+)$",
            'repositories': ["cloudstack"]}


def get_open_jpa():
    """
    The boxes for blocker and critical are unusually large, maybe an indicator of inflation? Also, we have a negative
    distance on Git :S

    As usual, JIRA data is full of negatives.
    :return: Project configuration.
    """
    return {'project_key': "OPENJPA",
            'project_id': "12310351",
            'release_regex': r"^(\d+\.)?(\d+\.)?(\*|\d+)$",
            'repositories': ["openjpa"]}


def get_spark():
    """
    The medians of blocker and critical are at zero, but also for Trivial.

    JIRA data for minor is incredibly negative.

    :return: Project configuration.

    """
    return {'project_key': "SPARK",
            'project_id': "12315420",
            'release_regex': r"^v(\d+\.)?(\d+\.)?(\*|\d+)$",
            'repositories': ["spark"]}


def get_mahout():
    """
    The box are incredibly thin, and all of them at zero. If we check the histograms per project, a lot of issues have a
    zero fix distance.

    JIRA shows the same behaviour, but including negatives.

    :return: Project configuration.
    """
    return {'project_key': "MAHOUT",
            'project_id': "12310751",
            'release_regex': r"^mahout-(\d+\.)?(\d+\.)?(\*|\d+)$",
            'repositories': ["mahout"]}


def get_kylin():
    """
    Unsually large boxes, in both Git and JIRA. Probable cause: almost ALL issues are labeled as Major.
    :return:Project configuration.
    """
    return {'project_key': "KYLIN",
            'project_id': "12316121",
            'release_regex': r"^(kylin-|v)(\d+\.)?(\d+\.)?(\*|\d+)$",
            'repositories': ["kylin"]}


def get_obbiz():
    """
    JIRA with huge negatives, and on Git an usual big box for blockers. A per-priority analysis shows
    that the zero release is still the predominant distance.
    :return: Project configuration.
    """
    return {'project_key': "OFBIZ",
            'project_id': "12310500",
            'release_regex': r"^REL-(\d+\.)?(\d+\.)?(\*|\d+)$",
            'repositories': ["ofbiz"]}


def get_isis():
    """
    Similar to Mahout: slim boxes with median at zero. Almost all the issues are concentrated between major and minor
    priorities, and this to levels have modes at zero distance.

    JIRA full with negatives again.
    :return: Project configuration.
    """
    return {'project_key': "ISIS",
            'project_id': "12311171",
            'release_regex': r"^rel/isis-(\d+\.)?(\d+\.)?(\*|\d+)$",
            'repositories': ["isis"]}


# No commit zone!

def get_acummulo():
    """
    Only 8 issues, with no commits
    :return: Project configuration.
    """
    # return {'project_key': "ACCUMULO",
    #         'project_id': "12312121",
    #         'release_regex': r"^(\d+\.)?(\d+\.)?(\*|\d+)$",
    #         'repositories': ["accumulo"]}
    return None


def get_helix():
    """
    None of the issues on our JIRA DB has commits on the Git Repository.

    :return:Project configuration
    """
    # return {'project_key': "HELIX",
    #         'project_id': "12314020",
    #         'release_regex': r"^helix-(\d+\.)?(\d+\.)?(\*|\d+)$",
    #         'repositories': ["helix"]}
    return None


def get_mesos():
    """
    None of the issues on our JIRA DB has commits on the Git Repository.

    :return:Project configuration
    """
    # return {'project_key': "MESOS",
    #         'project_id': "12311242",
    #         'release_regex': r"^(\d+\.)?(\d+\.)?(\*|\d+)$",
    #         'repositories': ["mesos"]}
    return None


def get_cassandra():
    """
    None of the commits on the Database contain the JIRA Issue Key.
    :return: Project configuration.
    """
    # return {'project_key': "CASSANDRA",
    #         'project_id': "12310865",
    #         'release_regex': r"^cassandra-(\d+\.)?(\d+\.)?(\*|\d+)$",
    #         'repositories': ["cassandra"]}
    return None


# No repo zone!

def get_vcl():
    """
    Has no repository on the official Apache GitHub account.
    :return: Project configuration.
    """
    return None


# Unclear tag zone!

def get_phoenix():
    """
    The tags for releases are not clear. Need to check documentation.
    :return:Project configuration.
    """
    return None


def get_slider():
    """
    A repository is on Git, but the tag names are uncommon. Currently delayed.
    :return: Project configuration.
    """
    return None


def get_geode():
    """
    The tag names seem confusing. Currently delayed.
    :return: Project configuration.
    """
    return None


# Several repos zone!

def get_flex():
    """
    Has several repositories in Apache GitHub account. Currently delayed.
    :return: Project configuration.
    """
    return None


def get_infra():
    """
    Several Git repositories. Although, I imagine not many commits are done here :S
    :return: Project configuration.
    """
    return None


def get_uima():
    """
    Has several repositories in Apache GitHub account. Currently delayed.
    :return: Project configuration.
    """
    return None


def get_npanday():
    """
    Has two repositories in Apache GitHub account, and none of them seems active. Currently delayed.
    :return: Project configuration.
    """
    return None


def get_airavata():
    """
    Has several repositories in Apache GitHub account. Currently delayed.
    :return: Project configuration.
    """
    return None


def get_ode():
    """
    Has several repositories in Apache GitHub account. Currently delayed.
    :return: Project configuration.
    """
    return None


def get_aurora():
    """
    Has several repositories in Apache GitHub account. Currently delayed.

    Although, the main repo seems identifiable.
    :return: Project configuration.
    """
    return None


def get_brooklyn():
    """
    Has several repositories in Apache GitHub account. Currently delayed.

    :return: Project configuration.
    """
    return None


def get_usergrid():
    """
    Has several repositories in Apache GitHub account. Currently delayed.

    Although, the main repo seems identifiable.
    :return: Project configuration.
    """
    return None


def get_project_catalog():
    """
    Returns the configuration for each project analyzed.
    :return: List of dicts.
    """
    return [
        get_obbiz(),
        get_flex(),
        get_cassandra(),
        get_infra(),
        get_cloudstack(),
        get_uima(),
        get_mahout(),
        get_open_jpa(),
        get_phoenix(),
        get_isis(),
        get_spark(),
        get_npanday(),
        get_airavata(),
        get_ode(),
        get_vcl(),
        get_slider(),
        get_kylin(),
        get_aurora(),
        get_mesos(),
        get_helix(),
        get_brooklyn(),
        get_usergrid(),
        get_geode(),
        get_acummulo()

    ]
