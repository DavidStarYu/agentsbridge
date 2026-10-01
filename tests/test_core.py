import pytest

from agentsbridge import core
from agentsbridge.targets import GENERATED_MARKER, TARGETS, render


def write_agents_md(root, body="# Rules\n\n- Be nice.\n"):
    (root / "AGENTS.md").write_text(body, encoding="utf-8")


class TestSync:
    def test_creates_all_targets(self, tmp_path):
        write_agents_md(tmp_path)
        results = core.sync(tmp_path)
        actions = {r.target: r.action for r in results}
        assert set(actions) == set(TARGETS)
        assert all(a in ("created",) for a in actions.values())
        assert (tmp_path / "CLAUDE.md").is_file()
        assert (tmp_path / ".github" / "copilot-instructions.md").is_file()
        assert (tmp_path / ".cursor" / "rules" / "agentsbridge.mdc").is_file()
        assert (tmp_path / ".windsurfrules").is_file()
        assert (tmp_path / ".clinerules").is_file()
        assert (tmp_path / "CONVENTIONS.md").is_file()

    def test_generated_files_have_marker(self, tmp_path):
        write_agents_md(tmp_path)
        core.sync(tmp_path)
        for r in core.sync(tmp_path):  # second run: unchanged
            text = r.path.read_text(encoding="utf-8")
            if r.target != "agents":
                assert GENERATED_MARKER in text

    def test_second_sync_is_noop(self, tmp_path):
        write_agents_md(tmp_path)
        core.sync(tmp_path)
        results = core.sync(tmp_path)
        assert all(r.action == "unchanged" for r in results)

    def test_source_body_preserved(self, tmp_path):
        write_agents_md(tmp_path, "# My Rules\n\n- use tabs\n- no lints\n")
        core.sync(tmp_path)
        text = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
        assert "use tabs" in text
        assert "no lints" in text
        assert "# My Rules" in text

    def test_never_overwrite_user_file_without_force(self, tmp_path):
        write_agents_md(tmp_path)
        (tmp_path / "CLAUDE.md").write_text("# my precious manual rules", encoding="utf-8")
        results = core.sync(tmp_path)
        by_target = {r.target: r for r in results}
        assert by_target["claude"].action == "skipped"
        assert "manual rules" in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")

    def test_force_overwrites_user_file(self, tmp_path):
        write_agents_md(tmp_path)
        (tmp_path / "CLAUDE.md").write_text("# manual", encoding="utf-8")
        results = core.sync(tmp_path, force=True)
        by_target = {r.target: r for r in results}
        assert by_target["claude"].action in ("created", "updated")
        assert GENERATED_MARKER in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")

    def test_dry_run_writes_nothing(self, tmp_path):
        write_agents_md(tmp_path)
        results = core.sync(tmp_path, dry_run=True)
        assert all(r.action == "created" for r in results)
        assert not (tmp_path / "CLAUDE.md").exists()

    def test_selected_targets(self, tmp_path):
        write_agents_md(tmp_path)
        results = core.sync(tmp_path, selected=["claude", "copilot"])
        assert {r.target for r in results} == {"claude", "copilot"}
        assert (tmp_path / "CLAUDE.md").is_file()
        assert not (tmp_path / ".windsurfrules").exists()

    def test_unknown_target_raises(self, tmp_path):
        write_agents_md(tmp_path)
        with pytest.raises(ValueError, match="Unknown target"):
            core.sync(tmp_path, selected=["nope"])

    def test_missing_source_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            core.sync(tmp_path)

    def test_edit_then_resync_updates(self, tmp_path):
        write_agents_md(tmp_path, "# v1\n- rule a\n")
        core.sync(tmp_path)
        write_agents_md(tmp_path, "# v2\n- rule a\n- rule b\n")
        results = core.sync(tmp_path)
        assert all(r.action == "updated" for r in results)
        assert "rule b" in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")


class TestCheck:
    def test_clean_after_sync(self, tmp_path):
        write_agents_md(tmp_path)
        core.sync(tmp_path)
        clean, results = core.check(tmp_path)
        assert clean
        assert all(r.action in ("ok", "skipped") for r in results)

    def test_detects_drift(self, tmp_path):
        write_agents_md(tmp_path, "# v1\n- a\n")
        core.sync(tmp_path)
        write_agents_md(tmp_path, "# v2\n- a\n- b\n")
        clean, results = core.check(tmp_path)
        assert not clean
        assert any(r.action == "drifted" for r in results)

    def test_detects_missing(self, tmp_path):
        write_agents_md(tmp_path)
        clean, results = core.check(tmp_path)
        assert not clean
        assert any(r.action == "missing" for r in results)

    def test_selected_subset(self, tmp_path):
        write_agents_md(tmp_path)
        core.sync(tmp_path, selected=["claude"])
        clean, _ = core.check(tmp_path, selected=["claude"])
        assert clean
        clean2, _ = core.check(tmp_path, selected=["copilot"])
        assert not clean2


class TestImport:
    def test_import_from_claude_md(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text("# Rules\n\n- be kind\n", encoding="utf-8")
        body, src = core.import_source(tmp_path)
        assert src.name == "CLAUDE.md"
        assert "be kind" in body

    def test_import_strips_generated_marker(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text(
            GENERATED_MARKER + "\n\n# Rules\n\n- x\n", encoding="utf-8"
        )
        body, _ = core.import_source(tmp_path)
        assert GENERATED_MARKER not in body

    def test_import_priority(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text("claude", encoding="utf-8")
        (tmp_path / ".cursorrules").write_text("cursor", encoding="utf-8")
        body, src = core.import_source(tmp_path)
        assert src.name == "CLAUDE.md"

    def test_import_nothing_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            core.import_source(tmp_path)


class TestInit:
    def test_creates_template(self, tmp_path):
        r = core.ensure_agents_md(tmp_path)
        assert r.action == "created"
        assert (tmp_path / "AGENTS.md").is_file()
        # template is valid source: sync works right after init
        results = core.sync(tmp_path)
        assert results

    def test_no_overwrite(self, tmp_path):
        write_agents_md(tmp_path)
        r = core.ensure_agents_md(tmp_path)
        assert r.action == "unchanged"
        assert "# Rules" in (tmp_path / "AGENTS.md").read_text(encoding="utf-8")


class TestRender:
    def test_mdc_has_frontmatter(self):
        t = TARGETS["cursor"]
        out = render(t, "# x\n- rule\n")
        assert out.startswith("---\n")
        assert "alwaysApply: true" in out
        assert "rule" in out

    def test_markdown_no_frontmatter(self):
        t = TARGETS["claude"]
        out = render(t, "# x\n")
        assert not out.startswith("---")

    def test_walk_up_finds_source(self, tmp_path):
        write_agents_md(tmp_path)
        nested = tmp_path / "a" / "b" / "c"
        nested.mkdir(parents=True)
        found = core.walk_up(nested)
        assert found == tmp_path.resolve() or found == tmp_path
