# Taskeract: automate task ingestion, issue creation, tagging, assignment, and projct board connections

Taskeract helps your team quickly receive, tag, triage, and track issues.

This sample repo contains issue templates for three types of tasks ("generic", "blogpost", and "video"), but you are free to create your own task types and delete the samples. Note the fields for `date`, `topic`, `product`, `region`, `stakeholders` -- each of these will be used by the automation to create labels on your issues so you can easily search & filter them.

## How to use this repo

Copy all files from the `.github` folder into your own repository's `.github` folder (or fork this repo if starting fresh)

Inside `.github/workflows/taskeract-created.yml` and `taskeract-edited.yml`, change `REPOSITORY_NAME` to be your new repository

If you'll be using [Project Boards](https://docs.github.com/en/github-ae@latest/issues/organizing-your-work-with-project-boards/managing-project-boards/about-project-boards):

- create a secret in your repo called `ADD_TO_PROJECT_PAT` which contains a token capable of editing any project boards you'll be adding issues to
- change the project URLs and field values in the "add to project and set project fields" section of `.github/workflows/taskeract-created.yml`

If you _won't_ be using Project Boards:

- delete the section under "add to project and set project fields" in `.github/workflows/taskeract-created.yml`

## What the automation does

- assigns newly-created issues to project boards (optional)
- adds labels to issues based on the following predefined fields: `date`, `topic`, `product`, `region`, `stakeholders`
- notifies supervisors (or whoever you want to triage your issues) based on the issue's `region` field
  - you can define who these supervisors are by setting their handles in `SUPERVISORS_BY_REGION` inside `.github/workflows/taskeract/utils.py`
- adds a "DRI" field to the **_body_** of the issue
  - this field does not appear until **_after_** the issue has been created, because the people _requesting_ the work should not necessarily _assign_ the work
  - once filled out, the DRI will be automatically added as an assignee
- adds the label "not planned" to issues closed as not planned

## Adding or deleting fields

Fields can be safely deleted from any issue template and the relevant field-mapping JSON file

New fields can be added to any issue template without affecting the automation

To add a field **_and_** create custom automation for that field:

- add the field to the relevant issue template
- find the associated `field-mapping-[TYPE].json` file inside `.github/workflows/taskeract/` and add an entry
  - the "field" value should exactly match the "label" value from the issue template
  - the "variable" should be a new unique value (preferably [snake_case](https://en.wikipedia.org/wiki/Snake_case))
- add a function to `.github/workflows/taskeract/utils.py` (see `assign_labels_topic` as an example... your new variable name from the prior step would replace `topics`)
- call this function from `.github/workflows/taskeract/issue_created.py` and/or `issue_edited.py`
  - if you'll be creating a new label from this field, be sure to add a `LABEL_PREFIX_[fieldname] = '[fieldname]: '` near the top of `utils.py`, and another entry inside `LABEL_COLORS` just below it.

## Adding a new task type

First, add a new issue template

- for the automation to work, it **_must_** have a label starting with `TASK: ` such as `labels: ["TASK: workshop"]` (the space is mandatory)

Next, add a new `field-mapping-[TYPE].json` file inside `.github/workflows/taskeract/`

- its content should be an array of field/variable maps (see `field-mapping-video.json` as an example)
- the "field" value should exactly match the "label" value from the issue template
- the "variable" should be a new unique value (preferably [snake_case](https://en.wikipedia.org/wiki/Snake_case))

Lastly, add any project assignments or field values needed to `.github/workflows/taskeract-created.yml` under "add to project and set project fields"

Note that unused task types can be safely removed by simply deleting their issue template and associated "field-mapping-[TYPE].json" file
