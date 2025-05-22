# Project Hours Logger CLI

## Overview

The Project Hours Logger CLI application is a command-line tool designed to help you track and manage the hours worked on various projects. It provides functionality for logging work sessions, summarizing work hours, and viewing detailed entries for specific periods.

## Features

- **Add Project**: Create new projects with a name and code.
- **List Projects**: View a list of all available projects.
- **Start Work**: Begin a work session on a specified project, with optional custom start time.
- **Stop Work**: End the current session and log the entry.
- **Summary**: Generate summaries of hours worked for various periods, including daily entries, weekly summaries, and project-specific summaries.
- **Today's Entries**: View all work entries for today in chronological order, including total hours worked.

## Usage

Below are examples of how to use the various commands provided by the CLI:

### Adding a Project

To add a new project, use:
```bash
python spacetime.py add_project <project_name> <project_code>
```
### Listing All Projects

To list all projects, use:

```bash

python spacetime.py list_projects
```
### Starting Work on a Project

To start working on a project, use:

```bash

python spacetime.py start <project_code> [--time HH:MM]
```
`--time HH:MM` is optional and specifies a custom start time.
### Stopping Work

To stop the current session and log the entry, use:

```bash

python spacetime.py stop
```
### Viewing Today's Entries

To view all entries for today, use:

```bash

python spacetime.py summary overall today
```
### Generating Summaries

To generate summaries for specific periods, use:

```bash

python spacetime.py summary overall <period>
```
`<period>` can be this_week, last_week, this_month, last_month, this_year, or today.

### To view project-specific summaries, use:

```bash

python spacetime.py summary project <period>
```
`<period>` can be this_week, last_week, this_month, last_month, or this_year.
### Requirements
- Python 3.x: Ensure you have Python 3 installed on your system.
- Dependencies: Standard Python libraries such as argparse, csv, and datetime are used. No additional installations are required.
- Installation
Clone the repository to your local machine.
Navigate to the directory containing the script.
License
