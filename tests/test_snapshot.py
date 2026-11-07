"""Source stability and durable-note preservation at the actual CLI boundary."""

import json
from pathlib import Path
import unittest

from test_changed import MARKER, MapFixture


class SnapshotTests(MapFixture):
    def capture(self):
        snapshot = Path(self.tmp.name) / "source-snapshot.json"
        result = self.cli("snapshot.py", "capture", self.agents, "--out", snapshot)
        self.assertEqual(result.returncode, 0, result.stderr)
        return snapshot

    def finalize(self, snapshot, expected=0):
        result = self.cli("snapshot.py", "finalize", self.agents, "--snapshot", snapshot)
        self.assertEqual(result.returncode, expected, result.stderr or result.stdout)
        return result

    def test_capture_leaves_baseline_unchanged(self):
        before = (self.agents / ".state.json").read_bytes()
        self.capture()
        self.assertEqual((self.agents / ".state.json").read_bytes(), before)

    def test_stable_source_finalizes_with_recorded_dirty_paths(self):
        self.write(self.repo / "src/old/file.ts", "export const version = 2;\n")
        snapshot = self.capture()
        self.finalize(snapshot)
        state = json.loads((self.agents / ".state.json").read_text())
        self.assertEqual(state["repos"]["app"]["dirty_files"], ["src/old/file.ts"])
        self.assertTrue(state["repos"]["app"]["dirty"])
        self.assertEqual(len(state["repos"]["app"]["fingerprint"]), 64)
        self.assertEqual(len(state["repos"]["app"]["dirty_hashes"]["src/old/file.ts"]), 64)
        self.assertIn("generator_version", state)

    def two_dirty_areas(self):
        self.write(self.repo / "src/new/other.ts", "export const other = 1;\n")
        self.git("add", ".")
        self.git("commit", "-qm", "second fixture area")
        self.state["repos"]["app"]["sha"] = self.git("rev-parse", "HEAD").stdout.strip()
        self.save_state()
        self.write(self.repo / "src/old/file.ts", "export const version = 2;\n")
        self.write(self.repo / "src/new/other.ts", "export const other = 2;\n")
        self.finalize(self.capture())

    def test_one_changed_file_does_not_reselect_unchanged_dirty_areas(self):
        self.two_dirty_areas()
        self.write(self.repo / "src/new/other.ts", "export const other = 3;\n")
        report = self.change_report()
        self.assertEqual(report["changed_files"], ["app/src/new/other.ts"])
        self.assertEqual(set(report["touched_areas"]), {"new"})

    def test_one_reverted_file_does_not_reselect_other_dirty_areas(self):
        self.two_dirty_areas()
        self.git("restore", "src/old/file.ts")
        report = self.change_report()
        self.assertEqual(report["changed_files"], ["app/src/old/file.ts"])
        self.assertEqual(set(report["touched_areas"]), {"old"})

    def test_committing_documented_dirty_content_does_not_repeat_writer_work(self):
        self.two_dirty_areas()
        self.git("add", ".")
        self.git("commit", "-qm", "commit already documented fixture edits")
        self.assertFalse(self.change_report()["needs_update"])

    def test_restoring_documented_deletion_selects_its_original_area(self):
        (self.repo / "src/old/file.ts").unlink()
        self.finalize(self.capture())
        state = json.loads((self.agents / ".state.json").read_text())
        self.assertEqual(state["repos"]["app"]["dirty_hashes"]["src/old/file.ts"], "deleted")
        self.git("restore", "src/old/file.ts")
        self.assertEqual(set(self.change_report()["touched_areas"]), {"old"})

    def test_legacy_state_needs_explicit_adoption(self):
        self.state["version"] = 2
        self.save_state()
        result = self.cli("snapshot.py", "capture", self.agents, "--out", self.root / "capture.json")
        self.assertEqual(result.returncode, 1)
        self.assertIn("version 3", result.stderr)

    def test_unchanged_dirty_snapshot_does_not_repeat_writer_work(self):
        self.write(self.repo / "src/old/file.ts", "export const version = 2;\n")
        self.finalize(self.capture())
        self.assertFalse(self.change_report()["needs_update"])
        self.git("restore", "src/old/file.ts")
        report = self.change_report()
        self.assertTrue(report["needs_update"])
        self.assertIn("old", report["touched_areas"])

    def test_source_change_during_writing_refuses_baseline_advance(self):
        snapshot = self.capture()
        before = (self.agents / ".state.json").read_bytes()
        self.write(self.repo / "src/old/file.ts", "export const version = 3;\n")
        result = self.finalize(snapshot, expected=1)
        self.assertIn("source changed", result.stderr)
        self.assertEqual((self.agents / ".state.json").read_bytes(), before)

    def test_changed_untracked_file_content_refuses_baseline_advance(self):
        path = self.repo / "src/old/new.ts"
        self.write(path, "export const value = 1;\n")
        snapshot = self.capture()
        self.write(path, "export const value = 2;\n")
        self.assertIn("source changed", self.finalize(snapshot, expected=1).stderr)

    def test_authored_svg_mutation_after_capture_refuses_baseline_advance(self):
        path = self.repo / "src/old/mark.svg"
        self.write(path, '<svg viewBox="0 0 10 10"/>\n')
        snapshot = self.capture()
        before = (self.agents / ".state.json").read_bytes()
        self.write(path, '<svg viewBox="0 0 20 20"/>\n')
        self.assertIn("source changed", self.finalize(snapshot, expected=1).stderr)
        self.assertEqual((self.agents / ".state.json").read_bytes(), before)

    def test_removed_keep_block_refuses_baseline_advance(self):
        page = self.agents / "areas/old.md"
        self.write(page, MARKER + "# Old\n<!-- keep -->\nOwner detail.\n<!-- /keep -->\n")
        snapshot = self.capture()
        before = (self.agents / ".state.json").read_bytes()
        self.write(page, MARKER + "# Old\n")
        self.assertIn("keep blocks", self.finalize(snapshot, expected=1).stderr)
        self.assertEqual((self.agents / ".state.json").read_bytes(), before)

    def test_keep_blocks_survive_generated_content_edit(self):
        page = self.agents / "areas/old.md"
        keep = "<!-- keep -->\nOwner detail.\n<!-- /keep -->\n"
        self.write(page, MARKER + "# Old\n" + keep)
        snapshot = self.capture()
        self.write(page, MARKER + "# Changed map\n" + keep)
        self.finalize(snapshot)

    def test_invalid_map_cannot_finalize(self):
        snapshot = self.capture()
        before = (self.agents / ".state.json").read_bytes()
        (self.agents / "contracts.md").unlink()
        self.assertIn("map check failed", self.finalize(snapshot, expected=1).stderr)
        self.assertEqual((self.agents / ".state.json").read_bytes(), before)

    def test_concurrent_baseline_change_is_not_overwritten(self):
        snapshot = self.capture()
        self.state["repos"]["app"]["dirty_files"] = ["someone-else.ts"]
        self.save_state()
        before = (self.agents / ".state.json").read_bytes()
        self.assertIn("baseline changed", self.finalize(snapshot, expected=1).stderr)
        self.assertEqual((self.agents / ".state.json").read_bytes(), before)

    def test_secret_files_do_not_enter_snapshot(self):
        self.write(self.repo / ".env.local", "NEVER_READ=this-is-a-test-fixture\n")
        self.write(self.repo / "secrets/credential.json", '{"test":"never-read"}\n')
        snapshot = self.capture()
        data = snapshot.read_text()
        self.assertNotIn("NEVER_READ", data)
        self.assertNotIn("credential.json", data)
        self.assertEqual(json.loads(data)["repos"]["app"]["dirty_files"], [])

    def test_single_repo_map_edits_do_not_change_source_snapshot(self):
        # Put the generated map inside the source repo, as in standalone mode.
        agents = self.repo / "docs/AGENTS"
        agents.parent.mkdir()
        self.agents.rename(agents)
        self.agents = agents
        self.root = self.repo
        self.state["repos"] = {".": self.state["repos"]["app"]}
        for area in self.state["areas"]:
            area["paths"] = [p.removeprefix("app/") for p in area["paths"]]
        self.save_state()
        snapshot = self.capture()
        self.write(agents / "areas/old.md", MARKER + "# Edited map\n")
        self.finalize(snapshot)


    def test_unknown_extension_movement_refuses_snapshot_advance(self):
        self.write(self.repo / "infra/main.tf", "old\n")
        snapshot = self.capture()
        self.write(self.repo / "infra/main.tf", "new\n")
        self.assertIn("source changed", self.finalize(snapshot, 1).stderr)

    def test_partial_finalize_keeps_unavailable_repo_baseline_and_never_claims_clean(self):
        old = {"sha": "a" * 40, "dirty": True, "dirty_files": ["old.proto"]}
        self.state["repos"]["offline"] = old
        self.save_state()
        self.write(self.agents / "areas/old.md", MARKER + "`offline/source.ts`\n[offline](../../../offline/source.ts)\n")
        self.write(self.repo / "src/old/file.ts", "changed\n")
        self.finalize(self.capture())
        state = json.loads((self.agents / ".state.json").read_text())
        self.assertEqual(state["repos"]["offline"], old)
        self.assertTrue(state["repos"]["app"]["dirty"])
        self.assertEqual(state["snapshot_status"], "partial")
        self.assertEqual(state["unavailable_repos"], ["offline"])
        report = self.change_report(2)
        self.assertEqual(report["freshness"], "partial")
        check = self.cli("check.py", self.agents, "--json")
        self.assertEqual(check.returncode, 2, check.stdout)
        self.assertEqual(json.loads(check.stdout)["structure"], "ok")

    def test_unmarked_file_removal_or_mutation_cannot_finalize(self):
        for filename in ("owner-notes.md", ".hidden-note", "design.custom"):
            with self.subTest(filename=filename):
                page = self.agents / filename
                self.write(page, "Handwritten bytes\n")
                snapshot = self.capture()
                before = (self.agents / ".state.json").read_bytes()
                page.unlink()
                self.assertIn("handwritten file", self.finalize(snapshot, 1).stderr)
                self.assertEqual((self.agents / ".state.json").read_bytes(), before)

    def test_unmarked_page_cannot_be_silently_adopted(self):
        page = self.agents / "areas/old.md"
        self.write(page, "Handwritten owner content\n")
        snapshot = self.capture()
        self.write(page, MARKER + "# Replaced\n")
        self.assertIn("handwritten file", self.finalize(snapshot, 1).stderr)

    def test_legacy_skip_and_keep_blocks_preserve_exact_crlf_bytes(self):
        page = self.agents / "areas/old.md"
        blocks = b"<!-- keep -->\r\nOwner\r\n<!-- /keep -->\r\n<!-- AUTOREGEN_SKIP_BEGIN -->\r\nLegacy\r\n<!-- AUTOREGEN_SKIP_END -->"
        page.write_bytes(MARKER.encode() + blocks)
        snapshot = self.capture()
        page.write_bytes(MARKER.encode() + b"# New generated text\n" + blocks)
        self.finalize(snapshot)
        snapshot = self.capture()
        page.write_bytes(page.read_bytes().replace(b"Legacy", b"Edited"))
        self.assertIn("keep blocks", self.finalize(snapshot, 1).stderr)

    def test_review_summary_is_preserved_without_inventing_evidence(self):
        review = {"pages": ["areas/old.md"], "ordinary_area": "old", "method": "self", "limitations": ["No independent check"]}
        self.state["review_summary"] = review
        self.save_state()
        self.finalize(self.capture())
        self.assertEqual(json.loads((self.agents / ".state.json").read_text())["review_summary"], review)

    def test_second_finalize_from_same_capture_is_rejected(self):
        snapshot = self.capture()
        self.finalize(snapshot)
        before = (self.agents / ".state.json").read_bytes()
        self.assertIn("baseline changed", self.finalize(snapshot, 1).stderr)
        self.assertEqual((self.agents / ".state.json").read_bytes(), before)


    def test_capture_cannot_overwrite_state_or_handwritten_file(self):
        for path in (self.agents / ".state.json", self.agents / "owner.md"):
            if path.name != ".state.json":
                self.write(path, "owner bytes\n")
            before = path.read_bytes()
            result = self.cli("snapshot.py", "capture", self.agents, "--out", path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("refusing to overwrite", result.stderr)
            self.assertEqual(path.read_bytes(), before)


    def test_ignored_watches_and_citations_track_mutation_but_ownership_does_not_expand_ignored(self):
        self.write(self.repo / ".gitignore", "local-inputs/\n")
        self.git("add", ".gitignore")
        self.git("commit", "-qm", "ignore local inputs")
        self.state["repos"]["app"]["sha"] = self.git("rev-parse", "HEAD").stdout.strip()
        self.state["areas"][0]["paths"].append("app/local-inputs/**")
        self.state["areas"][1]["watch"] = ["app/local-inputs/watched.*"]
        self.save_state()
        self.write(self.agents / "catches.md", MARKER + "`app/local-inputs/cited.proto`\n")
        for name in ("watched.proto", "cited.proto", "ownership-only.proto"):
            self.write(self.repo / "local-inputs" / name, "first\n")
        self.finalize(self.capture())
        state = json.loads((self.agents / ".state.json").read_text())
        self.assertEqual(state["repos"]["app"]["dirty_files"], ["local-inputs/cited.proto", "local-inputs/watched.proto"])
        for name in ("watched.proto", "cited.proto", "ownership-only.proto"):
            self.write(self.repo / "local-inputs" / name, "second\n")
        report = self.change_report()
        self.assertEqual(report["changed_files"], ["app/local-inputs/cited.proto", "app/local-inputs/watched.proto"])
        self.assertIn("new", report["touched_areas"])
        self.assertIn("catches.md", report["referenced_pages"])

    def test_ignored_dependency_expansion_prunes_secrets_cache_and_symlink_escapes(self):
        self.write(self.repo / ".gitignore", "local-inputs/\n")
        self.state["areas"][1]["watch"] = ["app/local-inputs/**"]
        self.save_state()
        for path in ("secrets/private.proto", "node_modules/generated.proto", ".cache/output.proto", "good.proto"):
            self.write(self.repo / "local-inputs" / path, "fixture\n")
        outside = self.root / "outside"
        outside.mkdir()
        self.write(outside / "external.proto", "outside\n")
        (self.repo / "local-inputs/escape").symlink_to(outside, target_is_directory=True)
        captured = json.loads(self.capture().read_text())
        self.assertEqual(captured["repos"]["app"]["dirty_files"], [".gitignore", "local-inputs/good.proto"])

    def test_unexplained_fingerprint_change_requires_full_review(self):
        self.finalize(self.capture())
        self.git("update-index", "--assume-unchanged", "src/old/file.ts")
        self.write(self.repo / "src/old/file.ts", "hidden change\n")
        report = self.change_report(2)
        self.assertIn("fingerprint", report["fallback_repos"]["app"])
        self.assertTrue(report["needs_update"])
        check = self.cli("check.py", self.agents)
        self.assertEqual(check.returncode, 2, check.stdout)

    def test_filemode_ignored_by_git_still_requires_review(self):
        self.finalize(self.capture())
        self.git("config", "core.filemode", "false")
        path = self.repo / "src/old/file.ts"
        path.chmod(path.stat().st_mode | 0o111)
        report = self.change_report(2)
        self.assertIn("fingerprint", report["fallback_repos"]["app"])


if __name__ == "__main__":
    unittest.main()
