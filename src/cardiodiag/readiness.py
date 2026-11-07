"""Fail-closed evaluation of documented real-world-readiness gates."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any

ALLOWED_STATUSES = {"passed", "partial", "blocked", "not_started"}


class ReadinessLedgerError(ValueError):
    """Raised when a readiness ledger is malformed or references unsafe paths."""


def evaluate_readiness(ledger: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Return a fail-closed readiness decision and per-phase evidence status.

    The ledger is a record of human-reviewed gates. This function checks its
    structure and that referenced evidence paths exist; it does not validate
    clinical, statistical, ethical, or regulatory conclusions in those files.
    """
    if ledger.get("schema_version") != 1:
        raise ReadinessLedgerError("Unsupported readiness ledger schema_version")
    phases = ledger.get("phases")
    if not isinstance(phases, list) or not phases:
        raise ReadinessLedgerError("Readiness ledger must contain a non-empty phases list")

    root = repo_root.resolve()
    seen_ids: set[str] = set()
    results: list[dict[str, Any]] = []
    errors: list[str] = []

    for phase in phases:
        if not isinstance(phase, dict):
            raise ReadinessLedgerError("Each phase must be an object")
        phase_id = phase.get("id")
        name = phase.get("name")
        accountable_role = phase.get("accountable_role")
        status = phase.get("status")
        target = phase.get("target")
        evidence_paths = phase.get("evidence_paths")
        if not all(
            isinstance(value, str) and value.strip()
            for value in (phase_id, name, accountable_role, target)
        ):
            raise ReadinessLedgerError(
                "Each phase needs non-empty id, name, accountable_role, and target strings"
            )
        if phase_id in seen_ids:
            raise ReadinessLedgerError(f"Duplicate phase id: {phase_id}")
        seen_ids.add(phase_id)
        if status not in ALLOWED_STATUSES:
            raise ReadinessLedgerError(f"Invalid status for {phase_id}: {status}")
        if not isinstance(evidence_paths, list) or not evidence_paths:
            raise ReadinessLedgerError(f"Phase {phase_id} needs at least one evidence path")
        blockers = phase.get("blockers", [])
        if not isinstance(blockers, list) or any(
            not isinstance(blocker, str) for blocker in blockers
        ):
            raise ReadinessLedgerError(f"Invalid blockers list for {phase_id}")

        missing: list[str] = []
        evidence: list[dict[str, str]] = []
        for relative_path in evidence_paths:
            if not isinstance(relative_path, str) or not relative_path.strip():
                raise ReadinessLedgerError(f"Invalid evidence path in phase {phase_id}")
            candidate = (root / relative_path).resolve()
            try:
                candidate.relative_to(root)
            except ValueError as exc:
                raise ReadinessLedgerError(
                    f"Evidence path escapes repository root in {phase_id}: {relative_path}"
                ) from exc
            if not candidate.is_file():
                missing.append(relative_path)
            else:
                evidence.append(
                    {
                        "path": relative_path,
                        "sha256": sha256(candidate.read_bytes()).hexdigest(),
                    }
                )

        passed = status == "passed" and not missing and not blockers
        results.append(
            {
                "id": phase_id,
                "name": name,
                "accountable_role": accountable_role,
                "recorded_status": status,
                "passed": passed,
                "missing_evidence": missing,
                "evidence": evidence,
                "blockers": blockers,
            }
        )
        if missing:
            errors.append(f"{phase_id} missing evidence: {', '.join(missing)}")

    conditions_met = all(result["passed"] for result in results)
    derived_decision = "READY" if conditions_met else "NO_GO"
    declared_decision = ledger.get("current_decision")
    decision_matches = declared_decision == derived_decision
    ready = conditions_met and decision_matches and declared_decision == "READY"
    open_phases = [result["id"] for result in results if not result["passed"]]
    return {
        "project": ledger.get("project", "unknown"),
        "decision": "READY" if ready else "NO_GO",
        "declared_decision": declared_decision,
        "ledger_decision_matches": decision_matches,
        "all_phase_conditions_met": conditions_met,
        "real_world_ready": ready,
        "phase_count": len(results),
        "passed_count": sum(result["passed"] for result in results),
        "open_phase_ids": open_phases,
        "errors": errors,
        "phases": results,
        "scope_note": (
            "This checker validates ledger structure, evidence-file existence, and hashes; "
            "it does not judge evidence content or replace human clinical, statistical, "
            "ethics, security, or regulatory review."
        ),
    }
