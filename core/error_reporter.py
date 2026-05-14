# =========================================================
# core/error_reporter.py
# Error reporting module — collects logs and opens the
# default email client with a pre-filled bug report.
#
# Flow:
#   1. Collect error events from current session log
#   2. Optionally collect recent past sessions
#   3. Build a ZIP archive in Logs/ (ready to attach)
#   4. Open Windows Explorer with the ZIP selected
#   5. Open the default email client via mailto:
# =========================================================

from __future__ import annotations

import json
import os
import platform
import subprocess
import urllib.parse
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_PROJECT_ROOT = Path(__file__).parent.parent
_LOGS_DIR     = _PROJECT_ROOT / "Logs"

# ── Developer contact ─────────────────────────────────────
DEVELOPER_EMAIL = "SmallSoftwareHouse@gmail.com"
APP_NAME        = "DubbingToolkit"

# ── Report settings ───────────────────────────────────────
MAX_PAST_SESSIONS = 3       # include last N sessions (besides current)
MAX_EVENTS_IN_BODY = 15     # max error/warning events shown in email body
MAILTO_BODY_LIMIT  = 1800   # characters before truncation in mailto: body


# =========================================================
# Internal helpers
# =========================================================

def _app_version() -> str:
    try:
        p = _PROJECT_ROOT / "Settings" / "settings_default.json"
        with p.open(encoding="utf-8") as f:
            return str(json.load(f).get("version", "?"))
    except Exception:
        return "?"


def _load_session(path: Path) -> Optional[dict]:
    """Load and return a session JSON. Returns None on error."""
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _collect_errors(session: dict) -> list[dict]:
    """Return only ERROR-level events from a session."""
    return [e for e in session.get("events", []) if e.get("level") == "ERROR"]


def _collect_warnings(session: dict) -> list[dict]:
    """Return only WARNING-level events from a session."""
    return [e for e in session.get("events", []) if e.get("level") == "WARNING"]


def _format_event_text(event: dict) -> str:
    """Render a single event as readable plain text."""
    lines = [
        f"  [{event.get('level')}] {event.get('time', '')}",
        f"  Module   : {event.get('module', '?')}.{event.get('function', '?')}",
        f"  Message  : {event.get('msg', '')}",
    ]
    ctx = event.get("context")
    if ctx:
        lines.append(f"  Context  : {json.dumps(ctx, ensure_ascii=False)}")
    ec = event.get("error_code")
    if ec:
        lines.append(f"  Error    : {ec} / {event.get('error_category', '')} (retryable: {event.get('is_retryable')})")
    tb = event.get("traceback")
    if tb:
        lines.append(f"  Traceback:\n    " + tb.replace("\n", "\n    "))
    return "\n".join(lines)


def _compute_stats(sess: dict) -> dict:
    """
    Compute session statistics directly from events (works for open sessions
    that haven't been closed yet, where summary is still None).
    Falls back to the stored summary if present.
    """
    summ   = sess.get("summary") or {}
    events = sess.get("events", [])

    errors   = [e for e in events if e.get("level") == "ERROR"]
    warnings = [e for e in events if e.get("level") == "WARNING"]
    ops_done = [e for e in events
                if e.get("event_type") == "operation" and e.get("status") == "SUCCESS"]

    # Duration: prefer stored value; otherwise compute from timestamps
    duration_str = "?"
    stored_dur = summ.get("total_duration_min")
    if stored_dur is not None:
        duration_str = f"{stored_dur}"
    else:
        start_str = sess.get("session_start")
        end_str   = sess.get("session_end")
        if start_str:
            try:
                start_dt = datetime.fromisoformat(start_str)
                end_dt   = (datetime.fromisoformat(end_str) if end_str
                            else datetime.now(timezone.utc))
                dur_min = round((end_dt - start_dt).total_seconds() / 60, 1)
                duration_str = f"{dur_min} (sessione {'aperta' if not end_str else 'chiusa'})"
            except Exception:
                pass

    return {
        "errors":   summ.get("errors",                len(errors)),
        "warnings": summ.get("warnings",              len(warnings)),
        "ops_done": summ.get("operations_completed",  len(ops_done)),
        "duration": duration_str,
    }


def _build_report_text(sessions: list[dict]) -> str:
    """
    Build a human-readable plain-text report from one or more sessions.
    Sections: header, system info, error list, full log summary.
    """
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "=" * 60,
        f"  {APP_NAME} — Error Report",
        f"  Generated : {now_str}",
        f"  Version   : {_app_version()}",
        "=" * 60,
        "",
    ]

    for idx, sess in enumerate(sessions):
        label  = "CURRENT SESSION" if idx == 0 else f"PREVIOUS SESSION {idx}"
        si     = sess.get("system_info", {})
        stats  = _compute_stats(sess)
        errors   = _collect_errors(sess)
        warnings = _collect_warnings(sess)

        end_val = sess.get("session_end") or "(sessione ancora aperta)"

        lines += [
            f"── {label} ───────────────────────────────────────",
            f"  Session ID : {sess.get('session_id', '?')}",
            f"  Start      : {sess.get('session_start', '?')}",
            f"  End        : {end_val}",
            f"  App ver.   : {si.get('app_version', '?')}",
            f"  Python     : {si.get('python_version', '?')}",
            f"  OS         : {si.get('os', '?')} {si.get('os_version', '')}",
            f"  CPU        : {si.get('cpu', '?')}",
            f"  RAM        : {si.get('ram_gb', '?')} GB",
            f"  Errors     : {stats['errors']}",
            f"  Warnings   : {stats['warnings']}",
            f"  Ops done   : {stats['ops_done']}",
            f"  Duration   : {stats['duration']} min",
            "",
        ]

        # ── Error events ──────────────────────────────────
        if errors:
            lines.append(f"  ERRORS ({len(errors)}):")
            lines.append("  " + "-" * 40)
            for ev in errors:
                lines.append(_format_event_text(ev))
                lines.append("")
        else:
            lines.append("  (no ERROR events in this session)")
            lines.append("")

        # ── Warning events ────────────────────────────────
        if warnings:
            lines.append(f"  WARNINGS ({len(warnings)}):")
            lines.append("  " + "-" * 40)
            for ev in warnings[:MAX_EVENTS_IN_BODY]:
                lines.append(_format_event_text(ev))
                lines.append("")
            if len(warnings) > MAX_EVENTS_IN_BODY:
                lines.append(f"  ... {len(warnings) - MAX_EVENTS_IN_BODY} more warnings in attached log.")
                lines.append("")

        lines.append("")

    lines += [
        "=" * 60,
        "  ATTACHED ZIP contains full session log(s).",
        "  Please attach it before sending.",
        "=" * 60,
    ]
    return "\n".join(lines)


def _get_recent_session_paths(current_path: Optional[Path], n: int) -> list[Path]:
    """
    Return up to n most-recent session JSON files EXCLUDING current_path,
    sorted newest first.
    """
    all_logs = sorted(
        _LOGS_DIR.glob("*_session*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    result = []
    for p in all_logs:
        if current_path and p.resolve() == current_path.resolve():
            continue
        result.append(p)
        if len(result) >= n:
            break
    return result


def _build_zip(sessions_paths: list[Path], report_text: str) -> Path:
    """
    Create a ZIP in Logs/ containing:
      - error_report.txt   (human-readable summary)
      - each session JSON
    Returns the ZIP path.
    """
    ts  = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    zip_path = _LOGS_DIR / f"DubbingToolkit_error_report_{ts}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("error_report.txt", report_text)
        for sp in sessions_paths:
            if sp.exists():
                zf.write(sp, sp.name)

    return zip_path


def _open_explorer_select(path: Path):
    """Open Windows Explorer with the given file selected."""
    try:
        subprocess.run(["explorer", "/select,", str(path)], check=False)
    except Exception:
        try:
            os.startfile(str(path.parent))
        except Exception:
            pass


def _open_mailto(subject: str, body: str):
    """Open the default email client via a mailto: URL."""
    # Truncate body to stay within URL limits
    if len(body) > MAILTO_BODY_LIMIT:
        body = body[:MAILTO_BODY_LIMIT] + "\n...\n[TRUNCATED — see attached ZIP for full report]"

    params = urllib.parse.urlencode(
        {"subject": subject, "body": body},
        quote_via=urllib.parse.quote,
    )
    url = f"mailto:{urllib.parse.quote(DEVELOPER_EMAIL)}?{params}"
    try:
        os.startfile(url)
    except Exception:
        # Fallback: webbrowser
        import webbrowser
        webbrowser.open(url)


# =========================================================
# Public API
# =========================================================

def create_silent_exit_report(logger_instance) -> Optional[Path]:
    """
    Create a ZIP report silently — no email, no Explorer, no user input.
    Called automatically when the console window is closed with X or on crash.
    Returns the ZIP path on success, None on failure.
    Fast: designed to complete within the ~5-second Windows shutdown window.
    """
    try:
        current_path = logger_instance._log_path
        current_sess = _load_session(current_path)
        if current_sess is None:
            return None

        paths_for_zip = [current_path]
        sessions_for_report = [current_sess]

        past_paths = _get_recent_session_paths(current_path, MAX_PAST_SESSIONS)
        for pp in past_paths:
            ps = _load_session(pp)
            if ps:
                sessions_for_report.append(ps)
                paths_for_zip.append(pp)

        report_text = _build_report_text(sessions_for_report)
        zip_path = _build_zip(paths_for_zip, report_text)
        return zip_path
    except Exception:
        return None


def has_errors(logger_instance) -> bool:
    """Quick check: did the current session log any ERROR-level events?"""
    try:
        session_path = logger_instance._log_path
        sess = _load_session(session_path)
        if sess is None:
            return False
        return any(e.get("level") == "ERROR" for e in sess.get("events", []))
    except Exception:
        return False


def send_error_report(
    logger_instance,
    messages=None,
    include_past_sessions: bool = True,
    open_explorer: bool = True,
) -> bool:
    """
    Main entry point.

    Steps:
      1. Load current session log
      2. Load recent past sessions (if requested)
      3. Build a plain-text report
      4. Create a ZIP archive in Logs/
      5. Open Explorer with ZIP selected
      6. Open default email client (mailto:) with pre-filled subject + body
      7. Show instructions in the terminal

    Args:
        logger_instance : the global ``logger`` singleton from core.logger
        messages        : Messages object for localized strings (optional)
        include_past_sessions: whether to include previous session logs in ZIP
        open_explorer   : whether to open Explorer pointing to the ZIP

    Returns:
        True if report was generated successfully, False on error.
    """
    from colorama import Fore, Style
    C, G, Y, RD, R = Fore.CYAN, Fore.GREEN, Fore.YELLOW, Fore.RED, Style.RESET_ALL

    try:
        # ── 1. Current session ────────────────────────────
        current_path = logger_instance._log_path
        current_sess = _load_session(current_path)
        if current_sess is None:
            print(RD + " [!] Cannot read current session log." + R)
            return False

        sessions_for_report = [current_sess]
        paths_for_zip       = [current_path]

        # ── 2. Past sessions ──────────────────────────────
        if include_past_sessions:
            past_paths = _get_recent_session_paths(current_path, MAX_PAST_SESSIONS)
            for pp in past_paths:
                ps = _load_session(pp)
                if ps:
                    sessions_for_report.append(ps)
                    paths_for_zip.append(pp)

        # ── 3. Build report text ──────────────────────────
        report_text = _build_report_text(sessions_for_report)

        # ── 4. Build ZIP ──────────────────────────────────
        zip_path = _build_zip(paths_for_zip, report_text)

        # ── 5. Open Explorer ──────────────────────────────
        if open_explorer:
            _open_explorer_select(zip_path)

        # ── 6. Open email client ──────────────────────────
        version = _app_version()
        session_id = current_sess.get("session_id", "?")
        error_count = len(_collect_errors(current_sess))
        os_info = current_sess.get("system_info", {}).get("os", platform.system())

        subject = f"[{APP_NAME} v{version}] Error Report — {session_id}"

        body_lines = [
            f"Hello,",
            f"",
            f"I encountered an error in {APP_NAME} and I'm sending this report.",
            f"",
            f"--- SUMMARY ---",
            f"Version  : {version}",
            f"Session  : {session_id}",
            f"OS       : {os_info}",
            f"Errors   : {error_count}",
            f"",
            f"--- ERROR DETAILS ---",
        ]

        # Add first few errors inline
        errors = _collect_errors(current_sess)
        for ev in errors[:3]:
            body_lines.append(_format_event_text(ev))
            body_lines.append("")

        if error_count > 3:
            body_lines.append(f"... {error_count - 3} more error(s) in attached ZIP.")
            body_lines.append("")

        body_lines += [
            "--- ATTACHED FILE ---",
            f"Please find the full report ZIP attached:",
            f"  {zip_path.name}",
            f"",
            "(The ZIP file should be open in Explorer — please attach it to this email.)",
            f"",
            "Thank you.",
        ]

        body = "\n".join(body_lines)
        _open_mailto(subject, body)

        # ── 7. Terminal instructions ──────────────────────
        print()
        print(C + "=" * 54 + R)
        print(C + "  SEGNALAZIONE ERRORI — REPORT CREATO" + R)
        print(C + "=" * 54 + R)
        print()
        print(G + "  ✓ File ZIP pronto:" + R)
        print(f"    {zip_path.name}")
        print(f"    (posizione: Logs\)")
        print()
        print(C + "  ─── COSA FARE ORA ───────────────────────────" + R)
        print()
        print(Y + "  1." + R + " Explorer si è aperto con il file ZIP evidenziato.")
        print(Y + "  2." + R + " Il tuo client email si è aperto (o ti ha chiesto")
        print("     con quale app aprirlo — scegli la tua email).")
        print()
        print(Y + "  3. IMPORTANTE:" + R + " prima di inviare l'email,")
        print(Y + "     ALLEGA il file ZIP" + R + " che vedi in Explorer.")
        print()
        print(f"  Destinatario: {C}{DEVELOPER_EMAIL}{R}")
        print()
        print(C + "  Il report contiene:" + R)
        print(f"    • Log della sessione corrente")
        print(f"    • Log delle {MAX_PAST_SESSIONS} sessioni precedenti")
        print(f"    • Informazioni di sistema (OS, CPU, RAM, versione app)")
        print(f"    • Dettaglio errori e traceback")
        print()
        print(C + "=" * 54 + R)
        print()
        input("  Premi Invio per tornare al menu... ")

        return True

    except Exception as e:
        try:
            from colorama import Fore, Style
            print(Fore.RED + f" [!] Error reporter failed: {e}" + Style.RESET_ALL)
        except Exception:
            print(f"[!] Error reporter failed: {e}")
        return False
