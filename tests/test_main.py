import json
from pathlib import Path
from main import bandit_annotations, run_bandit, bandit_run_check, bandit_error


def test_errors():
    results = json.loads(Path("tests/bandit.error.json").read_text())
    errors = [bandit_error(error) for error in results["errors"]]
    assert len(errors) == 2
    assert errors[0]["path"] == "LICENSE"
    assert errors[1]["path"] == "tests/py2.py"
    assert errors[1]["annotation_level"] == "failure"
    assert (
        errors[1]["title"] == "invalid syntax"
        or "Missing parentheses in call to 'print'. Did you mean print(...)?"
    )


def test_annotations():
    results = json.loads(Path("tests/bandit.json").read_text())
    annotations = bandit_annotations(results)
    assert annotations[0]["path"] == "canary.py"
    assert annotations[0]["start_line"] == 3


def test_run_bandit():
    results = run_bandit(["canary.py"])
    assert "results" in results


def test_run_check():
    results = json.loads(Path("tests/bandit.json").read_text())
    run_check_body = bandit_run_check(results)
    assert run_check_body["conclusion"] == "failure"
