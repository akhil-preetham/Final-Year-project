"""Evaluate the recorded CARDIODIAG real-world-readiness gates."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

from cardiodiag.readiness import ReadinessLedgerError, evaluate_readiness

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "docs" / "real_world_readiness_gates.json"
DEFAULT_OUTPUT = ROOT / "results" / "REAL_WORLD_READINESS_REPORT.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()
    try:
        ledger_bytes = args.ledger.read_bytes()
        ledger = json.loads(ledger_bytes)
        report = evaluate_readiness(ledger, ROOT)
    except (OSError, json.JSONDecodeError, ReadinessLedgerError) as exc:
        parser.error(str(exc))
    report["ledger_sha256"] = sha256(ledger_bytes).hexdigest()
    report["evaluated_utc"] = datetime.now(UTC).isoformat()
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"CARDIODIAG real-world readiness: {report['decision']}")
        print(f"Passed phases: {report['passed_count']}/{report['phase_count']}")
        print(f"Open phases: {', '.join(report['open_phase_ids'])}")
        for phase in report["phases"]:
            print(f"- {phase['id']} {phase['name']}: {phase['recorded_status']}")
        try:
            display_path = output_path.relative_to(ROOT)
        except ValueError:
            display_path = output_path
        print(f"Evidence-hashed report: {display_path}")
        print(report["scope_note"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
