"""Independent structural-check regressions at the CLI boundary, with real Git fixtures."""

import json
import shutil
import unittest

from test_changed import MARKER, MapFixture


class CheckTests(MapFixture):
    def check(self, expected=0, *args):
        result = self.cli("check.py", self.agents, *args)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stdout + result.stderr)
        return result.stdout

    def test_complete_valid_map_passes(self):
        output = self.check()
        self.assertIn("0 errors", output)

    def adopt_rules(self):
        self.state["project_rules"] = "wiki-test/rules/development.md"
        self.save_state()
        self.rules = self.root / self.state["project_rules"]
        self.write(self.rules, "# Owner rules\nKeep solutions simple.\n")
        index = self.agents / "index.md"
        self.write(index, index.read_text() + "[Rules](../rules/development.md)\n")

    def test_project_rules_and_handwritten_notes_are_read_only(self):
        self.adopt_rules()
        entry = self.repo / "AGENTS.md"
        body = ("# Handwritten\n<!-- keep -->Exact notes<!-- /keep -->\n"
                "<!-- wiki-system: project-rules -->\n"
                "Read [Rules](../wiki-test/rules/development.md).\n"
                "<!-- /wiki-system: project-rules -->\nTail stays.\n")
        self.write(entry, body)
        self.write(self.repo / "CLAUDE.md", "See [AGENTS.md](AGENTS.md).\n")
        policy = self.rules.read_bytes()
        self.check(2)
        self.assertEqual(entry.read_text(), body)
        self.assertEqual(self.rules.read_bytes(), policy)

    def test_declared_policy_cannot_silently_disappear(self):
        self.adopt_rules()
        self.rules.unlink()
        self.assertIn("project_rules: file missing", self.check(1))

    def test_policy_requires_index_and_generated_claude_links(self):
        self.adopt_rules()
        index = self.agents / "index.md"
        original = index.read_text()
        self.write(index, original.replace("[Rules](../rules/development.md)", ""))
        self.assertIn("index.md: missing project_rules", self.check(1))
        self.write(index, original)
        claude = self.root / "CLAUDE.md"
        self.write(claude, MARKER + "[Map](wiki-test/AGENTS/index.md)\n")
        self.assertIn("CLAUDE.md: missing project_rules", self.check(1))
        self.write(claude, claude.read_text() + "[Rules](wiki-test/rules/development.md#approach)\n")
        self.check()

    def test_managed_policy_pointer_must_resolve_to_declared_file(self):
        self.adopt_rules()
        entry = self.repo / "AGENTS.md"
        for body, error in [
            ("<!-- wiki-system: project-rules -->[Rules](../wiki-test/AGENTS/index.md)<!-- /wiki-system: project-rules -->", "missing project_rules"),
            ("<!-- wiki-system: project-rules -->Unclosed", "malformed project-rules"),
            ("<!-- /wiki-system: project-rules --><!-- wiki-system: project-rules -->", "malformed project-rules"),
        ]:
            with self.subTest(body=body):
                self.write(entry, body)
                self.assertIn(error, self.check(1))

    def test_owner_policy_cannot_be_a_generated_page(self):
        self.state["project_rules"] = "wiki-test/AGENTS/catches.md"
        self.save_state()
        self.assertIn("owner policy must live outside", self.check(1))

    def test_invalid_policy_paths_fail_without_traceback(self):
        for path in [None, [], "../outside.md", "/outside.md", "secrets/rules.md", "rules.json"]:
            with self.subTest(path=path):
                self.state["project_rules"] = path
                self.save_state()
                self.assertIn("project_rules must be", self.check(1))

    def test_empty_map_cannot_pass(self):
        for page in self.agents.rglob("*.md"):
            page.unlink()
        self.check(1)

    def test_missing_standard_page_fails(self):
        (self.agents / "catches.md").unlink()
        self.assertIn("required map page missing", self.check(1))

    def test_malformed_state_fails_without_traceback(self):
        states = [None, [], {"skill": "wiki-system", "version": 3},
                  {**self.state, "areas": [None]},
                  {**self.state, "repos": {"app": None}},
                  {**self.state, "areas": [{"id": [], "page": None, "paths": {}}]}]
        for state in states:
            with self.subTest(state=state):
                self.write(self.agents / ".state.json", json.dumps(state))
                self.check(1)
        self.write(self.agents / ".state.json", "{not valid JSON")
        self.check(1)

    def test_duplicate_area_identity_and_page_fail(self):
        self.state["areas"].append(dict(self.state["areas"][0]))
        self.save_state()
        self.assertIn("duplicate", self.check(1))

    def test_missing_prefixed_multi_repo_path_fails(self):
        self.write(self.agents / "areas/old.md", MARKER + "# Old\n`app/src/old/missing.ts`\n")
        self.assertIn("cited path does not exist", self.check(1))

    def test_misspelled_repo_prefix_cannot_hide_missing_path(self):
        self.write(self.agents / "areas/old.md", MARKER + "# Old\n`appp/src/old/file.ts`\n")
        self.assertIn("cited path does not exist", self.check(1))

    def test_invalid_repo_exclusions_fail_cleanly(self):
        self.state["excluded_repos"] = "app"
        self.save_state()
        self.assertIn("excluded_repos", self.check(1))

    def test_legacy_line_suffix_keeps_existing_file_extension(self):
        self.write(self.agents / "areas/old.md", MARKER + "# Old\n`app/src/old/file.ts:1`\n")
        output = self.check()
        self.assertIn("line-number anchors", output)
        self.assertNotIn("cited path does not exist", output)

    def test_large_page_budget_is_advisory(self):
        self.write(self.agents / "areas/old.md", MARKER + " ".join(["word"] * 901) + "\n")
        self.assertIn("over soft budget 600", self.check())

    def test_keep_notes_are_preserved_outside_generated_word_budget(self):
        text = MARKER + "# Old\n<!-- keep -->\n" + " ".join(["note"] * 1000) + "\n<!-- /keep -->\n"
        self.write(self.agents / "areas/old.md", text)
        self.check()
        self.assertEqual((self.agents / "areas/old.md").read_text(), text)

    def test_malformed_keep_blocks_fail(self):
        bodies = ["<!-- keep -->\nUnclosed note.\n",
                  "<!-- /keep -->\nStray closer.\n",
                  "<!-- keep --><!-- keep -->nested<!-- /keep --><!-- /keep -->\n"]
        for body in bodies:
            with self.subTest(body=body):
                self.write(self.agents / "areas/old.md", MARKER + "# Old\n" + body)
                self.assertIn("keep blocks", self.check(1))

    def test_missing_markdown_target_fails(self):
        self.write(self.agents / "areas/old.md", MARKER + "# Old\n[Other](missing.md)\n")
        self.assertIn("broken link", self.check(1))

    def test_generated_claude_without_map_pointer_fails(self):
        self.write(self.root / "CLAUDE.md", MARKER + "# App\n")
        self.assertIn("CLAUDE.md", self.check(1))

    def test_generated_claude_broken_map_link_fails(self):
        self.write(self.root / "CLAUDE.md", MARKER + "# App\n[Map](missing/AGENTS/index.md)\n")
        self.assertIn("broken link", self.check(1))

    def test_generated_claude_budget_is_advisory(self):
        self.write(self.root / "CLAUDE.md", MARKER + "[Map](wiki-test/AGENTS/index.md)\n" + "line\n" * 61)
        self.assertIn("over 60", self.check())

    def test_missing_git_checkout_cannot_pass(self):
        shutil.rmtree(self.repo / ".git")
        self.assertIn("repo unavailable", self.check(2))

    def test_coverage_includes_html_yaml_json_and_keeps_test_doc_evidence_separate(self):
        for rel, content in [("web/index.html", "<main>Page</main>\n"),
                             ("ops/new/settings.yaml", "enabled: true\n"),
                             ("data/schema.json", "{}\n"),
                             ("tests/auth.test.ts", "test('auth', () => {});\n"),
                             ("docs/guide.md", "# Local guide\n")]:
            self.write(self.repo / rel, content)
        output = self.check(2, "--coverage")
        self.assertIn("uncovered: app/web/", output)
        self.assertIn("uncovered: app/ops/new/", output)
        self.assertIn("uncovered: app/data/", output)
        self.assertNotIn("uncovered: app/tests/", output)
        self.assertNotIn("uncovered: app/docs/", output)
        self.assertIn("navigation evidence", output)
        self.assertIn("app/tests/auth.test.ts", output)
        self.assertIn("app/docs/guide.md", output)


    def test_index_only_map_is_valid_and_unmanaged_notes_are_not_checked(self):
        self.state["areas"] = []
        self.state["managed_pages"] = ["index.md"]
        self.save_state()
        self.write(self.agents / "index.md", MARKER + "# Navigation\n")
        self.write(self.agents / "owner-notes.md", "Handwritten [old](missing.md)\n")
        self.check()

    def test_managed_pages_contract_rejects_bad_shapes(self):
        for pages in (None, [], ["index.md", "index.md"], ["../index.md"], ["index.md", {}]):
            with self.subTest(pages=pages):
                self.state["managed_pages"] = pages
                self.save_state()
                self.assertIn("managed_pages", self.check(1))

    def test_public_check_reports_stale_separately_and_never_writes(self):
        self.write(self.repo / "new.unknown", "new source\n")
        before = {p: p.read_bytes() for p in self.agents.rglob("*") if p.is_file()}
        output = self.check(2)
        self.assertIn("Structure: ok", output)
        self.assertIn("Freshness: stale", output)
        self.assertEqual(before, {p: p.read_bytes() for p in self.agents.rglob("*") if p.is_file()})

    def test_context_blocks_validate_only_owned_links(self):
        entry = self.repo / "AGENTS.md"
        self.write(entry, "Owner [historical](missing.md)\n<!-- wiki-system: context -->\n"
                   "[Map](../wiki-test/AGENTS/index.md)\n<!-- /wiki-system: context -->\n")
        self.check(2)
        self.write(entry, entry.read_text().replace("../wiki-test/AGENTS/index.md", "../missing/index.md"))
        self.assertIn("broken link", self.check(1))

    def test_custom_map_directory_uses_explicit_root(self):
        custom = self.root / "deep" / "custom" / "navigation"
        custom.parent.mkdir(parents=True)
        self.agents.rename(custom)
        self.agents = custom
        self.check()

    def test_no_baseline_requires_full_review(self):
        self.state["repos"]["app"]["sha"] = None
        self.save_state()
        output = self.check(2)
        self.assertIn("Full source review required", output)
        self.assertIn("no baseline SHA", output)


class SingleRepoCheckTests(MapFixture):
    def setUp(self):
        super().setUp()
        old_agents = self.agents
        self.agents = self.repo / "docs" / "AGENTS"
        shutil.copytree(old_agents, self.agents)
        self.root = self.repo
        self.state["repos"] = {".": {"sha": self.sha, "dirty": False, "dirty_files": []}}
        for area in self.state["areas"]:
            area["paths"] = [path.removeprefix("app/") for path in area["paths"]]
        self.save_state()

    def test_valid_single_repo_map_passes(self):
        result = self.cli("check.py", self.agents)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_root_file_fails(self):
        self.write(self.agents / "areas/old.md", MARKER + "# Old\n`missing.ts`\n")
        result = self.cli("check.py", self.agents)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing.ts", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_missing_top_level_directory_path_fails(self):
        self.write(self.agents / "areas/old.md", MARKER + "# Old\n`typo/missing.ts`\n")
        result = self.cli("check.py", self.agents)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("typo/missing.ts", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_existing_root_file_is_accepted(self):
        self.write(self.agents / "areas/old.md", MARKER + "# Old\n`package.json`\n")
        result = self.cli("check.py", self.agents)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
