"""Failure-isolated, resource-bounded parallel model execution."""

from __future__ import annotations

import json
import os
import threading
import time
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, wait
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class ExecutionRecord:
    """Serializable record for one attempted candidate job."""

    name: str
    status: str
    attempt: int
    elapsed_seconds: float = 0.0
    error_type: str | None = None
    error_message: str | None = None
    result: dict[str, Any] | None = None
    memory_mb: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ParallelExecutionEngine:
    """Run independent candidate jobs concurrently with checkpoints.

    The default thread backend is portable on Windows and allows estimators
    whose native implementations release the GIL to run concurrently.  Each
    candidate is configured single-threaded by the registry, so the outer
    ``max_workers`` is the resource control.  Timeouts are soft for running
    threads: completed work is isolated, cancelled pending work is skipped, and
    the checkpoint records the timeout request.
    """

    def __init__(
        self,
        max_workers: int | None = None,
        timeout_seconds: float | None = None,
        retries: int = 0,
        checkpoint_path: str | Path | None = None,
    ) -> None:
        if retries < 0:
            raise ValueError("retries must be non-negative")
        self.max_workers = max_workers or max(1, min(4, (os.cpu_count() or 2) // 2))
        self.timeout_seconds = timeout_seconds
        self.retries = retries
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else None
        self._checkpoint_lock = threading.Lock()

    def run(
        self,
        jobs: dict[str, Callable[[], dict[str, Any]]],
    ) -> tuple[dict[str, dict[str, Any]], list[ExecutionRecord]]:
        """Execute jobs and return successful results plus all execution records."""

        results: dict[str, dict[str, Any]] = {}
        records: list[ExecutionRecord] = []
        pending_jobs = dict(jobs)
        for attempt in range(self.retries + 1):
            if not pending_jobs:
                break
            executor = ThreadPoolExecutor(
                max_workers=self.max_workers, thread_name_prefix="clin-adapt"
            )
            started = {name: time.perf_counter() for name in pending_jobs}
            futures: dict[Future[dict[str, Any]], tuple[str, int]] = {
                executor.submit(job): (name, attempt) for name, job in pending_jobs.items()
            }
            pending = set(futures)
            retry_names: set[str] = set()
            while pending:
                done, pending = wait(pending, timeout=0.1)
                for future in done:
                    name, job_attempt = futures[future]
                    elapsed = time.perf_counter() - started[name]
                    try:
                        result = future.result()
                    except Exception as exc:  # candidate failure must not abort peers
                        record = ExecutionRecord(
                            name=name,
                            status="failed",
                            attempt=job_attempt,
                            elapsed_seconds=elapsed,
                            error_type=type(exc).__name__,
                            error_message=str(exc),
                        )
                        retry_names.add(name)
                    else:
                        results[name] = result
                        record = ExecutionRecord(
                            name=name,
                            status="completed",
                            attempt=job_attempt,
                            elapsed_seconds=elapsed,
                            result=_compact_result(result),
                            memory_mb=_process_memory_mb(),
                        )
                    records.append(record)
                    self._write_checkpoint(results, records)
                if self.timeout_seconds is not None:
                    overdue = [
                        future
                        for future in pending
                        if time.perf_counter() - started[futures[future][0]] > self.timeout_seconds
                    ]
                    for future in overdue:
                        name, job_attempt = futures[future]
                        future.cancel()
                        pending.remove(future)
                        retry_names.add(name)
                        records.append(
                            ExecutionRecord(
                                name=name,
                                status="timeout_requested",
                                attempt=job_attempt,
                                elapsed_seconds=time.perf_counter() - started[name],
                                error_type="TimeoutError",
                                error_message=(
                                    "soft timeout exceeded; running thread may finish in background"
                                ),
                            )
                        )
                        self._write_checkpoint(results, records)
            executor.shutdown(wait=False, cancel_futures=True)
            pending_jobs = {name: jobs[name] for name in retry_names if name not in results}
        return results, records

    def _write_checkpoint(
        self, results: dict[str, dict[str, Any]], records: list[ExecutionRecord]
    ) -> None:
        if self.checkpoint_path is None:
            return
        payload = {
            "status": "checkpoint",
            "results": {name: _compact_result(result) for name, result in results.items()},
            "records": [record.to_dict() for record in records],
        }
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.checkpoint_path.with_suffix(self.checkpoint_path.suffix + ".tmp")
        with self._checkpoint_lock:
            temporary.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
            temporary.replace(self.checkpoint_path)


def _compact_result(result: dict[str, Any]) -> dict[str, Any]:
    """Keep checkpoints JSON-safe without discarding the full in-memory result."""

    compact: dict[str, Any] = {}
    for key, value in result.items():
        if key in {"predictions", "oof_predictions"}:
            continue
        try:
            json.dumps(value, allow_nan=False)
        except (TypeError, ValueError):
            compact[key] = str(value)
        else:
            compact[key] = value
    return compact


def _process_memory_mb() -> float | None:
    try:
        import psutil

        return float(psutil.Process().memory_info().rss / (1024 * 1024))
    except (ImportError, AttributeError, OSError):
        return None
