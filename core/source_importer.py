# =========================================================
# core/source_importer.py
# =========================================================
# Prompts the user to import an externally selected file
# into the active workspace stage folder (copy / move / keep external).
# Shows file size, available disk space, and warns before moving
# files that are already referenced by other projects.
# =========================================================

import shutil
from pathlib import Path

from colorama import Fore, Style
from core.input_parsing import is_yes

_APP_ROOT     = Path(__file__).resolve().parent.parent
_PROJECTS_DIR = _APP_ROOT / "Workspace" / "projects"


def _format_size(size_bytes: int) -> str:
    if size_bytes >= 1024 ** 3:
        return f"{size_bytes / 1024 ** 3:.1f} GB"
    elif size_bytes >= 1024 ** 2:
        return f"{size_bytes / 1024 ** 2:.1f} MB"
    else:
        return f"{size_bytes / 1024:.1f} KB"


def _find_projects_referencing(file_path) -> list[str]:
    """Return names of projects whose project_info.json contains the given absolute path."""
    import json as _json
    resolved = str(Path(file_path).resolve())
    # On Windows backslashes are JSON-escaped in the file, so search the JSON-encoded form.
    resolved_json = _json.dumps(resolved)[1:-1]
    referencing = []
    if not _PROJECTS_DIR.exists():
        return referencing
    for proj_dir in _PROJECTS_DIR.iterdir():
        if not proj_dir.is_dir():
            continue
        info_path = proj_dir / "project_info.json"
        if not info_path.exists():
            continue
        try:
            content = info_path.read_text(encoding="utf-8")
            if resolved_json in content:
                referencing.append(proj_dir.name)
        except Exception:
            pass
    return referencing


def ask_import(file_path, dest_dir, messages) -> tuple:
    """Show an import dialog for a file selected outside the workspace.

    Prompts the user to keep the file at its original path, copy it into
    dest_dir, or move it into dest_dir. Displays file size and free disk
    space. Warns if a move would affect other projects that reference the
    same file.

    If the file is already inside dest_dir the dialog is skipped and
    ("external", file_path) is returned immediately.

    Returns:
        (Path, str)  — (final_path, source_mode) where source_mode is
                       "external", "copy", or "move"
        (None, None) — user cancelled; caller should loop back to file selection
    """
    file_path = Path(file_path).resolve()
    dest_dir  = Path(dest_dir).resolve()

    # Skip dialog if file is already inside the destination folder
    try:
        file_path.relative_to(dest_dir)
        return (file_path, "external")
    except ValueError:
        pass

    C, Y, G, RD, R = Fore.CYAN, Fore.YELLOW, Fore.GREEN, Fore.RED, Style.RESET_ALL
    W = 44

    file_size = file_path.stat().st_size if file_path.exists() else 0
    try:
        free_space = shutil.disk_usage(dest_dir.anchor).free
    except Exception:
        free_space = 0

    drive_label = dest_dir.anchor.rstrip("\\/")

    sep = C + "-" * W + R

    while True:
        print()
        print(sep)
        print(C + f" {getattr(messages, 'IMPORT_title', 'IMPORT FILE?')}" + R)
        print(sep)
        print(f" {getattr(messages, 'IMPORT_file_label', 'File')}:  {file_path.name}")
        print(f" {getattr(messages, 'IMPORT_size_label', 'Size')}:  {_format_size(file_size)}")
        print(f" {getattr(messages, 'IMPORT_free_label', 'Free')}:  {_format_size(free_space)}  ({drive_label})")
        print(sep)
        print(f"  1. {getattr(messages, 'IMPORT_opt_external', 'Keep external  (path only)')}")
        print(f"  2. {getattr(messages, 'IMPORT_opt_copy', 'Copy into project')}")
        print(f"  3. {getattr(messages, 'IMPORT_opt_move', 'Move into project')}")
        print(f"  0. {getattr(messages, 'IMPORT_opt_cancel', 'Cancel selection')}")
        print(sep)

        choice = input(getattr(messages, "IMPORT_prompt", "Choice") + ": ").strip()

        if choice == "0":
            return (None, None)

        elif choice == "1":
            return (file_path, "external")

        elif choice == "2":
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / file_path.name
            try:
                shutil.copy2(str(file_path), str(dest))
                print(G + getattr(messages, "IMPORT_copied", "Copied to: {dest}").format(dest=dest) + R)
                return (dest, "copy")
            except Exception as e:
                print(RD + getattr(messages, "IMPORT_error", "Error: {error}").format(error=e) + R)
                continue

        elif choice == "3":
            referencing = _find_projects_referencing(file_path)
            if referencing:
                warn_sep = Y + "-" * W + R
                print()
                print(warn_sep)
                print(Y + f" {getattr(messages, 'IMPORT_warn_title', 'WARNING: file used by other projects')}" + R)
                print(Y + f" {getattr(messages, 'IMPORT_warn_used_by', 'Used by: {projects}').format(projects=', '.join(referencing))}" + R)
                print(warn_sep)
                confirm = input(getattr(messages, "IMPORT_warn_confirm", "Continue with move? (y/N)") + " ").strip()
                if not is_yes(confirm, messages):
                    continue

            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / file_path.name
            try:
                shutil.move(str(file_path), str(dest))
                print(G + getattr(messages, "IMPORT_moved", "Moved to: {dest}").format(dest=dest) + R)
                return (dest, "move")
            except Exception as e:
                print(RD + getattr(messages, "IMPORT_error", "Error: {error}").format(error=e) + R)
                continue

        else:
            print(RD + getattr(messages, "IMPORT_invalid", "Invalid choice") + R)
