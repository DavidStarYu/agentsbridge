import pytest

from agentsbridge import cli


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "AGENTS.md").write_text("# Rules\n\n- be nice\n", encoding="utf-8")
    return tmp_path


class TestSyncCommand:
    def test_sync_ok(self, project, capsys):
        assert cli.main(["sync"]) == 0
        out = capsys.readouterr().out
        assert "CLAUDE.md" in out
        assert (project / "CLAUDE.md").is_file()

    def test_sync_dry_run(self, project, capsys):
        assert cli.main(["sync", "--dry-run"]) == 0
        assert not (project / "CLAUDE.md").exists()

    def test_sync_targets_subset(self, project, capsys):
        assert cli.main(["sync", "-t", "claude"]) == 0
        assert (project / "CLAUDE.md").is_file()
        assert not (project / "CONVENTIONS.md").exists()

    def test_sync_unknown_target_exit_code(self, project):
        assert cli.main(["sync", "-t", "nope"]) == 2

    def test_sync_no_source_exit_code(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert cli.main(["sync"]) == 1


class TestCheckCommand:
    def test_check_clean(self, project, capsys):
        cli.main(["sync"])
        assert cli.main(["check"]) == 0

    def test_check_drift_exit_1(self, project):
        cli.main(["sync"])
        (project / "AGENTS.md").write_text("# Rules\n\n- be nice\n- be kind\n", encoding="utf-8")
        assert cli.main(["check"]) == 1


class TestImportCommand:
    def test_import_creates_agents_md(self, project, capsys):
        (project / "AGENTS.md").unlink()
        (project / "CLAUDE.md").write_text("# rules\n- x\n", encoding="utf-8")
        assert cli.main(["import"]) == 0
        assert (project / "AGENTS.md").is_file()
        out = capsys.readouterr().out
        assert "CLAUDE.md" in out

    def test_import_refuses_existing(self, project):
        assert cli.main(["import"]) == 1


class TestInitCommand:
    def test_init(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        assert cli.main(["init"]) == 0
        assert (tmp_path / "AGENTS.md").is_file()

    def test_init_existing_noop(self, project, capsys):
        assert cli.main(["init"]) == 0
        out = capsys.readouterr().out
        assert "already exists" in out


class TestVersion:
    def test_version_flag(self, capsys):
        with pytest.raises(SystemExit) as e:
            cli.main(["--version"])
        assert e.value.code == 0
        assert "agentsbridge" in capsys.readouterr().out


class TestListCommand:
    def test_lists_all_targets(self, capsys):
        assert cli.main(["list"]) == 0
        out = capsys.readouterr().out
        for target in ("claude", "copilot", "cursor", "roo", "kilocode", "junie", "amazonq"):
            assert target in out
        assert "CLAUDE.md" in out
        assert ".roo/rules/agentsbridge.md" in out

    def test_mentions_native_tools(self, capsys):
        assert cli.main(["list"]) == 0
        out = capsys.readouterr().out
        assert "Codex CLI" in out


class TestEnvTargets:
    def test_sync_respects_env(self, project, monkeypatch, capsys):
        monkeypatch.setenv("AGENTSBRIDGE_TARGETS", "claude")
        assert cli.main(["sync"]) == 0
        assert (project / "CLAUDE.md").is_file()
        assert not (project / "CONVENTIONS.md").exists()


class TestCheckSummary:
    def test_drift_message_has_counts(self, project, capsys):
        cli.main(["sync"])
        (project / "AGENTS.md").write_text("# Rules\n\n- be nice\n- be kind\n", encoding="utf-8")
        assert cli.main(["check"]) == 1
        err = capsys.readouterr().err
        assert "drifted" in err
        assert "missing" not in err

    def test_drift_message_includes_missing(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "AGENTS.md").write_text("# Rules\n\n- x\n", encoding="utf-8")
        assert cli.main(["check"]) == 1
        err = capsys.readouterr().err
        assert "missing" in err
