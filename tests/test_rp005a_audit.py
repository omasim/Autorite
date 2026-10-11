import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
from research.RP005A import audit, replay
from research.RP005A.contract import INPUTS, OUTPUTS, FREEZE_PATH


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


runner = module("rp005a_run", "scripts/run-rp005a-audit.py")
checker = module("rp005a_check", "scripts/check-rp005a-audit.py")
FIXTURES = json.loads((ROOT / "research/RP005A/RP005A_FIXTURES.json").read_text())
CONFIG = json.loads((ROOT / "research/RP005A/RP005A_AUDIT_CONFIG.json").read_text())


def rows():
    return [list(function(FIXTURES, CONFIG))
            for function in (audit.iter_planner, audit.iter_pairs, audit.iter_structural)]


def stream(values):
    return io.StringIO("".join(replay.canonical(v) + "\n" for v in values))


def verify(values):
    return replay.replay(*(stream(v) for v in values), FIXTURES, CONFIG)


def fake_source(root):
    originals = {}
    for name in INPUTS:
        data = (ROOT / name).read_bytes()
        originals[name] = data
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    frozen = {"version": "0.1", "source_commit": "0" * 40,
              "input_sha256": {n: hashlib.sha256(v).hexdigest() for n, v in originals.items()},
              "configuration": CONFIG}
    (root / FREEZE_PATH).write_text(replay.canonical(frozen) + "\n")
    return frozen, originals


class AuditPreparationTests(unittest.TestCase):
    def test_frozen_configuration_rejects_numeric_coercion_and_scope_drift(self):
        replay.check_config(CONFIG)
        for key, value in (("wall_seconds", 60.0), ("expected_pair_rows", True),
                           ("horizons", [1, 2, 3]), ("targets", ["t1"]),
                           ("arms", ["restricted", "unrestricted"])):
            bad = copy.deepcopy(CONFIG)
            bad[key] = value
            with self.assertRaises(ValueError):
                replay.check_config(bad)

    def test_independent_rows_match_disclosed_controls(self):
        for case in FIXTURES["cases"]:
            graph = replay.rebuild(case)
            for control in case["expected"]:
                for arm in CONFIG["arms"]:
                    expected = replay.planner_row(graph, case["id"], control["horizon"], arm, CONFIG, 0)
                    replay.verify_row(audit.make_planner_row(case, control["horizon"], arm, CONFIG, 0), expected)
                    key = "restricted" if arm == "restricted" else "baseline"
                    self.assertEqual(expected["endpoint"], control[key + "_endpoint"])
                    self.assertEqual(expected["primary_count"], control[key + "_primary"])

    def test_complete_in_memory_roundtrip_is_only_disclosed_calibration(self):
        values = rows()
        independent = verify(values)
        self.assertEqual(independent, audit.summarize(*values, CONFIG))
        self.assertEqual((independent["planner_rows"], independent["paired_comparisons"],
                          independent["structural_sources"], independent["ordered_pairs_per_inclusion_family"]),
                         (24, 12, 35, 313))

    def test_planner_corruption_targets_scores_budget_and_types_rejected(self):
        case = FIXTURES["cases"][1]
        expected = replay.planner_row(replay.rebuild(case), "V1", 2, "restricted", CONFIG, 0)
        for key, value in (("ordinal", True), ("denominator", 3), ("primary_count", 3.0),
                           ("future_budget", 2), ("primary_targets", ["t1", "t2"]),
                           ("action_scores", [{"destination": "a", "score": 2}]),
                           ("removed_edges", []), ("case_hint", "benefit")):
            bad = copy.deepcopy(expected)
            bad[key] = value
            with self.assertRaises(ValueError):
                replay.verify_row(bad, expected)

    def test_pair_ratio_and_selection_deletion_corruption_rejected(self):
        case = FIXTURES["cases"][3]
        a = replay.planner_row(replay.rebuild(case), "C0", 1, "unrestricted", CONFIG, 0)
        b = replay.planner_row(replay.rebuild(case), "C0", 1, "restricted", CONFIG, 1)
        expected = replay.pair_row(a, b, 0)
        self.assertEqual(expected["primary_difference"], {"numerator": -1, "denominator": 5})
        for key, value in (("deletion_difference", {"numerator": 0, "denominator": 1}),
                           ("primary_difference", {"numerator": -2, "denominator": 10}),
                           ("planner_ordinals", [1, 0]), ("direction", "positive")):
            bad = copy.deepcopy(expected)
            bad[key] = value
            with self.assertRaises(ValueError):
                replay.verify_row(bad, expected)

    def test_structural_raw_and_budget_certificates_cannot_be_coerced(self):
        case = FIXTURES["cases"][0]
        expected = replay.structural_row(replay.rebuild(case), "V0", "s", CONFIG, 0)
        for key, value in (("inclusion", 1), ("lost_targets", []),
                           ("ordered_pairs_checked", 7), ("restricted_reachable", ["s"]),
                           ("underlying_budget_reachable", [])):
            bad = copy.deepcopy(expected)
            bad[key] = value
            with self.assertRaises(ValueError):
                replay.verify_row(bad, expected)

    def test_missing_duplicate_extra_and_reordered_streams_rejected(self):
        for family in range(3):
            for mutation in ("missing", "duplicate", "extra", "order"):
                values = rows()
                if mutation == "missing": values[family].pop()
                if mutation == "duplicate": values[family][1] = values[family][0]
                if mutation == "extra": values[family].append(values[family][-1])
                if mutation == "order": values[family][0], values[family][1] = values[family][1], values[family][0]
                with self.assertRaises(ValueError):
                    verify(values)

    def test_independent_graph_validation_cycle_reward_target_and_restriction(self):
        for mutation in ("cycle", "reward", "target", "restriction"):
            case = copy.deepcopy(FIXTURES["cases"][0])
            if mutation == "cycle": case["edges"].append({"from": "a", "to": "s", "reward": 0})
            if mutation == "reward": case["edges"][0]["reward"] = True
            if mutation == "target": case["targets"].append("a")
            if mutation == "restriction": case["removed"] = [["a", "b"]]
            with self.assertRaises(ValueError):
                replay.rebuild(case)

    def test_guard_stops_before_any_target_output(self):
        def stop():
            raise RuntimeError("engineering stop")
        for function in (audit.iter_planner, audit.iter_pairs, audit.iter_structural):
            with self.assertRaisesRegex(RuntimeError, "engineering stop"):
                next(function(FIXTURES, CONFIG, stop))
        with self.assertRaisesRegex(RuntimeError, "engineering stop"):
            replay.replay([], [], [], FIXTURES, CONFIG, stop)

    def test_strict_json_rejects_duplicate_keys_and_nonfinite_numbers(self):
        for text in ('{"ordinal":0,"ordinal":1}', '{"value":NaN}', '{"value":Infinity}'):
            with self.assertRaises(ValueError):
                replay.strict_loads(text)

    def test_reviewed_input_hash_drift_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            freeze, original = fake_source(root)
            with mock.patch.object(runner.subprocess, "check_output", side_effect=lambda cmd, **kw: original[cmd[-1].split(":", 1)[1]]):
                runner.verify_freeze(root, freeze)
                (root / INPUTS[0]).write_text("changed protocol\n")
                with self.assertRaisesRegex(ValueError, "differs from reviewed freeze"):
                    runner.verify_freeze(root, freeze)

    def test_preflight_requires_authorization_committed_freeze_and_fresh_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            freeze, _ = fake_source(root)
            note = "engineering preflight only"
            with mock.patch.object(runner, "ROOT", root), mock.patch.object(runner.sys, "version_info", (3, 11)), mock.patch.object(runner, "verify_freeze"):
                frozen = (root / FREEZE_PATH).read_bytes()
                with mock.patch.object(runner.subprocess, "check_output", side_effect=[b"", frozen]):
                    self.assertEqual(runner.preflight(CONFIG["run_id"], note), freeze)
                with self.assertRaisesRegex(ValueError, "authorization"):
                    runner.preflight(CONFIG["run_id"], "")
                with mock.patch.object(runner.subprocess, "check_output", side_effect=[b"", b"different"]):
                    with self.assertRaisesRegex(ValueError, "freeze must be committed"):
                        runner.preflight(CONFIG["run_id"], note)
                (root / "research/RP005A/runs" / CONFIG["run_id"]).mkdir(parents=True)
                with mock.patch.object(runner.subprocess, "check_output", side_effect=[b"", frozen]):
                    with self.assertRaisesRegex(ValueError, "Existing run directory"):
                        runner.preflight(CONFIG["run_id"], note)

    def test_failure_preserves_metadata_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            freeze, _ = fake_source(root)
            directory = root / "engineering-failure"
            with mock.patch.object(runner, "ROOT", root):
                status = runner.execute(directory, freeze, "engineering failure test only", clock=lambda: 0.0,
                                        resident=lambda: CONFIG["memory_bytes"] + 1)
            self.assertEqual(status, "INCOMPLETE")
            failure = (directory / "failure.txt").read_text()
            self.assertIn("Declared resource budget exceeded", failure)
            self.assertIn("Final resource check failed", failure)
            self.assertFalse((directory / "planner.jsonl").exists())
            with self.assertRaises(FileExistsError):
                runner.execute(directory, freeze, "must not overwrite")
            self.assertEqual((directory / "failure.txt").read_text(), failure)

    def test_full_checker_rejects_modified_hash_summary_and_resources(self):
        # Synthetic serialized engineering artifact in /tmp; never a repository run.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            freeze, originals = fake_source(root)
            run = root / "engineering-artifacts" / CONFIG["run_id"]
            run.mkdir(parents=True)
            note = "synthetic checker test artifact"
            configuration = {"source_commit": freeze["source_commit"], "input_sha256": freeze["input_sha256"],
                "config": CONFIG, "source_freeze_sha256": checker.digest(root / FREEZE_PATH),
                "command": ["python3", "scripts/run-rp005a-audit.py", "--run-id", CONFIG["run_id"], "--authorization-note", note],
                "execution_authorization": note, "output_inventory": OUTPUTS}
            manifest = {"configuration": configuration, "seeds": CONFIG["seeds"], "environment": {
                "python": "3.11.0 engineering", "os": "engineering fixture", "processes": 1,
                "network": "none used by the audit", "peak_memory_units": "bytes"}, "outputs": {}}
            values = rows()
            for name, family in zip(("planner.jsonl", "pairs.jsonl", "structural.jsonl"), values):
                (run / name).write_text(stream(family).getvalue())
            payloads = {"frozen-inputs.json": {k: manifest[k] for k in ("configuration", "seeds", "environment")},
                "summary.json": audit.summarize(*values, CONFIG),
                "replay.json": {"status": "PASS", "planner_rows_verified": 24, "paired_comparisons_verified": 12,
                    "structural_sources_verified": 35, "ordered_pairs_per_inclusion_family_verified": 313,
                    "coverage_order_types_and_all_values_verified": True, "disclosed_calibration": {
                    "cases": 4, "planner_rows": 24, "paired_controls": 12, "inclusion_sources": 35}},
                "timing.json": {"status": "COMPLETE", "started_at": "2026-10-11T00:00:00+00:00",
                    "ended_at": "2026-10-11T00:00:01+00:00", "elapsed_monotonic_seconds": 1.0,
                    "peak_resident_memory_bytes": 1024}}
            for name, value in payloads.items():
                (run / name).write_text(replay.canonical(value) + "\n")

            def finalize():
                manifest["outputs"] = {n: checker.digest(run / n) for n in OUTPUTS if n != "manifest.json"}
                (run / "manifest.json").write_text(replay.canonical(manifest) + "\n")
            finalize()
            with mock.patch.object(checker.subprocess, "check_output", side_effect=lambda cmd, **kw: originals[cmd[-1].split(":", 1)[1]]):
                checker.check_run(run, root)
                with (run / "planner.jsonl").open("a") as output:
                    output.write("{}\n")
                with self.assertRaises(AssertionError):
                    checker.check_run(run, root)
                (run / "planner.jsonl").write_text(stream(values[0]).getvalue())
                for name, key, value in (("summary.json", "planner_rows", 23),
                                          ("timing.json", "peak_resident_memory_bytes", 0)):
                    bad = copy.deepcopy(payloads[name])
                    bad[key] = value
                    (run / name).write_text(replay.canonical(bad) + "\n")
                    finalize()
                    with self.assertRaises(AssertionError):
                        checker.check_run(run, root)
                    (run / name).write_text(replay.canonical(payloads[name]) + "\n")
                incomplete = copy.deepcopy(payloads["timing.json"])
                incomplete.update(status="INCOMPLETE", elapsed_monotonic_seconds=61.0,
                                  peak_resident_memory_bytes=CONFIG["memory_bytes"] + 1)
                (run / "timing.json").write_text(replay.canonical(incomplete) + "\n")
                (run / "failure.txt").write_text("Synthetic late resource failure\n")
                manifest["outputs"] = {p.name: checker.digest(p) for p in run.iterdir() if p.name != "manifest.json"}
                (run / "manifest.json").write_text(replay.canonical(manifest) + "\n")
                self.assertEqual(checker.check_run(run, root)["status"], "INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
