# =========================================================
# core/workspace_manager.py
# =========================================================
# Description:
#   Central resolver for all workspace paths.
#   All modules must obtain workspace paths through this class.
#   No other module may use hardcoded Path(...) for workspace locations.
#
#   Workspace layout:
#     Workspace/
#       active_workspace.json
#       runtime.lock
#       temp/                      global temp, always safe-to-delete
#       projects/
#         {name}/                  named workspaces
#           project_info.json
#           video_input/
#           audio_input/
#           audio_extraction/
#           transcripts/
#           translated/
#           dubbed/
#           output/
#
#   Within each stage, outputs are stored as:
#     {stage}/{track_id}/current/   active output
#     {stage}/{track_id}/archive/   previous outputs (rotate_to_archive)
#
# Language rule:
#   All comments must be written in English.
# =========================================================

import os
import secrets
import shutil
from datetime import datetime
from pathlib import Path

from .utils_settings import load_json, write_json_atomic

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_APP_ROOT      = Path(__file__).resolve().parent.parent   # DubbingToolkit/
_WORKSPACE_DIR = _APP_ROOT / "Workspace"
_ACTIVE_FILE   = _WORKSPACE_DIR / "active_workspace.json"
_TEMP_DIR      = _WORKSPACE_DIR / "temp"
_PROJECTS_DIR  = _WORKSPACE_DIR / "projects"

_STAGE_DIRS = [
    "video_input",
    "audio_input",
    "audio_extraction",
    "transcripts",
    "translated",
    "dubbed",
    "output",
]


class WorkspaceError(Exception):
    pass


# ---------------------------------------------------------------------------
# WorkspaceManager
# ---------------------------------------------------------------------------

class WorkspaceManager:
    """Central resolver for all workspace paths.

    Obtain an instance with WorkspaceManager.get_active().
    Never instantiate directly in pipeline scripts.
    """

    def __init__(self, name: str) -> None:
        self._name = name
        self._root = _PROJECTS_DIR / name

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Logical name of the active project."""
        return self._name

    @property
    def root(self) -> Path:
        """Absolute path to the active workspace root directory."""
        return self._root

    # ------------------------------------------------------------------
    # Path resolution
    # ------------------------------------------------------------------

    def resolve(self, relative_path: str) -> Path:
        """Convert a workspace-relative path (forward slashes) to an absolute Path.

        The relative_path format matches what is stored in project_info.json.
        Example:
            ws.resolve("transcripts/track_01/current/transcript_work.srt")
            -> Path(".../Workspace/projects/my_project/transcripts/track_01/current/transcript_work.srt")
        """
        return self._root / Path(*relative_path.split("/"))

    def stage_current(self, stage: str, track_id: str) -> Path:
        """Return the current/ directory for a stage and track.

        Example:
            ws.stage_current("transcripts", "track_01")
            -> Path(".../transcripts/track_01/current/")
        """
        return self._root / stage / track_id / "current"

    def stage_archive_dir(self, stage: str, track_id: str) -> Path:
        """Return the archive/ directory for a stage and track."""
        return self._root / stage / track_id / "archive"

    def relative(self, absolute_path: Path) -> str:
        """Convert an absolute path inside this workspace to a forward-slash relative string.

        Used when writing paths into project_info.json.
        Raises ValueError if the path is outside this workspace root.
        """
        rel = absolute_path.resolve().relative_to(self._root.resolve())
        return rel.as_posix()

    # ------------------------------------------------------------------
    # Archive rotation
    # ------------------------------------------------------------------

    def rotate_to_archive(self, stage: str, track_id: str) -> Path | None:
        """Move current/ -> archive/{timestamp}_{suffix}/ and return the archive path.

        Must be called only AFTER new output has been successfully produced.
        Returns None if current/ does not exist (first run, nothing to archive).
        A short random suffix prevents collision on rapid retries.
        """
        current = self.stage_current(stage, track_id)
        if not current.exists():
            return None

        archive_base = self.stage_archive_dir(stage, track_id)
        archive_base.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        suffix    = secrets.token_hex(2)
        dest      = archive_base / f"{timestamp}_{suffix}"

        current.rename(dest)
        return dest

    def prune_archives(self, stage: str, track_id: str,
                       max_count: int | None = None,
                       max_size_mb: float | None = None,
                       dry_run: bool = False,
                       use_trash: bool = False) -> list:
        """Delete the oldest archive folders that exceed the given limits.

        max_count   — keep at most this many archive folders per track/stage.
        max_size_mb — keep total archive size below this threshold (MB).
        dry_run     — if True, compute and return what would be deleted without
                      actually deleting anything (used for pre-confirmation preview).
        use_trash   — if True, send folders to the system Recycle Bin instead of
                      permanently deleting them. Ignored when dry_run=True.
        Both limits are applied independently; whichever is violated triggers
        deletion of the oldest folder (sorted by timestamp-prefixed name).
        Returns the list of deleted (or would-be-deleted) Path objects.
        """
        archive_dir = self.stage_archive_dir(stage, track_id)
        if not archive_dir.exists():
            return []

        archives = sorted(
            (p for p in archive_dir.iterdir() if p.is_dir()),
            key=lambda p: p.name
        )

        to_delete = []

        if max_count is not None:
            while len(archives) > max_count:
                oldest = archives.pop(0)
                to_delete.append(oldest)

        if max_size_mb is not None:
            def _size_mb(path: Path) -> float:
                return sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / (1024 * 1024)

            while archives:
                if sum(_size_mb(a) for a in archives) <= max_size_mb:
                    break
                oldest = archives.pop(0)
                to_delete.append(oldest)

        if not dry_run:
            if use_trash:
                try:
                    from send2trash import send2trash
                    for path in to_delete:
                        send2trash(str(path))
                except Exception:
                    for path in to_delete:
                        shutil.rmtree(path, ignore_errors=True)
            else:
                for path in to_delete:
                    shutil.rmtree(path, ignore_errors=True)

        return to_delete

    # ------------------------------------------------------------------
    # Structure management
    # ------------------------------------------------------------------

    def ensure_structure(self) -> None:
        """Create all missing workspace directories for this project."""
        _TEMP_DIR.mkdir(parents=True, exist_ok=True)
        _PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

        for stage in _STAGE_DIRS:
            (self._root / stage).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Factory / class-level methods
    # ------------------------------------------------------------------

    @classmethod
    def get_active(cls) -> "WorkspaceManager | None":
        """Read active_workspace.json and return the active workspace, or None.

        Returns None if no project is active, the file is missing, or the
        project directory no longer exists on disk.
        """
        try:
            data = load_json(_ACTIVE_FILE)
            name = data.get("active")
            if not name:
                return None
            if not (_PROJECTS_DIR / name).exists():
                return None
            return cls(name)
        except Exception:
            return None

    @classmethod
    def create_project(cls, name: str) -> "WorkspaceManager":
        """Create a new named project, set it as active, and return its manager.

        Raises WorkspaceError if the name is reserved or already exists.
        """
        _validate_name(name)
        if (_PROJECTS_DIR / name).exists():
            raise WorkspaceError(f"Project '{name}' already exists.")
        ws = cls(name)
        ws.ensure_structure()
        _write_active(name)
        return ws

    @classmethod
    def open_project(cls, name: str) -> "WorkspaceManager":
        """Set an existing project as active and return its manager.

        Raises WorkspaceError if the project does not exist.
        """
        _validate_name(name)
        if not (_PROJECTS_DIR / name).exists():
            raise WorkspaceError(f"Project '{name}' does not exist.")
        _write_active(name)
        return cls(name)

    @classmethod
    def close_project(cls) -> None:
        """Deselect the active project. get_active() will return None afterwards."""
        _write_active(None)

    @classmethod
    def list_projects(cls) -> list[str]:
        """Return a sorted list of existing project names."""
        if not _PROJECTS_DIR.exists():
            return []
        return sorted(d.name for d in _PROJECTS_DIR.iterdir() if d.is_dir())

    @classmethod
    def delete_project(cls, name: str, use_trash: bool = False) -> None:
        """Delete a named project directory.

        If the deleted project was active, clears the active selection.
        Raises WorkspaceError if name is reserved or project does not exist.
        """
        _validate_name(name)
        project_dir = _PROJECTS_DIR / name
        if not project_dir.exists():
            raise WorkspaceError(f"Project '{name}' does not exist.")
        active = cls.get_active()
        if active is not None and active.name == name:
            _write_active(None)
        if use_trash:
            try:
                from send2trash import send2trash
                send2trash(str(project_dir))
                return
            except Exception:
                pass
        shutil.rmtree(project_dir)

    @classmethod
    def duplicate_project(cls, source_name: str, dest_name: str) -> "WorkspaceManager":
        """Copy a project directory to a new name.

        Updates progetto.nome_progetto in the copy's project_info.json if present.
        Returns a WorkspaceManager for the new project (not set as active).
        Raises WorkspaceError if source does not exist or dest already exists.
        """
        _validate_name(source_name)
        _validate_name(dest_name)
        source_dir = _PROJECTS_DIR / source_name
        dest_dir   = _PROJECTS_DIR / dest_name
        if not source_dir.exists():
            raise WorkspaceError(f"Project '{source_name}' does not exist.")
        if dest_dir.exists():
            raise WorkspaceError(f"Project '{dest_name}' already exists.")
        shutil.copytree(str(source_dir), str(dest_dir))
        info_path = dest_dir / "project_info.json"
        if info_path.exists():
            try:
                import json
                data = json.loads(info_path.read_text(encoding="utf-8"))
                if isinstance(data.get("progetto"), dict):
                    data["progetto"]["nome_progetto"] = dest_name
                write_json_atomic(info_path, data)
            except Exception:
                pass
        return cls(dest_name)

    @classmethod
    def rename_project(cls, old_name: str, new_name: str) -> "WorkspaceManager":
        """Rename a project directory.

        If the renamed project was active, updates the active pointer.
        Updates progetto.nome_progetto in project_info.json if present.
        Returns a WorkspaceManager for the renamed project.
        Raises WorkspaceError if old_name does not exist or new_name already exists.
        """
        _validate_name(old_name)
        _validate_name(new_name)
        old_dir = _PROJECTS_DIR / old_name
        new_dir = _PROJECTS_DIR / new_name
        if not old_dir.exists():
            raise WorkspaceError(f"Project '{old_name}' does not exist.")
        if new_dir.exists():
            raise WorkspaceError(f"Project '{new_name}' already exists.")
        # Check active status before renaming — get_active() validates dir existence
        active = cls.get_active()
        was_active = active is not None and active.name == old_name
        old_dir.rename(new_dir)
        if was_active:
            _write_active(new_name)
        info_path = new_dir / "project_info.json"
        if info_path.exists():
            try:
                import json
                data = json.loads(info_path.read_text(encoding="utf-8"))
                if isinstance(data.get("progetto"), dict):
                    data["progetto"]["nome_progetto"] = new_name
                write_json_atomic(info_path, data)
            except Exception:
                pass
        return cls(new_name)


# ---------------------------------------------------------------------------
# Module-private helpers
# ---------------------------------------------------------------------------

def _write_active(name: str) -> None:
    _WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    write_json_atomic(_ACTIVE_FILE, {"schema_version": 1, "active": name})


def _validate_name(name: str) -> None:
    if not name:
        raise WorkspaceError("Project name cannot be empty.")
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
    invalid = set(name) - allowed
    if invalid:
        raise WorkspaceError(f"Invalid characters in project name: {''.join(sorted(invalid))}")
