import os

JIRA_USER = os.environ.get('JIRA_USER')
API_TOKEN = os.environ.get('API_TOKEN')
SLACK_API = os.environ.get('SLACK_API')
TITLE_LINK = os.environ.get('TITLE_LINK')
JIRA_URL = os.environ.get('JIRA_URL')


colors_env = {
    "dev": "#36a64f",
    "staging": "#36a64f",
    "prod": "#f44242"
}


conf = {
    "title_link": TITLE_LINK,
    "jira_url": JIRA_URL
}
