"""Bandit report action."""

import json

from ast import parse
from datetime import datetime, timezone
from os import environ
from pathlib import Path
from subprocess import (  # nosec - module is used cleaning environment variables and with shell=False
    run,
)

import requests


def gh_req(url, method="GET", data=None, headers=None, token=None):
    """Make a github API request."""
    headers = dict(
        headers or {}, **{"Accept": "application/vnd.github.antiope-preview+json"}
    )
    if token:
        headers["Authorization"] = f"token {token}"
    return requests.request(
        method=method, url=url, headers=headers, data=data, timeout=(2, 5),
    )


def to_gh_severity(bandit_severity):
    """
    Maps bandit severity to github annotation_level.

    see: https://docs.github.com/en/rest/reference/checks#create-a-check-run
    """
    bandit_severity = bandit_severity.lower()
    bandit_severity_map = {
        "low": "notice",
        "medium": "warning",
        "high": "failure",
        "undefined": "notice",
    }
    return bandit_severity_map[bandit_severity]


def run_bandit(args, env=None):
    """Control environment variables passed to bandit."""
    my_args = ["bandit", "-f", "json"] + args
    out = run(
        my_args,
        check=False,
        shell=False,
        capture_output=True,
        env=env or {"PATH": environ["PATH"]},
    )  # nosec - this input cannot execute different commands.
    if out.returncode < 2:
        # Everything ok
        return json.loads(out.stdout)
    raise SystemExit(out.stderr)


def bandit_annotation(result):
    """Parse a single result and extract annotation."""
    try:
        end_line = result["line_range"][-1]
    except (KeyError, IndexError):
        end_line = result["line_number"]

    data = dict(
        path=result["filename"],
        start_line=result["line_number"],
        end_line=end_line,
        annotation_level=to_gh_severity(result["issue_severity"]),
        title="Test: {test_name} id: {test_id}".format(**result),
        message="{issue_text} more info {more_info}".format(**result),
    )

    return data


def bandit_error(error):
    """Parse bandit errors and return a dict."""
    title = "Error processing file (not a python file?)"
    start_line, end_line = 1, 1
    message = error["reason"]
    try:
        parse(Path(error["filename"]).read_text(encoding='utf-8'))
    except SyntaxError as exc:
        title, _ = exc.args  # noqa - need to handle different size tuples
        end_line = start_line = exc.lineno
        message = exc.msg
    except Exception:  # nosec - I really want to ignore further exceptions here.
        # Use default error values
        pass

    return dict(
        path=error["filename"],
        start_line=start_line,
        end_line=end_line,
        annotation_level="failure",
        title=title,
        message=message,
    )


def bandit_annotations(results):
    """Parse results and return a list."""
    return [bandit_annotation(result) for result in results["results"]]


def bandit_run_check(results, github_sha=None, dummy=False):
    """
    Process results for a given hash, return a report including any
    annotations or errors.
    """
    annotations = bandit_annotations(results)
    errors = [bandit_error(e) for e in results["errors"]]
    conclusion = "success"
    title = "Bandit: no issues found"
    name = "Bandit comments"
    summary = (
        f"""Total statistics: {json.dumps(results['metrics']["_totals"], indent=2)}"""
    )

    if errors or annotations:
        conclusion = "failure"
        title = f"Bandit: {len(errors)} errors and {len(annotations)} annotations found"
    if dummy:
        conclusion = "neutral"
        name = "Bandit dummy run"
        title = "Bandit dummy run (always neutral)"

    return {
        "name": name,
        "head_sha": github_sha,
        "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "conclusion": conclusion,
        "output": {
            "title": title,
            "summary": summary,
            "annotations": annotations + errors,
        },
    }


if __name__ == "__main__":
    from sys import argv

    REQUIRED_ENV = {"GITHUB_API_URL", "GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_TOKEN"}
    if not REQUIRED_ENV < set(environ):
        print(
            "Missing one or more of the following environment variables",
            REQUIRED_ENV - set(environ),
        )
        raise SystemExit(1)

    u_patch = "{GITHUB_API_URL}/repos/{GITHUB_REPOSITORY}/commits/{GITHUB_SHA}/check-runs".format(
        **environ
    )
    u_post = "{GITHUB_API_URL}/repos/{GITHUB_REPOSITORY}/check-runs".format(**environ)

    bandit_results = run_bandit(argv[1:], env={"PATH": environ["PATH"]})

    bandit_checks = bandit_run_check(
        bandit_results, environ.get("GITHUB_SHA"), dummy=environ.get("DUMMY_ANNOTATION")
    )
    res = gh_req(
        u_post,
        method="POST",
        data=json.dumps(bandit_checks),
        token=environ["GITHUB_TOKEN"],
    )

    print("Workflow status:", res.status_code, res.json(), res.url)

    if res.status_code >= 300:
        raise SystemExit(1)
