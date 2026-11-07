"""Offline integration regressions for map change planning, using real temporary Git repos."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
MARKER = "<!-- wiki-system: generated from code; refresh with /wiki-system update -->\n"


class MapFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="wiki-system-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "app"
        self.agents = self.root / "wiki-test" / "AGENTS"
        self.repo.mkdir()
        self.agents.mkdir(parents=True)
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        self.write(self.repo / "src/old/file.ts", "export const version = 1;\n")
        self.write(self.repo / "package.json", '{"scripts":{"test":"old-test"}}\n')
        self.git("add", ".")
        self.git("commit", "-qm", "isolated fixture")
        self.sha = self.git("rev-parse", "HEAD").stdout.strip()
        self.state = {
            "skill": "wiki-system", "version": 3,
            "repos": {"app": {"sha": self.sha, "dirty": False, "dirty_files": []}},
            "managed_pages": ["index.md", "catalog.md", "contracts.md", "catches.md", "areas/old.md", "areas/new.md"],
            "areas": [
                {"id": "old", "title": "Old", "page": "areas/old.md", "paths": ["app/src/old/**"]},
                {"id": "new", "title": "New", "page": "areas/new.md", "paths": ["app/src/new/**"]},
                {"id": "contracts", "title": "Contracts", "page": "contracts.md", "paths": ["app/config/**"]},
            ],
            "unmapped_ok": [],
        }
        self.save_state()
        for page in ["index.md", "catalog.md", "contracts.md", "catches.md", "areas/old.md", "areas/new.md"]:
            self.write(self.agents / page, MARKER + "# Map\n")
        self.write(self.agents / "index.md", MARKER + "# Map\n" + "\n".join(
            f"- [{p}]({p})" for p in ["catalog.md", "contracts.md", "catches.md", "areas/old.md", "areas/new.md"]
        ) + "\n")

    @staticmethod
    def write(path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def save_state(self):
        self.write(self.agents / ".state.json", json.dumps(self.state))

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def cli(self, script, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *map(str, args), "--root", str(self.root)], capture_output=True, text=True, timeout=30)

    def change_report(self, expected=0):
        result = self.cli("changed.py", self.agents, "--json")
        self.assertEqual(result.returncode, expected, result.stderr or result.stdout)
        return json.loads(result.stdout)


class ChangedTests(MapFixture):
    def test_unchanged_tree_reports_clean(self):
        report = self.change_report()
        self.assertFalse(report["needs_update"])
        self.assertEqual(report["changed_files"], [])

    def test_rename_pulls_in_both_owner_areas(self):
        (self.repo / "src/new").mkdir()
        self.git("mv", "src/old/file.ts", "src/new/file.ts")
        report = self.change_report()
        self.assertEqual(set(report["touched_areas"]), {"old", "new"})
        self.assertEqual(report["changed_files"], ["app/src/new/file.ts", "app/src/old/file.ts"])

    def test_dirty_file_reverted_since_documentation_still_needs_review(self):
        self.state["repos"]["app"].update(dirty=True, dirty_files=["src/old/file.ts"])
        self.save_state()
        report = self.change_report()
        self.assertTrue(report["needs_update"])
        self.assertIn("old", report["touched_areas"])

    def test_legacy_dirty_baseline_demands_full_fallback(self):
        self.state["repos"]["app"] = {"sha": self.sha, "dirty": True}
        self.save_state()
        report = self.change_report(expected=2)
        self.assertIn("app", report["fallback_repos"])
        self.assertTrue(report["needs_update"])

    def test_unusable_baseline_does_not_report_success(self):
        self.state["repos"]["app"]["sha"] = "0" * 40
        self.save_state()
        report = self.change_report(expected=2)
        self.assertIn("app", report["fallback_repos"])

    def test_commands_change_needs_update_even_without_touched_area(self):
        self.write(self.repo / "package.json", '{"scripts":{"test":"new-test"}}\n')
        report = self.change_report()
        self.assertTrue(report["needs_update"])
        self.assertEqual(report["touched_areas"], {})
        self.assertEqual(report["index_hints"], ["app/package.json"])

    def test_unmapped_html_and_ci_configuration_are_reported(self):
        self.write(self.repo / "src/new.html", "<h1>New entry</h1>\n")
        self.write(self.repo / ".github/workflows/ci.yml", "name: CI\n")
        report = self.change_report()
        self.assertEqual(report["unmapped"], ["app/.github/workflows/ci.yml", "app/src/new.html"])
        self.assertTrue(report["needs_update"])

    def test_reference_pulls_in_page_outside_ownership_globs(self):
        self.write(self.agents / "areas/new.md", MARKER + "# New\nShared source: `app/src/old/file.ts`.\n")
        self.write(self.agents / "catches.md", MARKER + "# Catches\nRead `app/src/old/`.\n")
        self.write(self.repo / "src/old/file.ts", "export const version = 2;\n")
        report = self.change_report()
        self.assertEqual(set(report["touched_areas"]), {"old", "new"})
        self.assertIn("catches.md", report["referenced_pages"])

    def test_markdown_code_link_pulls_in_page_outside_ownership(self):
        self.write(self.agents / "areas/new.md", MARKER + "# New\n[shared](../../../app/src/old/file.ts)\n")
        self.write(self.repo / "src/old/file.ts", "export const version = 2;\n")
        report = self.change_report()
        self.assertIn("new", report["touched_areas"])

    def test_watch_glob_pulls_in_dependent_area(self):
        self.state["areas"][1]["watch"] = ["app/src/old/**"]
        self.save_state()
        self.write(self.repo / "src/old/file.ts", "export const version = 2;\n")
        self.assertIn("new", self.change_report()["touched_areas"])

    def test_authored_svg_change_selects_owner_and_referencing_page(self):
        self.write(self.repo / "src/old/mark.svg", '<svg viewBox="0 0 10 10"/>\n')
        self.git("add", ".")
        self.git("commit", "-qm", "authored SVG fixture")
        self.state["repos"]["app"]["sha"] = self.git("rev-parse", "HEAD").stdout.strip()
        self.save_state()
        self.write(self.agents / "areas/new.md", MARKER + "# New\nBrand source: `app/src/old/mark.svg`.\n")
        self.write(self.repo / "src/old/mark.svg", '<svg viewBox="0 0 20 20"/>\n')
        report = self.change_report()
        self.assertEqual(report["changed_files"], ["app/src/old/mark.svg"])
        self.assertEqual(set(report["touched_areas"]), {"old", "new"})
        self.assertIn("areas/new.md", report["referenced_pages"])

    def test_nul_parsing_handles_newline_in_filename(self):
        self.write(self.repo / "src/old/line\nbreak.ts", "export const x = 1;\n")
        report = self.change_report()
        self.assertEqual(report["changed_files"], ["app/src/old/line\nbreak.ts"])

    def test_new_repo_prevents_clean_report_until_mapped_or_excluded(self):
        sibling = self.root / "new-app"
        sibling.mkdir()
        subprocess.run(["git", "-C", str(sibling), "init", "-q"], check=True, capture_output=True)
        report = self.change_report()
        self.assertEqual(report["discovered_repos"], ["new-app"])
        self.assertTrue(report["needs_update"])
        self.state["excluded_repos"] = ["new-app"]
        self.save_state()
        self.assertFalse(self.change_report()["needs_update"])

    def test_missing_repo_is_fallback_not_clean(self):
        self.repo.rename(self.root / "moved-app")
        self.assertIn("app", self.change_report(expected=2)["fallback_repos"])


    def test_unknown_extensions_and_extensionless_files_select_owners_watchers_and_citations(self):
        self.state["areas"][1]["watch"] = ["app/infra/**"]
        self.save_state()
        self.write(self.agents / "catches.md", MARKER + "`app/infra/main.tf` and `app/LICENSE`\n")
        for path in ("src/old/service.proto", "infra/main.tf", "LICENSE"):
            self.write(self.repo / path, "first-party source\n")
        report = self.change_report()
        self.assertEqual(report["changed_files"], ["app/LICENSE", "app/infra/main.tf", "app/src/old/service.proto"])
        self.assertEqual(set(report["touched_areas"]), {"old", "new"})
        self.assertEqual(report["referenced_pages"]["catches.md"], ["app/LICENSE", "app/infra/main.tf"])

    def test_generated_sensitive_and_cache_files_stay_excluded(self):
        for path in (".env.private", "secrets/key.custom", ".cache/item.custom", "generated/out.proto", "dist/file.ts"):
            self.write(self.repo / path, "fixture only\n")
        self.assertFalse(self.change_report()["needs_update"])

    def test_encoded_angle_and_title_links_share_dependency_and_check_parser(self):
        self.write(self.repo / "src/old/file with space.proto", "source\n")
        self.write(self.agents / "areas/new.md", MARKER + '[source](<../../../app/src/old/file%20with%20space.proto#thing> "Title")\n')
        report = self.change_report()
        self.assertIn("new", report["touched_areas"])
        check = self.cli("check.py", self.agents, "--structure-only")
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_worktree_git_file_is_a_supported_checkout(self):
        worktree = self.root / "worktree"
        self.git("worktree", "add", "--detach", str(worktree))
        self.state["excluded_repos"] = ["app"]
        self.state["repos"] = {"worktree": self.state["repos"]["app"]}
        for area in self.state["areas"]:
            area["paths"] = [p.replace("app/", "worktree/") for p in area["paths"]]
        self.save_state()
        self.write(worktree / "src/old/file.ts", "changed\n")
        report = self.change_report()
        self.assertEqual(report["changed_files"], ["worktree/src/old/file.ts"])
        self.assertEqual(report["fallback_repos"], {})


    def test_explicit_generated_contracts_are_not_filtered_out(self):
        self.state["areas"][1]["watch"] = ["app/generated/watched.proto"]
        self.save_state()
        self.write(self.agents / "catches.md", MARKER + "`app/generated/cited.proto`\n")
        for path in ("src/old/database.types.ts", "generated/watched.proto", "generated/cited.proto", "generated/ignored.proto"):
            self.write(self.repo / path, "contract\n")
        report = self.change_report()
        self.assertEqual(report["changed_files"], ["app/generated/cited.proto", "app/generated/watched.proto", "app/src/old/database.types.ts"])
        self.assertEqual(set(report["touched_areas"]), {"old", "new"})
        self.assertIn("catches.md", report["referenced_pages"])


    def test_custom_docs_checkout_is_excluded_by_identity_but_wiki_named_source_is_discovered(self):
        subprocess.run(["git", "-C", str(self.agents.parent), "init", "-q"], check=True, capture_output=True)
        moved_docs = self.root / "reference"
        self.agents.parent.rename(moved_docs)
        self.agents = moved_docs / "AGENTS"
        for name in ("wiki-client", ".scratch", "vendor", "node_modules", ".cache"):
            sibling = self.root / name
            sibling.mkdir()
            subprocess.run(["git", "-C", str(sibling), "init", "-q"], check=True, capture_output=True)
        report = self.change_report()
        self.assertEqual(report["discovered_repos"], ["wiki-client"])


if __name__ == "__main__":
    unittest.main()
