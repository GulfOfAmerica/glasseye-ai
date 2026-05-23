"""
conftest.py — redirect root-owned
paths to tmp_path so non-root users can run the GlasseyeOS-AI test suite.
"""
import logging
import os
import sqlite3
import sys
from pathlib import Path
import pytest

GLASSEYE_ROOT = Path('/home/x/GlasseyeOS-AI')
sys.path.insert(0, str(GLASSEYE_ROOT))


def _is_root_owned_path(p) -> bool:
    try:
        Path(str(p)).relative_to(GLASSEYE_ROOT)
        return True
    except (ValueError, TypeError):
        return False


@pytest.fixture(autouse=True)
def redirect_file_handlers(tmp_path, monkeypatch):
    original_init = logging.FileHandler.__init__
    def patched_init(self, filename, mode="a", encoding=None, delay=False, errors=None):
        s = str(filename)
        if not os.path.isabs(s) or _is_root_owned_path(s):
            filename = str(tmp_path / Path(s).name)
        kwargs = dict(mode=mode, encoding=encoding, delay=delay)
        if errors is not None:
            kwargs["errors"] = errors
        original_init(self, filename, **kwargs)
    monkeypatch.setattr(logging.FileHandler, "__init__", patched_init)


@pytest.fixture(autouse=True)
def redirect_mkdir(monkeypatch):
    original_mkdir = Path.mkdir
    def patched_mkdir(self, mode=0o777, parents=False, exist_ok=False):
        try:
            original_mkdir(self, mode=mode, parents=parents, exist_ok=exist_ok)
        except PermissionError:
            pass
    monkeypatch.setattr(Path, "mkdir", patched_mkdir)


@pytest.fixture(autouse=True)
def redirect_db(tmp_path, monkeypatch):
    original_connect = sqlite3.connect
    def patched_connect(database, *args, **kwargs):
        if isinstance(database, str) and (not os.path.isabs(database) or _is_root_owned_path(database)):
            database = str(tmp_path / Path(database).name)
        return original_connect(database, *args, **kwargs)
    monkeypatch.setattr(sqlite3, "connect", patched_connect)


@pytest.fixture(autouse=True)
def redirect_compliance_paths(tmp_path, monkeypatch):
    import compliance_enforcer as ce
    original_ce_init = ce.ComplianceEnforcer.__init__
    def patched_ce_init(self, *args, **kwargs):
        original_ce_init(self, *args, **kwargs)
        self.audit_log_path = str(tmp_path / "compliance_audit.jsonl")
        if hasattr(self, "incident_response") and hasattr(self.incident_response, "incidents_dir"):
            self.incident_response.incidents_dir = tmp_path / "incidents"
            self.incident_response.incidents_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(ce.ComplianceEnforcer, "__init__", patched_ce_init)


@pytest.fixture(autouse=True)
def redirect_tool_generator_base(tmp_path, monkeypatch):
    """Only redirect dirs that point into the root-owned tree (no explicit override given)."""
    try:
        import tool_generator as tg
        original_tg_init = tg.ToolGenerator.__init__

        def patched_tg_init(self, templates_dir=None, output_dir=None, skills_dir=None):
            original_tg_init(self, templates_dir=templates_dir,
                             output_dir=output_dir, skills_dir=skills_dir)
            # Only redirect dirs that ended up pointing inside the root-owned tree
            if _is_root_owned_path(self.base_dir):
                self.base_dir = tmp_path
            if _is_root_owned_path(self.tools_dir if hasattr(self, 'tools_dir') else self.output_dir):
                self.tools_dir = tmp_path / "generated_tools"
                self.output_dir = tmp_path / "generated_tools"
                self.tools_dir.mkdir(exist_ok=True)
            if _is_root_owned_path(self.skills_dir):
                self.skills_dir = tmp_path / "generated_skills"
                self.skills_dir.mkdir(exist_ok=True)
            if _is_root_owned_path(self.templates_dir):
                self.templates_dir = tmp_path / "templates"
                self.templates_dir.mkdir(exist_ok=True)

        monkeypatch.setattr(tg.ToolGenerator, "__init__", patched_tg_init)
    except ImportError:
        pass


@pytest.fixture(autouse=True)
def redirect_self_updater_dirs(tmp_path, monkeypatch):
    """Redirect EnhancedSelfUpdater data dirs to tmp_path for test isolation."""
    try:
        import self_updater as su
        original_su_init = su.EnhancedSelfUpdater.__init__

        def patched_su_init(self, *args, **kwargs):
            original_su_init(self, *args, **kwargs)
            # Redirect all data dirs to tmp_path for isolation
            if not str(self.data_cache_dir).startswith('/tmp/pytest'):
                self.data_cache_dir = tmp_path / "data_cache"
                self.data_cache_dir.mkdir(exist_ok=True)
            if not str(self.program_snapshots_dir).startswith('/tmp/pytest'):
                self.program_snapshots_dir = tmp_path / "program_snapshots"
                self.program_snapshots_dir.mkdir(exist_ok=True)

        monkeypatch.setattr(su.EnhancedSelfUpdater, "__init__", patched_su_init)
    except ImportError:
        pass

@pytest.fixture(autouse=True)
def isolate_cwd(tmp_path, monkeypatch):
    """
    Run each test with cwd=tmp_path and pre-create writable subdirs that
    the source code expects (logs/, data_sources/, config/).
    Relative Path checks in tests (e.g. Path('logs/foo').exists()) then
    resolve correctly inside tmp_path.
    """
    for subdir in ('logs', 'logs/incidents', 'data_sources', 'data_sources/program_snapshots', 'config'):
        (tmp_path / subdir).mkdir(parents=True, exist_ok=True)
    # Copy read-only config files the source may need
    src_config = GLASSEYE_ROOT / 'config'
    if src_config.exists():
        import shutil
        try:
            shutil.copytree(str(src_config), str(tmp_path / 'config'), dirs_exist_ok=True)
        except Exception:
            pass
    monkeypatch.chdir(tmp_path)
