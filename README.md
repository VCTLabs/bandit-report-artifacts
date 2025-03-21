[![Test](https://github.com/VCTLabs/bandit-report-artifacts/actions/workflows/test.yml/badge.svg)](https://github.com/VCTLabs/bandit-report-artifacts/actions/workflows/test.yml)
[![Security check - Bandit](https://github.com/VCTLabs/bandit-report-artifacts/actions/workflows/bandit.yml/badge.svg)](https://github.com/VCTLabs/bandit-report-artifacts/actions/workflows/bandit.yml)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)


This <a href="https://github.com/features/actions">GitHub Action</a> runs
bandit checks on your code and annotates the workflow with any
reported issues.

The action is run in the workflow:

![](assets/screenshot-jobs.png)

A list of all issues is shown in the Workflow

![](assets/screenshot-issues.png)

If an issue is found in the changed files, the affected LoC are shown in
 the PR:

![](assets/screenshot-code.png)


## Usage

To add this Github action to your repository, write a short workflow such
 as the following, eg:


```yml
name: Security check - Bandit

on:
  push:

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
    - uses: actions/checkout@v4

    - name: Run bandit
      uses: VCTLabs/bandit-report-artifacts@master
      with:
        project_path: .
        ignore_failure: true

    # This is optional
    - name: Security check report artifacts
      uses: actions/upload-artifact@v2
      with:
        name: Security report
        path: output/security_report.txt
```


### Getting Started :airplane:

You can include the action in your workflow to trigger on any event that
 [GitHub actions supports](https://help.github.com/en/articles/events-that-trigger-workflows).
 If the remote branch that you wish to deploy to doesn't already exist the action will create it for you.
 Your workflow will also need to include the `actions/checkout` step before this workflow runs
 in order for the deployment to work.


If you'd like to make it so the workflow only triggers on push events
 to specific branches then you can modify the `on` section.

```yml
on:
  push:
    branches:
      - master
```

### Configuration 📁

The `with` portion of the workflow **must** be configured before the action will work.
 You can add these in the `with` section found in the examples above.
 Any `secrets` must be referenced using the bracket syntax and stored
 in the GitHub repositories `Settings/Secrets` menu.
 You can learn more about setting environment variables
 with GitHub actions [here](https://help.github.com/en/articles/workflow-syntax-for-github-actions#jobsjob_idstepsenv).

#### Required Setup

Use any of the following deployment options to configure the workflow;
note the last two options are mutually exclusive, ie, use only one of
`exclude_paths` or `config_file`.

| Key                | Value Information                                                                                                                                                                                                                                                                                                                                     | Type   | Required | Default |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | -------- | -------- |
| `PROJECT_PATH` | To provide your python location at which this security check needed to be done.                                                                                             | `with` | **No**  | "." |
| `IGNORE_FAILURE` | This is to ignore the security failures and pass the check.                                                                                                 | `with` | **No**  | false |
| `EXCLUDE_PATHS` | A comma separated string of exclude paths. By default, no exclude paths are used.                                                                         | `with` | **No**  | "" |
| `CONFIG_FILE` | An optional config file. By default, no file is used.                                                                                                 | `with` | **No**  | "" |


---


#### Bandit report (security checks report) 👮‍♂️

The following is a bandit report for a django project.
[learn more about bandit](https://pypi.org/project/bandit/).

```txt
Run started:2020-03-22 18:12:42.386731

Test results:
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: '(2h1-*yec9^6xz6y920vco%zdd+!7m6j6$!gi@)3amkbduup%d'
   Severity: Low   Confidence: Medium
   Location: ./sample_project/settings.py:25
   More Info: https://bandit.readthedocs.io/en/latest/plugins/b105_hardcoded_password_string.html
24      # SECURITY WARNING: keep the secret key used in production secret!
25      SECRET_KEY = "(2h1-*yec9^6xz6y920vco%zdd+!7m6j6$!gi@)3amkbduup%d"
26
27      # SECURITY WARNING: don't run with debug turned on in production!
28      DEBUG = True

--------------------------------------------------

Test results:
        No issues identified.

Code scanned:
        Total lines of code: 138
        Total lines skipped (#nosec): 0

Run metrics:
        Total issues (by severity):
                Undefined: 0.0
                Low: 0.0
                Medium: 0.0
                High: 0.0
        Total issues (by confidence):
                Undefined: 0.0
                Low: 0.0
                Medium: 0.0
                High: 0.0
Files skipped (0):
```

This can be achieved by adding the following to your job.

```yml
    - name: Security check report artifacts
      uses: actions/upload-artifact@v1
      # if: failure()
      with:
        name: Security report
        path: output/security_report.txt
```

### License 👨🏻‍💻

The Dockerfile and associated scripts and documentation in this project
are released under the [MIT License](LICENSE).

Container images built with this project include third party materials.
As with all Docker images, these likely also contain other software which
may be under other licenses. It is the image user's responsibility to ensure
that any use of this image complies with any relevant licenses for all
software contained within.
