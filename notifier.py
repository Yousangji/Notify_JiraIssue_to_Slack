#!/usr/bin/env python

from jira import JIRA, JIRAError
from slacker import Slacker
from config import settings
import sys
import os


def jira_tickets(issue_ids=[]):
    if not settings.JIRA_USER:
        return None

    jira = JIRA(settings.conf.get('jira_url'), basic_auth=(settings.JIRA_USER, settings.API_TOKEN))
    issues = []
    for t_id in sorted(issue_ids, reverse=True):
        try:
            issue = jira.issue(t_id)
            issues.append(issue)
        except JIRAError as e:
            print(str(e.args))

    changes = []

    for issue in issues:
        changes.append("%s %s - %s" % (issue.key, issue.fields.status.name, issue.fields.summary))

    return changes


def get_tickets(workspace="", start="origin/develop", end="HEAD", env="dev", board_name="KP"):
    if env == "prod":
        recent_git_tag = os.popen("git --git-dir " + workspace + "/.git describe").read()
        start = recent_git_tag.split("-")[0]

    changes_log_command_str = "git --git-dir " + workspace + "/.git log {0}..{1} | ".format(start, end)
    changes_log_command_str += "grep -o '{0}-[0-9]*' | sort | uniq".format(board_name)
    changes = os.popen(changes_log_command_str).read()
    return changes


def send_slack(project_name, workspace, env="dev", start="origin/develop", end='HEAD', board_name='KP', branch="develop", username="sangji", specific_tickets=""):

    changes = get_tickets(workspace=workspace, start=start, end=end, env=env, board_name=board_name)
    verbose_changes = jira_tickets(changes.split('\n'))

    for change in verbose_changes:
        print(change)
    slack = Slacker(settings.SLACK_API)
    slack.chat.post_message(
        channel="#kb_dev",
        text="<!here> %s , 환경: %s, 브랜치: %s 배포되었습니다. build_user: %s \n" % (project_name, env, branch, username),
        attachments=[
            {
                "text": ('\n'.join(verbose_changes) if verbose_changes else changes) + ("적용된 티켓: " + specific_tickets),
                "fallback": "Required plain-text summary of the attachment.",
                "color": settings.colors_env.get(env, "#36a64f"),
                "title": project_name,
                "title_link": settings.conf['title_link'] + project_name,
                "footer": "%sbrowse/%s" % (settings.conf.get('jira_url'), board_name)
            }
        ],
        username='konobot')


if __name__ == '__main__':
    env = sys.argv[1]
    git_path = sys.argv[2]
    send_slack(project_name=sys.argv[1], workspace=sys.argv[2], **dict(arg.split("=") for arg in sys.argv[3:]))