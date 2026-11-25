"""Unattended prepare/conclude at the CLI boundary, without a model (result.json is written by the test)."""

import json
from pathlib import Path
import subprocess
import unittest

from test_changed import MARKER, MapFixture


class CiTests(MapFixture):
    def setUp(self):
        super().setUp()
        self.wiki = self.agents.parent
        self.work = Path(self.tmp.name) / "work"
        self.wgit("init", "-q")
        self.wgit("config", "user.email", "fixture@example.invalid")
        self.wgit("config", "user.name", "Fixture")
        self.wgit("add", ".")
        self.wgit("commit", "-qm", "map")

    def wgit(self, *args):
        result = subprocess.run(["git", "-C", str(self.wiki), *args], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def ci(self, command, *extra, expected=0):
        result = self.cli("ci.py", command, self.agents, "--work", self.work, *extra)
        self.assertEqual(result.returncode, expected, result.stderr or result.stdout)
        return result

    def plan(self):
        return json.loads((self.work / "prepare.json").read_text())

    def status(self):
        return json.loads((self.work / "status.json").read_text())

    def result(self, **fields):
        self.work.mkdir(exist_ok=True)
        (self.work / "result.json").write_text(json.dumps({"outcome": "updated", "summary": "s", "pages": [],
                                                           "limitations": [], **fields}))

    def change_source(self):
        self.write(self.repo / "src/old/file.ts", "export const version = 2;\n")
        self.git("commit", "-qam", "change")

    def test_unchanged_source_skips_the_model_and_concludes_no_change(self):
        self.ci("prepare")
        self.assertEqual(self.plan()["decision"], "skip")
        self.ci("conclude")
        self.assertEqual(self.status()["status"], "no_change")

    def test_changed_source_needs_the_model_and_records_the_range(self):
        self.change_source()
        self.ci("prepare")
        plan = self.plan()
        self.assertEqual(plan["decision"], "update")
        head = self.git("rev-parse", "HEAD").stdout.strip()
        self.assertEqual(plan["ranges"]["app"], {"from": self.sha, "to": head})
        self.assertIn("app/src/old/file.ts", (self.work / "brief.md").read_text())

    def test_structure_error_alone_needs_the_model(self):
        self.write(self.agents / "areas/old.md", MARKER + "# Old\n[gone](../missing.md)\n")
        self.wgit("commit", "-qam", "broken link")
        self.ci("prepare")
        self.assertEqual(self.plan()["decision"], "update")
        self.assertTrue(self.plan()["structure_errors"])

    def test_page_edit_concludes_updated_and_advances_the_baseline(self):
        self.change_source()
        self.ci("prepare")
        self.write(self.agents / "areas/old.md", MARKER + "# Old\nVersion two.\n")
        self.result(pages=["areas/old.md"])
        self.ci("conclude")
        status = self.status()
        self.assertEqual(status["status"], "updated")
        self.assertEqual(status["pages"], ["AGENTS/areas/old.md"])
        state = json.loads((self.agents / ".state.json").read_text())
        self.assertEqual(state["repos"]["app"]["sha"], self.git("rev-parse", "HEAD").stdout.strip())

    def test_missing_result_fails_without_advancing(self):
        self.change_source()
        self.ci("prepare")
        before = (self.agents / ".state.json").read_bytes()
        self.ci("conclude", expected=1)
        self.assertEqual(self.status()["status"], "failed")
        self.assertIn("result.json", self.status()["reason"])
        self.assertEqual((self.agents / ".state.json").read_bytes(), before)

    def test_model_reported_failure_is_passed_on(self):
        self.change_source()
        self.ci("prepare")
        self.result(outcome="failed", summary="could not read the router")
        self.ci("conclude", expected=1)
        self.assertEqual(self.status()["reason"], "could not read the router")

    def test_edit_outside_the_map_fails(self):
        self.change_source()
        self.ci("prepare")
        self.write(self.wiki / "notes.md", "owner notes\n")
        self.result()
        self.ci("conclude", expected=1)
        self.assertIn("notes.md", self.status()["reason"])

    def test_preexisting_change_outside_the_map_is_tolerated(self):
        self.write(self.wiki / "tasks/001/PLAN.md", "draft\n")
        self.change_source()
        self.ci("prepare")
        self.result()
        self.ci("conclude")
        self.assertNotIn("tasks/001/PLAN.md", self.status()["pages"])

    def test_source_edit_fails(self):
        self.change_source()
        self.ci("prepare")
        self.write(self.repo / "src/old/file.ts", "export const version = 3;\n")
        self.result()
        self.ci("conclude", expected=1)
        self.assertIn("source checkout changed", self.status()["reason"])

    def test_dirty_map_refuses_to_start(self):
        self.write(self.agents / "areas/old.md", MARKER + "# Edited by hand\n")
        self.ci("prepare", expected=1)
        self.assertIn("uncommitted", self.status()["reason"])

    def test_model_stop_reason_is_reported(self):
        self.change_source()
        self.ci("prepare")
        (self.work / "claude.json").write_text(json.dumps(
            {"type": "result", "subtype": "error_max_budget_usd", "total_cost_usd": 2.01, "num_turns": 40}))
        self.ci("conclude", expected=1)
        status = self.status()
        self.assertIn("error_max_budget_usd", status["reason"])
        self.assertEqual(status["model"]["total_cost_usd"], 2.01)


    def test_repair_pass_cost_is_added(self):
        self.change_source()
        self.ci("prepare")
        self.write(self.agents / "areas/old.md", MARKER + "# Old\nVersion two.\n")
        self.result()
        (self.work / "claude.json").write_text(json.dumps({"subtype": "success", "total_cost_usd": 0.2, "num_turns": 20}))
        (self.work / "claude-repair.json").write_text(json.dumps({"subtype": "success", "total_cost_usd": 0.05, "num_turns": 4}))
        self.ci("conclude")
        model = self.status()["model"]
        self.assertTrue(model["repair_pass"])
        self.assertAlmostEqual(model["total_cost_usd"], 0.25)
        self.assertEqual(model["num_turns"], 24)


if __name__ == "__main__":
    unittest.main()
