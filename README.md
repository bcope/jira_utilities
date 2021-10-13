# Jira Utilities

<!-- TOC -->

- [Overview](#overview)
- [Running the container](#running-the-container)
- [Assumptions](#assumptions)
  - [Environment variables](#environment-variables)
- [Plans](#plans)
  - [Main script to handle calls to other scripts](#main-script-to-handle-calls-to-other-scripts)
  - [Jira client class](#jira-client-class)
  - [Group membership management](#group-membership-management)
  - [Team membership management](#team-membership-management)
  - [Team / Group sync script](#team--group-sync-script)
  - [Bulk edit Issue sprints to multiple sprints determined by Board](#bulk-edit-issue-sprints-to-multiple-sprints-determined-by-board)
  - [Sprint management script](#sprint-management-script)
  - [Board Quick Filter management](#board-quick-filter-management)
- [Ideas](#ideas)
  - [Fastmail Calendar Integration](#fastmail-calendar-integration)
- [Contribution](#contribution)

<!-- /TOC -->

## Overview

Contains utility scripts useful for Jira administrators and power users.

## Assumptions

### Docker

This code is run in a Python 3.7 Docker container. You will need Docker installed locally.

### Environment variables

- JIRA_USER
- JIRA_API_TOKEN
- JIRA_URL

## Running the container

```sh
docker run --rm -e JIRA_USER=$JIRA_USER -e JIRA_API_TOKEN=$JIRA_API_TOKEN -e JIRA_URL=$JIRA_URL jira_utilities
# add required arguments for main.py
```

## Plans

Sections here are currently planned to be implemented.

### Main script to handle calls to other scripts

The users will be able to execute any of the underlying scripts through the primary Docker entrypoint.

### Jira client class

This will house any generic logic for interacting with the API.

### Group membership management

This will enable a user to add or remove Users to/from a Group.

### Team membership management

This will enable a user to add or remove Users to/from a Team.

### Team / Group sync script

This will enable a user to automatically keep a Group and Team's membership in sync. Using a config file to map the relationship between Groups and Teams, the user can automatically detect when they are out of sync. The config file will specify the sync direction.

### Bulk edit Issue sprints to multiple sprints determined by Board

This will enable a user to automatically edit the sprint value of issues based on JQL filter criteria associated with a Board saved in a config file. This filter criteria should be mutually exclusive as it will be evaluated sequentially and issues appearing in multiple criteria will have their sprint value updated multiple times (only the last matching criteria will be used).

### Sprint management script

This will enable a user to automatically create sprints in bulk based on a config file. The config file will enable a user to specify a Board and a typical sprint duration. The script will enable the user to check to see if a sprint exists for a passed date or date range, create a sprint with a standardized name format if none exists, and then return the full list of sprints for the time period.

### Board Quick Filter management

This will enable a user to automatically create Quick Filters on a Board based on a config file.

## Ideas

Sections here may be explored and evaluated for possible implementation

### Fastmail Calendar Integration

This needs further requirement definition.

[Stack Overflow](https://stackoverflow.com/questions/53029743/access-fastmail-caldav-with-python)

## Contribution

It probably makes sense to reach out with your idea via an issue first, but if you're okay shooting in the dark feel free to just follow this procedure:

- Create a feature branch
- Follow the style guide recommendations [here](https://github.com/bcope/style_guides/)
- Put in PR for review
