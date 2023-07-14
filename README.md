<img src="https://upload.wikimedia.org/wikipedia/commons/d/df/Tesseract-1K.gif" width="100" height="100" alt="A tesseract" />

# Taskeract: automate task ingestion, issue creation, tagging, assignment, and projct board connections

Taskeract helps your team quickly receive, tag, triage, and track issues.

This sample repo contains issue templates for three types of tasks ("generic", "blogpost", and "video"), but you are free to create your own task types and delete the samples. Note the fields for `date`, `topic`, `product`, `region`, `stakeholders` -- each of these will be used by the automation to create labels on your issues so you can easily search & filter them.

## What the automation does

- adds labels to issues based on the following predefined fields: `date`, `topic`, `product`, `region`, `stakeholders`
- (optional) assigns newly-created issues to project boards and sets field values
- (optional) notifies supervisors (or whoever you want to triage your issues) based on the issue's `region` field
  - you can change the assignments to be based on a different field, such as `product`, by editing `notify_supervisors` and `SUPERVISORS_BY_REGION` inside `.github/workflows/taskeract/utils.py`
- adds a "DRI" field to the **_body_** of the issue
  - this field does not appear until **_after_** the issue has been created, because the people _requesting_ the work should not necessarily _assign_ the work
  - once filled out, the DRI will be automatically added as an assignee
- adds the label "not planned" to issues closed as not planned

## How to use this repo

1. Copy all files from the `.github` folder into your own repository's `.github` folder (or fork this repo if starting fresh)

1. In your repository, go to Settings > Actions > General and set "Workflow permissions" to "Read and write permissions". If this is too permissive, you can instead create a PAT under Secrets, and edit all `tesseract-*.yml` workflows to use that secret instead of `secrets.GITHUB_TOKEN``

1. In your repository, [create the following labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels#creating-a-label): `TASK: generic`,`TASK: blogpost`,`TASK: video`
    - pick any colors you prefer
    - if you have changed the issue templates, create the labels defined in their "labels:" array instead.

1. Inside `.github/workflows/taskeract-created.yml` and `taskeract-edited.yml`, change `REPOSITORY_NAME` to be your new repository

1. If you want to notify regional supervisors when new issues are created, add their handles to `SUPERVISORS_BY_REGION` inside `.github/workflows/taskeract/utils.py`

1. Decide whether to use the Project Board automation available in this tool. While [Project Boards](https://docs.github.com/en/issues/planning-and-tracking-with-projects) provide a [native mechanism](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/adding-items-automatically) for auto-adding issues to projects, Taskeract gives you a bit more control over which issues are added, and allows you to set field values as you do.
    - If you'll be using Taskeract's board automation:
      - [create a secret](https://github.com/settings/tokens) in your repo called `ADD_TO_PROJECT_PAT` which contains a token capable of editing any project boards you'll be adding issues to (usually, a "classic"" token with "Full control of private repositories" and "Full control of projects")
      - change the project URLs and field values in the "add to project and set project fields" section of `.github/workflows/taskeract-created.yml`
    - If you _won't_ be using Project Boards, or you'll be using their native mechanism for adding issues:
      - delete the section under "add to project and set project fields" in `.github/workflows/taskeract-created.yml`

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
  - if you'll be creating a new label from this field, be sure to add a `LABEL_PREFIX_[fieldname] = '[fieldname]: '` (the trailing space is mandatory) near the top of `utils.py`, and another entry inside `LABEL_COLORS` just below it.

## Adding a new task type

First, add a new issue template.

- for the automation to work, it **_must_** have a label starting with `TASK: ` such as `labels: ["TASK: workshop"]` (the space is mandatory)
- don't forget to [create the label in your repo](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels#creating-a-label) as well

Next, add a new `field-mapping-[TYPE].json` file inside `.github/workflows/taskeract/`

- its content should be an array of field/variable maps (see `field-mapping-video.json` as an example)
- the "field" value should exactly match the "label" value from the issue template
- the "variable" should be a new unique value (preferably [snake_case](https://en.wikipedia.org/wiki/Snake_case))

Lastly, add any project assignments or field values needed to `.github/workflows/taskeract-created.yml` under "add to project and set project fields"

Note that unused task types can be safely removed by simply deleting their issue template and associated "field-mapping-[TYPE].json" file
