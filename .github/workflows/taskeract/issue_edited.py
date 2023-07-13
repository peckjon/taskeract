
""" handles edit of issues """
from utils import *

# load issue
issue = load_issue_from_env('ISSUE_NUMBER')
fields = parse_issue_body_to_fields(issue)

# set labels
assign_labels_date(issue, fields)
assign_labels_topic(issue, fields)
assign_labels_product(issue, fields)
assign_labels_region(issue, fields)
assign_labels_stakeholder(issue, fields)

# set DRI label
assign_labels_dri(issue, fields)

# export ISSUE_DATA to github env
dump_issue_data_to_github_env(fields)