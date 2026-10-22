import json
from pathlib import Path

import pytest

from devcheck.diagnostics import load_config, run_diagnostics


def test_success_report_has_four_checks(monkeypatch, tmp_path):
    monkeypatch.setattr("devcheck.diagnostics.check_python", lambda: {"name": "python_version", "status": "pass", "message": "ok", "details": {}})
    monkeypatch.setattr("devcheck.diagnostics.check_disk", lambda path: {"name": "disk_space", "status": "pass", "message": "ok", "details": {}})
    monkeypatch.setattr("devcheck.diagnostics.check_environment", lambda required: {"name": "environment_variables", "status": "pass", "message": "ok", "details": {}})
    monkeypatch.setattr("devcheck.diagnostics.check_tools", lambda tools: {"name": "developer_tools", "status": "pass", "message": "ok", "details": {}})
    report = run_diagnostics({"required_env": ["PATH"], "tools": ["git"], "disk_path": str(tmp_path)})
    assert report["overall_status"] == "pass"
    assert report["summary"] == {"total": 4, "passed": 4, "failed": 0}
    assert len(report["checks"]) == 4


def test_missing_dependency_is_reported(monkeypatch):
    monkeypatch.setattr("devcheck.diagnostics.shutil.which", lambda name: None)
    from devcheck.diagnostics import check_tools
    result = check_tools(["tool-that-is-not-installed"])
    assert result["status"] == "fail"
    assert result["details"]["missing"] == ["tool-that-is-not-installed"]


def test_malformed_configuration_path(tmp_path):
    missing = tmp_path / "does-not-exist.json"
    with pytest.raises(ValueError, match="does not exist"):
        load_config(missing)


def test_invalid_json_configuration(tmp_path):
    config = tmp_path / "bad.json"
    config.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid configuration"):
        load_config(config)


def test_config_validates_types(tmp_path):
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"required_env": "PATH"}), encoding="utf-8")
    with pytest.raises(ValueError, match="required_env"):
        load_config(config)
