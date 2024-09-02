# Clerks Friend


<p>
    <a href="https://clerks-friend.readthedocs.io/en/stable/">
        <img src="https://img.shields.io/readthedocs/clerks-friend"/>
    </a>
    <a href="https://pypi.org/project/clerks-friend/">
        <img src="https://img.shields.io/pypi/v/clerks-friend"/>
    </a>
    <a href="https://pypi.org/project/clerks-friend/">
        <img src="https://img.shields.io/pypi/wheel/clerks-friend"/>
    </a>
    <a href="https://pypi.org/project/clerks-friend/">
        <img src="https://img.shields.io/pypi/pyversions/clerks-friend"/>
    </a>
    <a href="https://github.com/IsaacsLab42/clerks_friend/">
        <img src="https://img.shields.io/github/license/IsaacsLab42/clerks_friend"/>
    </a>
    <a href="https://black.readthedocs.io/en/stable/">
        <img src="https://img.shields.io/badge/code_style-black-black"/>
    </a>
</p>

---

Useful reports for Ward Clerk's of The Church of Jesus Christ of Latter-Day Saints. The
included script `clerks_friend` can run several useful reports and produce Markdown
style output. This output could be used by various programs to create HTML or PDF
output. Or, the way I use it, is to paste the markdown into Google Docs. They have a
feature where markdown can be pasted into a Google Doc and it will render the output.

## Command Line Script

This package installs a command line script called `clerks_friend`:

```bash
$ clerks_friend --help
usage: clerks_friend [-h] [-u USERNAME] [-p PASSWORD] [-c COOKIE_FILE]
                     [-o MARKDOWN_OUTPUT]
                     INPUT_FILE

Run clerk reports from LCR for The Church of Jesus Christ of Latter-Day
Saints.

positional arguments:
  INPUT_FILE            input YAML file containing the report
                        configuration

options:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        LCR username [env var: LCR_USERNAME]
  -p PASSWORD, --password PASSWORD
                        LCR password [env var: LCR_PASSWORD]
  -c COOKIE_FILE, --cookie-file COOKIE_FILE
                        cookie jar file to save the session or load a
                        saved session
  -o MARKDOWN_OUTPUT, --output MARKDOWN_OUTPUT
                        output file for markdown report. Defaults to
                        stdout.
```

## Authentication

The `clerks_friend` script requires your member username and password, for The Church of
Jesus Christ of Latter-Day Saints LCR system. There are three different ways to supply
these credentials:

1. On the command line, using the `--username` and `--password` options.
2. Through the environment variables `LCR_USERNAME` and `LCR_PASSWORD`.
3. From an environment file `.env`. This is the recommended option.

The `.env` file must be in the same directory that the script is run from. The file format is very simple:

```
LCR_USERNAME=ace
LCR_PASSWORD=ThePassword
```

## Report File Input

The input file, specifying which reports to run and their parameters, is a YAML file
format. As example is shown below:

```yaml
---
title: Celestial Ward Clerical Report

reports:
  - name: not_set_apart
    heading: Not Set Apart

  - name: expiring_recommends
    heading: "Expiring/Expired Temple Recommends"
    parameters:
      months_past: -3
      months_future: 1
      recommend_type: REGULAR

  - name: protecting_children_and_youth_training
    heading: Protecting Children and Youth Training
    parameters:
      months_future: 1

  - name: sacrament_meeting_attendance
    heading: Sacrament Meeting Attendance
    parameters:
      year: 2024
```

## Valid Reports

The currently valid report types are:

* not_set_apart
* expiring_recommends
* protecting_children_and_youth_training
* sacrament_meeting_attendance

As time permits I would like to add additional reports. If you would like to help add
more reports then please feel free to open a pull request, or an issue describing the
report you'd like.


## Cached Sessions

This script uses the [lcr_session](https://github.com/IsaacsLab42/lcr_session) library
to provide authentication. This library can also cache sessions, so that
re-authentication is not necessary if several reports need to be run in a row. For this
use the `--cookie-file` option. Church sessions are typically valid for one hour.


## Example

For example, save the above YAML sample as `report.yaml`. Create a `.env` file with your
LCR credentials, then run the following:

```bash
$ clerks_friend ./report.yaml -c cookies.txt -o report.md
```

A `report.md` file would be output with the results. This could then be copied and
pasted into a Google Document, which would render the markdown properly. Note that
markdown support must be enabled for the document, and you must select the "Paste from
markdown" option.
