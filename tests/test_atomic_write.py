"""Tests de la escritura atómica de JSON."""

import json

import pytest

from handy.atomic_write import write_json_atomic


def test_writes_valid_json_without_leaving_tmp(tmp_path):
    target = tmp_path / "config.json"
    write_json_atomic(str(target), {"a": 1, "ñ": "é"}, indent=2)
    assert json.loads(target.read_text(encoding="utf-8")) == {"a": 1, "ñ": "é"}
    assert [p.name for p in tmp_path.iterdir()] == ["config.json"]


def test_replaces_existing_file(tmp_path):
    target = tmp_path / "config.json"
    target.write_text('{"old": true}', encoding="utf-8")
    write_json_atomic(str(target), {"new": True})
    assert json.loads(target.read_text(encoding="utf-8")) == {"new": True}


def test_failure_keeps_original_and_removes_tmp(tmp_path):
    target = tmp_path / "config.json"
    target.write_text('{"old": true}', encoding="utf-8")
    with pytest.raises(TypeError):
        write_json_atomic(str(target), {"bad": object()})
    assert json.loads(target.read_text(encoding="utf-8")) == {"old": True}
    assert [p.name for p in tmp_path.iterdir()] == ["config.json"]
