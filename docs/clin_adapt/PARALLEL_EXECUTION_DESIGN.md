# CLIN-ADAPT parallel execution design

## Resource model

Each candidate factory is single-threaded. `ParallelExecutionEngine` controls
the outer worker count, defaulting to a conservative fraction of available
CPUs and capped at four unless configured otherwise. This avoids multiplying
native estimator threads by worker count.

## Failure isolation

Each job returns independently. Exceptions become `ExecutionRecord` entries with
candidate, attempt, elapsed time, exception type and message. A failed job does
not cancel successful peers. Optional retry counts are fixed in the experiment
configuration; random seeds are not changed between retries.

## Checkpointing

After every completed or failed job, the engine writes an atomic JSON checkpoint
containing compact results and execution records. Large prediction arrays are
excluded from the checkpoint and remain in the final experiment artifact when
requested. A future recovery command can use the checkpoint to identify jobs
already completed without overwriting historical results.

## Time limits and memory

Timeouts are soft for Python threads: pending jobs can be cancelled, while a
running native estimator may finish in the background. The record therefore says
`timeout_requested`, not falsely claiming termination. RSS memory is recorded
when `psutil` is installed; absence of `psutil` is represented as null.

GPU detection and GPU scheduling are not implemented in v0.1 because the active
environment has no PyTorch/GPU model stack. GPU candidates remain explicit
unavailable registry records.

## Observed cycle

| Run | Workers | Jobs | Completed | Runtime |
|---|---:|---:|---:|---:|
| Heart5 full portfolio | 4 | 60 | 60 | 31.97 s |
| Mendeley full portfolio | 4 | 60 | 60 | 37.46 s |
| 70K priority portfolio | 3 | 12 | 12 | 34.85 s |

These are wall-clock measurements from the stored artifacts and are not a
hardware-independent speed claim.
