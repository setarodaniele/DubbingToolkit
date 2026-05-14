# =========================================================
# core/archive_pruner.py
# =========================================================
# Description:
#   Confirmation-aware archive pruning helper.
#   Wraps WorkspaceManager.prune_archives() with a dry-run
#   preview and user confirmation step.
#
#   Confirmation policy:
#     - dubbed stage: ALWAYS shows double confirmation regardless
#       of the show_confirmations setting (final audio is irreplaceable).
#     - all other stages: shows single confirmation only when
#       show_confirmations=True in settings.
#
#   Per-language pruning:
#     - prune_by_language() reads metadata.json from each archive folder
#       and groups archives by their language code. Applies a per-group
#       count limit independently of the global max_count limit.
#     - Language key read: "detected_lang" (transcripts), "target_lang" (translated).
#
# Language rule:
#   All comments must be written in English.
# =========================================================

import json
from pathlib import Path
from colorama import Fore, Style
from core.input_parsing import is_yes


def _read_lang_from_archive(archive_path: Path, lang_key: str) -> str | None:
    """Read a language code from metadata.json inside an archive folder."""
    meta = archive_path / "metadata.json"
    if not meta.exists():
        return None
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
        return data.get(lang_key)
    except Exception:
        return None


def prune_by_language(
    ws,
    stage: str,
    track_id: str,
    lang_key: str,
    max_per_lang: int,
    use_trash: bool = False,
) -> list:
    """Delete the oldest archive folders that exceed the per-language limit.

    Reads lang_key from each archive's metadata.json to group archives.
    Archives without metadata are treated as language "unknown" and
    counted as a separate group.
    Returns the list of deleted Path objects.
    """
    archive_dir = ws.stage_archive_dir(stage, track_id)
    if not archive_dir.exists():
        return []

    archives = sorted(
        (p for p in archive_dir.iterdir() if p.is_dir()),
        key=lambda p: p.name
    )

    groups: dict[str, list[Path]] = {}
    for a in archives:
        lang = _read_lang_from_archive(a, lang_key) or "unknown"
        groups.setdefault(lang, []).append(a)

    to_delete = []
    for lang_archives in groups.values():
        while len(lang_archives) > max_per_lang:
            to_delete.append(lang_archives.pop(0))

    if to_delete:
        if use_trash:
            try:
                from send2trash import send2trash
                for path in to_delete:
                    send2trash(str(path))
            except Exception:
                import shutil
                for path in to_delete:
                    shutil.rmtree(path, ignore_errors=True)
        else:
            import shutil
            for path in to_delete:
                shutil.rmtree(path, ignore_errors=True)

    return to_delete


def prune_with_confirmation(
    ws,
    stage: str,
    track_id: str,
    messages,
    show_confirmations: bool = True,
    high_risk: bool = False,
    use_trash: bool = False,
    max_count: int | None = None,
    max_size_mb: float | None = None,
) -> list:
    """Prune old archive folders with optional user confirmation.

    Returns the list of deleted Path objects (empty if user cancels or
    nothing needed pruning).

    Parameters
    ----------
    ws               WorkspaceManager instance for the active workspace.
    stage            Pipeline stage name (e.g. "dubbed", "transcripts").
    track_id         Track identifier (e.g. "track_01").
    messages         Localised Messages object.
    show_confirmations  When True, non-high-risk stages ask before deleting.
    high_risk        When True (e.g. dubbed), always asks twice.
    use_trash        When True, send deleted folders to the Recycle Bin.
    max_count        Keep at most this many archive folders.
    max_size_mb      Keep total archive size below this threshold (MB).
    """
    to_delete = ws.prune_archives(
        stage, track_id,
        max_count=max_count,
        max_size_mb=max_size_mb,
        dry_run=True,
    )

    if not to_delete:
        return []

    needs_confirmation = high_risk or show_confirmations

    if needs_confirmation:
        print()
        print(Fore.YELLOW + messages.ARCHIVE_PruneWillDelete + Style.RESET_ALL)
        for p in to_delete:
            print(Fore.YELLOW + messages.ARCHIVE_PruneFolder.format(p.name) + Style.RESET_ALL)

        if high_risk:
            ans1 = input(Fore.RED + messages.ARCHIVE_PruneDubConfirm1 + " " + Style.RESET_ALL).strip()
            if not is_yes(ans1, messages):
                print(Fore.CYAN + messages.ARCHIVE_PruneAborted + Style.RESET_ALL)
                return []
            ans2 = input(Fore.RED + messages.ARCHIVE_PruneDubConfirm2 + " " + Style.RESET_ALL).strip()
            if not is_yes(ans2, messages):
                print(Fore.CYAN + messages.ARCHIVE_PruneAborted + Style.RESET_ALL)
                return []
        else:
            ans = input(Fore.YELLOW + messages.ARCHIVE_PruneConfirm + " " + Style.RESET_ALL).strip()
            if not is_yes(ans, messages):
                print(Fore.CYAN + messages.ARCHIVE_PruneAborted + Style.RESET_ALL)
                return []

    deleted = ws.prune_archives(
        stage, track_id,
        max_count=max_count,
        max_size_mb=max_size_mb,
        dry_run=False,
        use_trash=use_trash,
    )

    if deleted and needs_confirmation:
        print(Fore.GREEN + messages.ARCHIVE_PruneDone.format(len(deleted)) + Style.RESET_ALL)

    return deleted
