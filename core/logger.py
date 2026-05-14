# =========================================================
# core/logger.py — Centralized JSON session logger (singleton)
# =========================================================

import json
import sys
import os
import platform
import threading
import traceback as _tb
from datetime import datetime, timezone
from pathlib import Path

try:
    import psutil as _psutil
    _PSUTIL_OK = True
except ImportError:
    _PSUTIL_OK = False

_MAX_BYTES = 5 * 1024 * 1024   # 5 MB
_RETENTION_DAYS = 30
_PROJECT_ROOT = Path(__file__).parent.parent
_LOGS_DIR = _PROJECT_ROOT / "Logs"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _app_version() -> str:
    try:
        p = _PROJECT_ROOT / "Settings" / "settings_default.json"
        with open(p, encoding="utf-8") as f:
            return str(json.load(f).get("version", "0.1"))
    except Exception:
        return "0.1"


def _ram_gb():
    if _PSUTIL_OK:
        try:
            return round(_psutil.virtual_memory().total / (1024 ** 3), 2)
        except Exception:
            pass
    return None


class _Logger:
    _instance = None
    _class_lock = threading.Lock()

    def __init__(self):
        self._lock = threading.Lock()
        self._events = []
        self._part = 1
        self._warnings = 0
        self._errors = 0
        self._ops_completed = 0
        self._session_start = datetime.now(timezone.utc)

        _LOGS_DIR.mkdir(exist_ok=True)
        self._purge_old()

        ts = self._session_start.strftime("%Y-%m-%d_%H-%M-%S")
        self._session_id = ts
        self._log_path = _LOGS_DIR / f"{ts}_session.json"
        self._header = self._build_header()
        self._flush()

    # ── Internal helpers ──────────────────────────────────────────

    def _build_header(self) -> dict:
        return {
            "session_id": self._session_id,
            "session_start": self._session_start.isoformat(timespec="milliseconds"),
            "session_end": None,
            "system_info": {
                "app_version": _app_version(),
                "python_version": sys.version.split()[0],
                "os": f"{platform.system()} {platform.release()}",
                "os_version": platform.version(),
                "machine": platform.machine(),
                "cpu": platform.processor(),
                "ram_gb": _ram_gb(),
            },
            "events": [],
        }

    def _purge_old(self):
        cutoff = datetime.now(timezone.utc).timestamp() - _RETENTION_DAYS * 86400
        for f in _LOGS_DIR.glob("*_session*.json"):
            try:
                if f.stat().st_mtime < cutoff:
                    f.unlink()
            except Exception:
                pass

    def _flush(self):
        doc = dict(self._header)
        doc["events"] = self._events
        try:
            with open(self._log_path, "w", encoding="utf-8") as fh:
                json.dump(doc, fh, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _rotate_if_needed(self):
        try:
            if self._log_path.exists() and self._log_path.stat().st_size >= _MAX_BYTES:
                self._part += 1
                self._log_path = _LOGS_DIR / f"{self._session_id}_session_part{self._part}.json"
                self._events = []
                self._header = self._build_header()
        except Exception:
            pass

    def _append(self, event: dict):
        with self._lock:
            level = event.get("level")
            if level == "WARNING":
                self._warnings += 1
            elif level == "ERROR":
                self._errors += 1
            if event.get("event_type") == "operation" and event.get("status") == "SUCCESS":
                self._ops_completed += 1
            self._rotate_if_needed()
            self._events.append(event)
            self._flush()

    @staticmethod
    def _make_event(level, event_type, module, function, msg,
                    status=None, duration_ms=None, api_latency_ms=None,
                    context=None, correlation_id=None, error_code=None,
                    error_category=None, is_retryable=None, traceback=None) -> dict:
        return {
            "time": _now_iso(),
            "level": level,
            "event_type": event_type,
            "correlation_id": correlation_id,
            "module": module,
            "function": function,
            "msg": msg,
            "status": status,
            "duration_ms": duration_ms,
            "api_latency_ms": api_latency_ms,
            "context": context or {},
            "error_code": error_code,
            "error_category": error_category,
            "is_retryable": is_retryable,
            "traceback": traceback,
        }

    # ── Public API ────────────────────────────────────────────────

    def info(self, module, function, msg, context=None, correlation_id=None):
        self._append(self._make_event(
            "INFO", "lifecycle", module, function, msg,
            context=context, correlation_id=correlation_id,
        ))

    def warning(self, module, function, msg, context=None, correlation_id=None):
        self._append(self._make_event(
            "WARNING", "lifecycle", module, function, msg,
            context=context, correlation_id=correlation_id,
        ))

    def error(self, module, function, msg, error_code, error_category,
              is_retryable, context=None, correlation_id=None, traceback=None):
        self._append(self._make_event(
            "ERROR", "lifecycle", module, function, msg,
            context=context, correlation_id=correlation_id,
            error_code=error_code, error_category=error_category,
            is_retryable=is_retryable, traceback=traceback,
        ))

    def operation(self, module, function, msg, status, duration_ms=None,
                  api_latency_ms=None, context=None, correlation_id=None):
        self._append(self._make_event(
            "INFO", "operation", module, function, msg,
            status=status, duration_ms=duration_ms, api_latency_ms=api_latency_ms,
            context=context, correlation_id=correlation_id,
        ))

    def close_session(self, exit_reason: str = "normal"):
        with self._lock:
            end = datetime.now(timezone.utc)
            dur = round((end - self._session_start).total_seconds() / 60, 2)
            self._header["session_end"] = end.isoformat(timespec="milliseconds")
            self._header["exit_reason"] = exit_reason
            self._header["summary"] = {
                "operations_completed": self._ops_completed,
                "warnings": self._warnings,
                "errors": self._errors,
                "total_duration_min": dur,
            }
            self._flush()

    # ── Singleton ─────────────────────────────────────────────────

    @classmethod
    def get_instance(cls):
        with cls._class_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance


logger = _Logger.get_instance()
