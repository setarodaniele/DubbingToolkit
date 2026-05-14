# =========================================================
# core/update_checker.py — Remote version check via GitHub Gist
# =========================================================

import json
import time
import urllib.request
import urllib.error
from typing import Optional


def check_for_updates(current_version: str, gist_url: str) -> tuple:
    """
    Downloads version.json from gist_url and compares with current_version.

    Returns:
        (True,  remote_version) — a newer version is available
        (False, None)           — already up to date
        (None,  None)           — connection/parse error
    """
    try:
        gist_url_with_cache_bust = f"{gist_url}?t={int(time.time())}"
        req = urllib.request.Request(
            gist_url_with_cache_bust,
            headers={"User-Agent": "DubbingToolkit-UpdateChecker"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        remote_version = data.get("version", "")
        if not remote_version:
            return (None, None)
        if _version_tuple(remote_version) > _version_tuple(current_version):
            return (True, remote_version)
        return (False, None)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return (None, None)
    except Exception:
        return (None, None)


def _version_tuple(v: str) -> tuple:
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except ValueError:
        return (0,)
