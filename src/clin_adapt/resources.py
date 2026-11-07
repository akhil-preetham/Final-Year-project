"""Runtime resource detection for CLIN-ADAPT scheduling and provenance."""

from __future__ import annotations

import importlib.util
import os
from typing import Any


def detect_runtime_resources() -> dict[str, Any]:
    """Return a conservative runtime resource snapshot without installation."""

    snapshot: dict[str, Any] = {
        "cpu_logical_count": os.cpu_count() or 1,
        "gpu": {"available": False, "backend": None, "device_count": 0},
        "memory": {"available": False, "total_mb": None, "available_mb": None},
    }
    if importlib.util.find_spec("torch") is not None:
        try:
            import torch

            available = bool(torch.cuda.is_available())
            snapshot["gpu"] = {
                "available": available,
                "backend": "cuda" if available else None,
                "device_count": int(torch.cuda.device_count()) if available else 0,
            }
        except (ImportError, RuntimeError, OSError):
            snapshot["gpu"] = {
                "available": False,
                "backend": None,
                "device_count": 0,
                "detection_error": "torch_runtime_probe_failed",
            }
    if importlib.util.find_spec("psutil") is not None:
        try:
            import psutil

            memory = psutil.virtual_memory()
            snapshot["memory"] = {
                "available": True,
                "total_mb": float(memory.total / (1024 * 1024)),
                "available_mb": float(memory.available / (1024 * 1024)),
            }
        except (ImportError, OSError, AttributeError):
            snapshot["memory"] = {
                "available": False,
                "total_mb": None,
                "available_mb": None,
                "detection_error": "psutil_runtime_probe_failed",
            }
    return snapshot
