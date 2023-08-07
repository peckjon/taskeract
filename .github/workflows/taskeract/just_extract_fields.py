
""" minimal sample to extract fields from form and make available in GitHub ENV """
from utils import *

# load issue
issue = load_issue_from_env('ISSUE_NUMBER')
fields = parse_issue_body_to_fields(issue)

# export ISSUE_DATA to github env
dump_issue_data_to_github_env(fields)
