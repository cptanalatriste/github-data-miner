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


def get_cassandra():
    """
    Git and JIRA plots are very similar, and it behaves like a regular project.

    Also, some negative values on Git.

    :return: Project configuration.
    """
    return {'project_key': "CASSANDRA",
            'project_id': "12310865",
            'release_regex': r"^cassandra-(\d+\.)?(\d+\.)?(\*|\d+)$",
            'repositories': ["cassandra"]}


def get_phoenix():
    """
    JIRA information is way distorted, and Git shows very thin boxes. A large amount of issues at delivered at the next
    release.

    Release information: https://phoenix.apache.org/release.html

    :return:Project configuration.
    """
    return {'project_key': "PHOENIX",
            'project_id': "12315120",
            'release_regex': r"^v(\d+\.)?(\d+\.)?(\*|\d+)$",
            'repositories': ["phoenix"]}


def get_slider():
    """

    A lot of thin boxes again. Several issues delivered on the next release.

    Release process: https://slider.incubator.apache.org/developing/releasing_process_v1.html

    :return: Project configuration.
    """
    return {'project_key': "SLIDER",
            'project_id': "12315422",
            'release_regex': r"^release-(\d+\.)?(\d+\.)?(\*|\d+)$",
            'repositories': ["incubator-slider"]}


def get_mesos():
    """
    We see a clear difference between each priority level, however we only have 25 issues.

    Also, no trivial issues are found.

    :return:Project configuration
    """
    return {'project_key': "MESOS",
            'project_id': "12311242",
            'release_regex': r"^(\d+\.)?(\d+\.)?(\*|\d+)$",
            'repositories': ["mesos"]}


def get_helix():
    """
    Almost all issues are Major, so Major has an usually large box.

    :return:Project configuration
    """
    return {'project_key': "HELIX",
            'project_id': "12314020",
            'release_regex': r"^helix-(\d+\.)?(\d+\.)?(\*|\d+)$",
            'repositories': ["helix"]}


def get_airavata():
    """
    Has 6+ repositories in Apache GitHub account. The two more active are airavata and airavata-php-gateway, which does
    not have tag information.

    Very slim boxes, again with a median at zero. JIRA infomation agrees, with slightly bigger boxes.

    Release process: http://airavata.apache.org/development/release-management.html

    :return: Project configuration.
    """
    return {'project_key': "AIRAVATA",
            'project_id': "12311302",
            'release_regex': r"^airavata-(\d+\.)?(\d+\.)?(\*|\d+)$",
            'repositories': ["airavata"]}


def get_ode():
    """
    Has 3 repositories in Apache GitHub account. Only ode -most popular- has release information.

    A couple of boxes on Blocker and Critical, and 0 modes on the other priorities. JIRA information is plagued with
    negatives.

    Release guidelines: http://ode.apache.org/developerguide/release-guidelines.html

    :return: Project configuration.
    """
    return {'project_key': "ODE",
            'project_id': "12310270",
            'release_regex': r"^APACHE_ODE_(\d+\.)?(\d+\.)?(\*|\d+)$",
            'repositories': ["ode"]}


def get_aurora():
    """
    Has 3 repositories in Apache GitHub account. The only project with tag information is aurora

    Again, very slim boxes with median at zero. JIRA seems to agree with wider boxes.

    Release guide: http://aurora.apache.org/documentation/latest/development/committers-guide/

    :return: Project configuration.
    """
    return {'project_key': "AURORA",
            'project_id': "12314922",
            'release_regex': r"^rel/(\d+\.)?(\d+\.)?(\*|\d+)$",
            'repositories': ["aurora"]}


# Unclear tag zone!


def get_geode():
    """
    The tag names seem confusing. Currently delayed.

    Besides, it seems to only have one release.

    :return: Project configuration.
    """
    return None


# Several repos zone!

def get_flex():
    """
    Has 10+ repositories in Apache GitHub account. Currently delayed.
    :return: Project configuration.
    """
    return None


def get_infra():
    """
    Several Git repositories. Although, I imagine not many commits are done here :S.

    Most active repository -infrastructure-puppet- doesn't have tags.

    :return: Project configuration.
    """
    return None


def get_uima():
    """
    Has 8+ repositories in Apache GitHub account. Currently delayed.
    :return: Project configuration.
    """
    return None


def get_npanday():
    """
    Has 2 repositories in Apache GitHub account, and none of them seems active. Currently delayed.

    Inconsistent Git Tag names.

    Release information: http://incubator.apache.org/npanday/docs/1.3-incubating/developers/releasing.html

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


# No repo zone!

def get_vcl():
    """
    Has no repository on the official Apache GitHub account.
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
