import json
from pathlib import Path

import pytest

from cardiodiag.readiness import ReadinessLedgerError, evaluate_readiness

ROOT = Path(__file__).resolve().parents[1]


def test_current_readiness_ledger_fails_closed_with_existing_evidence():
    ledger = json.loads((ROOT / "docs/real_world_readiness_gates.json").read_text())

    report = evaluate_readiness(ledger, ROOT)

    assert report["decision"] == "NO_GO"
    assert report["real_world_ready"] is False
    assert report["ledger_decision_matches"] is True
    assert report["passed_count"] == 1
    assert "G6" in report["open_phase_ids"]
    assert not report["errors"]
    assert report["phases"][0]["evidence"][0]["sha256"]


def test_all_gates_need_passed_status_and_existing_evidence(tmp_path):
    evidence = tmp_path / "evidence.txt"
    evidence.write_text("reviewed")
    ledger = {
        "schema_version": 1,
        "project": "test",
        "current_decision": "READY",
        "phases": [
            {
                "id": "G0",
                "name": "Gate",
                "accountable_role": "Project lead",
                "status": "passed",
                "target": "Complete",
                "evidence_paths": ["evidence.txt"],
                "blockers": [],
            }
        ],
    }

    report = evaluate_readiness(ledger, tmp_path)

    assert report["real_world_ready"] is True
    assert report["passed_count"] == 1


def test_missing_evidence_prevents_readiness(tmp_path):
    ledger = {
        "schema_version": 1,
        "project": "test",
        "current_decision": "NO_GO",
        "phases": [
            {
                "id": "G0",
                "name": "Gate",
                "accountable_role": "Project lead",
                "status": "passed",
                "target": "Complete",
                "evidence_paths": ["missing.txt"],
                "blockers": [],
            }
        ],
    }

    report = evaluate_readiness(ledger, tmp_path)

    assert report["decision"] == "NO_GO"
    assert report["phases"][0]["missing_evidence"] == ["missing.txt"]


def test_recorded_blocker_prevents_readiness_even_with_passed_status(tmp_path):
    evidence = tmp_path / "evidence.txt"
    evidence.write_text("reviewed")
    ledger = {
        "schema_version": 1,
        "project": "test",
        "phases": [
            {
                "id": "G0",
                "name": "Gate",
                "accountable_role": "Project lead",
                "status": "passed",
                "target": "Complete",
                "evidence_paths": ["evidence.txt"],
                "blockers": ["review remains open"],
            }
        ],
    }

    report = evaluate_readiness(ledger, tmp_path)

    assert report["real_world_ready"] is False
    assert report["ledger_decision_matches"] is False
    assert report["phases"][0]["passed"] is False


def test_evidence_path_cannot_escape_repository_root(tmp_path):
    ledger = {
        "schema_version": 1,
        "project": "test",
        "phases": [
            {
                "id": "G0",
                "name": "Gate",
                "accountable_role": "Project lead",
                "status": "passed",
                "target": "Complete",
                "evidence_paths": ["../outside.txt"],
                "blockers": [],
            }
        ],
    }

    with pytest.raises(ReadinessLedgerError, match="escapes repository root"):
        evaluate_readiness(ledger, tmp_path)


def test_accountable_role_is_required(tmp_path):
    ledger = {
        "schema_version": 1,
        "project": "test",
        "current_decision": "NO_GO",
        "phases": [
            {
                "id": "G0",
                "name": "Gate",
                "status": "blocked",
                "target": "Complete",
                "evidence_paths": ["evidence.txt"],
                "blockers": ["owner unknown"],
            }
        ],
    }

    with pytest.raises(ReadinessLedgerError, match="accountable_role"):
        evaluate_readiness(ledger, tmp_path)
