"""Controlled source/state/page interleavings at the finalization boundary."""

from contextlib import redirect_stderr, redirect_stdout
import fcntl
import io
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from test_changed import MapFixture, SCRIPTS

sys.path.insert(0, str(SCRIPTS))
import snapshot


class FinalizeRaceTests(MapFixture):
    def captured(self):
        path = Path(self.tmp.name) / "capture.json"
        result = self.cli("snapshot.py", "capture", self.agents, "--out", path)
        self.assertEqual(result.returncode, 0, result.stderr)
        return path

    def test_competing_finalizer_lock_cannot_overwrite_baseline(self):
        captured = self.captured()
        before = (self.agents / ".state.json").read_bytes()
        with (self.agents / ".state.lock").open("a") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            result = self.cli("snapshot.py", "finalize", self.agents, "--snapshot", captured)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual((self.agents / ".state.json").read_bytes(), before)

    def test_movement_after_structural_check_cannot_advance_baseline(self):
        for kind in ("source", "state", "managed page"):
            with self.subTest(kind=kind):
                captured = self.captured()
                baseline_path = self.agents / ".state.json"
                expected = baseline_path.read_bytes()
                run = subprocess.run

                def mutate_after_check(command, **kwargs):
                    nonlocal expected
                    result = run(command, **kwargs)
                    if any(str(arg).endswith("check.py") for arg in command):
                        if kind == "source":
                            self.write(self.repo / "src/old/file.ts", "concurrent source\\n")
                        elif kind == "state":
                            state = json.loads(expected)
                            state["generated"] = "another run"
                            baseline_path.write_text(json.dumps(state))
                            expected = baseline_path.read_bytes()
                        else:
                            page = self.agents / "areas/old.md"
                            self.write(page, page.read_text() + "concurrent page edit\\n")
                    return result

                stderr = io.StringIO()
                with patch.object(sys, "argv", ["snapshot.py", "finalize", str(self.agents), "--snapshot", str(captured), "--root", str(self.root)]), patch.object(snapshot.subprocess, "run", side_effect=mutate_after_check), redirect_stderr(stderr), redirect_stdout(io.StringIO()):
                    code = snapshot.main()
                self.assertEqual(code, 1, stderr.getvalue())
                self.assertIn("changed during final checks", stderr.getvalue())
                self.assertEqual(baseline_path.read_bytes(), expected)


    def test_concurrent_state_edit_after_read_cannot_pair_new_bytes_with_old_parsed_state(self):
        captured = self.captured()
        baseline_path = self.agents / ".state.json"
        read = Path.read_bytes
        changed = False
        expected = None

        def mutate_after_read(path):
            nonlocal changed, expected
            data = read(path)
            if path == baseline_path and not changed:
                changed = True
                state = json.loads(data)
                state["review_summary"] = {"pages": ["index.md"], "ordinary_area": None, "method": "self", "limitations": ["concurrent owner evidence"]}
                path.write_text(json.dumps(state))
                expected = read(path)
            return data

        stderr = io.StringIO()
        with patch.object(sys, "argv", ["snapshot.py", "finalize", str(self.agents), "--snapshot", str(captured), "--root", str(self.root)]), patch.object(Path, "read_bytes", mutate_after_read), redirect_stderr(stderr), redirect_stdout(io.StringIO()):
            code = snapshot.main()
        self.assertEqual(code, 1, stderr.getvalue())
        self.assertIn("state changed", stderr.getvalue())
        self.assertEqual(baseline_path.read_bytes(), expected)
