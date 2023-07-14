""" utility functions and constants """

# GitHub handles which should be notified when an issue is created
SUPERVISORS_BY_REGION = {
    'Global': [], # do not include '@', e.g. ['username1', 'username2']
    'AMER': [],
    'APAC': [],
    'EMEA': []
}

# Colors and prefixes for labels
LABEL_COLORS = {
    'date': '049BE5',
    'topic': '009051',
    'product': 'B60205',
    'region': '531B93',
    'stakeholder': 'A34100',
    'dri': 'D49E58'
}
# Always include a trailing space after PREFIX:
LABEL_PREFIXES = {
    'date': 'DATE: ',
    'topic': 'TOPIC: ',
    'product': 'PRODUCT: ',
    'region': 'REGION: ',
    'stakeholder': 'STAKEHOLDER: ',
    'dri': 'DRI: '
}
# If this is changed, also change the "labels" section of all issue templates
LABEL_PREFIX_TASK = 'TASK: '

# Visible label for DRI field
FIELD_DRI_LABEL = "DRI (list GitHub handles once you are ready to assign)"


# Don't edit below this line unless you know what you're doing :-)

import json
import os
import datetime
from dateutil.parser import parse as dateparse
from github import Github

def get_env_or_throw(env_var):
    value = os.getenv(env_var)
    if not value:
        raise Exception(f'Environment variable {env_var} not set')
    return value

DATE_FORMAT = '%Y-%m-%d'
NL = os.linesep
DT_NOW = datetime.datetime.now()
GITHUB_TOKEN = get_env_or_throw('GITHUB_TOKEN')
GH = Github(GITHUB_TOKEN)
WORKING_REPO = GH.get_repo(get_env_or_throw('REPOSITORY_NAME'))
KNOWN_FIELDS = {FIELD_DRI_LABEL: "dri"}


# retrieve issue specified by environment variable from working repo
def load_issue_from_env(env_var):
    issue_number = int(get_env_or_throw(env_var))
    issue = WORKING_REPO.get_issue(number=issue_number)
    # load known fields from json file
    for label in issue.labels:
        if label.name.startswith(LABEL_PREFIX_TASK):
            jsonfile = f'taskeract/field-mapping-{label.name[len(LABEL_PREFIX_TASK):]}.json'
            with open(jsonfile, 'r', encoding='utf-8') as jsonfile:
                jsondata = ''.join(line for line in jsonfile if not line.startswith('//'))
                for mapping in json.loads(jsondata):
                    KNOWN_FIELDS[mapping['field']] = mapping['variable']
    return issue


# attempt to parse and format number, or return original string
def parse_number(value):
    try:
        return '{:,}'.format(int(value.replace(',', '')))
    except Exception:
        return value


# attempt to parse and format datetime, or return original string
def parse_date(value):
    try:
        # 2n-nn-nn will parse as 202Y-MM-DD but nn/nn/nn will parse as MM/DD/YY
        value_hyphen_prefix = value.split('-')[0]
        if len(value_hyphen_prefix)==2 and value_hyphen_prefix.startswith('2'):
            value = f'20{value}'
        return dateparse(value, fuzzy=False).replace(tzinfo=None)
    except Exception as ex:
        print(ex)
        return None


def remove_labels_with_prefix(issue, label_prefix, except_label_list):
    for label in issue.labels:
        if label.name.startswith(label_prefix) and label not in except_label_list:
            issue.remove_from_labels(label)
            print(f'Unlabelled: {label.name}')


def get_or_create_label(label_text, label_color):
    label_text = label_text[:50]
    try:
        return WORKING_REPO.get_label(label_text)
    except Exception:
        return WORKING_REPO.create_label(name=label_text, color=label_color)


def append_dri_to_issue_body(issue):
    appendme = f'''
### {FIELD_DRI_LABEL}

TBD
'''
    issue.edit(body=f'{issue.body}{NL}{appendme}{NL}')

def dump_issue_data_to_github_env(fields):
    with open(get_env_or_throw('GITHUB_ENV'), "a") as github_env:
        github_env.write(f'ISSUE_DATA={json.dumps(fields)}')


# read fields from issue form, clean up empty items, reformat
def parse_issue_body_to_fields(issue):
    body=issue.body
    body_lines = body.splitlines()
    body_vars = {}
    found_vars = []
    last_key = None
    for line in body_lines:
        line = line.strip()
        if line.startswith('## '):
            continue
        if line.startswith('### '):
            found_key = line.strip('### ').split(' | ', 1)[0]
            try:
                last_key = KNOWN_FIELDS[found_key]
            except KeyError:
                print(f'WARNING: Unknown field "{found_key}" (this is usually fine, just be sure it is not a typo of a known field)')
                last_key = found_key #f'unknown_field {found_key}'
        elif last_key:
            found_vars.append(last_key)
            if not line.startswith('- [ ] '):
                line = line.lstrip('- [x] ').lstrip('- [X] ')
                if line and line != '_No response_':
                    line = parse_number(line)
                    if last_key == 'date':
                        line_date = parse_date(line)
                        line = line_date.strftime(DATE_FORMAT) if line_date else line
                    old_value = body_vars.get(last_key, '')
                    body_vars[last_key] = f'{old_value}{NL}{line}'.strip()
    for key,value in KNOWN_FIELDS.items():
        if not value in found_vars:
            print(f'WARNING: Missing field "{key}" (this usually indicates that you did not add it to the field-mapping file)')
    return body_vars


# create and assign a label for any text-based field
def assign_labels_string_field(issue, issue_body_vars, fieldname):
    if fieldname in issue_body_vars:
        labels_to_add = []
        try:
            for line in issue_body_vars[fieldname].splitlines():
                label = get_or_create_label(f"{LABEL_PREFIXES[fieldname]}{line.split(' (')[0]}", LABEL_COLORS[fieldname])
                labels_to_add.append(label)
            remove_labels_with_prefix(issue, LABEL_PREFIXES[fieldname], labels_to_add)
            for label in labels_to_add:
                if not label in issue.labels:
                    issue.add_to_labels(label)
                    print(f'Labelled: {label.name}')
        except Exception as ex:
            print(f"WARNING: unable to create '{fieldname}' label for {issue_body_vars[fieldname]}: {ex}")


# create and assign a label based on the date of the event
def assign_labels_date(issue, issue_body_vars):
    if 'date' in issue_body_vars:
        try:
            date = dateparse(issue_body_vars['date'], fuzzy=True)
            label = get_or_create_label(f"{LABEL_PREFIXES['date']}{date.year}-{date.month}", LABEL_COLORS['date'])
            remove_labels_with_prefix(issue, LABEL_PREFIXES['date'], [label])
            if not label in issue.labels:
                issue.add_to_labels(label)
                print(f'Labelled {label.name}')
        except Exception as ex:
            print(f"WARNING: unable create DATE label from {issue_body_vars['date']}: {ex}")


def assign_labels_topic(issue, issue_body_vars):
    assign_labels_string_field(issue, issue_body_vars, 'topic')


def assign_labels_product(issue, issue_body_vars):
    assign_labels_string_field(issue, issue_body_vars, 'product')


def assign_labels_region(issue, issue_body_vars):
    assign_labels_string_field(issue, issue_body_vars, 'region')


def assign_labels_stakeholder(issue, issue_body_vars):
    assign_labels_string_field(issue, issue_body_vars, 'stakeholder')


def assign_labels_dri(issue, issue_body_vars):
    dri = issue_body_vars.get('dri')
    print(f'dri: {dri}')
    if dri:
        dri_handles = [h[1:] for h in dri.split() if h.startswith('@')]
        if len(dri_handles)==0:
            remove_labels_with_prefix(issue, LABEL_PREFIXES['dri'], [])
        try:
            labels = [get_or_create_label(f"{LABEL_PREFIXES['dri']}{dri_handle}", LABEL_COLORS['dri']) for dri_handle in dri_handles]
            remove_labels_with_prefix(issue, LABEL_PREFIXES['dri'], labels)
            for label in labels:
                if not label in issue.labels:
                    issue.add_to_labels(label)
                    print(f'Labelled: {label.name}')
                    issue.add_to_assignees(label.name[len(LABEL_PREFIXES['dri']):])
                    print(f"Assigned: {label.name[len(LABEL_PREFIXES['dri']):]}")
        except Exception as ex:
            print(f"WARNING: unable to create 'dri' labels or assignments for {dri_handles}: {ex}")


def notify_supervisors(issue, issue_body_vars):
    handles_to_notify = []
    if 'region' in issue_body_vars:
        for line in issue_body_vars['region'].splitlines():
            region = line.split(' (')[0]
            handles_to_notify.extend(SUPERVISORS_BY_REGION[region])
    if not handles_to_notify:
        handles_to_notify.extend(SUPERVISORS_BY_REGION['Global'])
    if handles_to_notify:
        comment = f'@{handles_to_notify[0]}'
        for handle in handles_to_notify[1:]:
            comment += f', @{handle}'
        comment += ' - please triage this issue, and if accepted, set the "DRI" value in the BODY of the issue.'
        issue.create_comment(comment)
