import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ROUTER = ROOT / "scripts" / "skill_router.py"
CASES = json.loads((ROOT / "evals" / "routing" / "cases.json").read_text())["cases"]


class SkillRouterEvaluationTests(unittest.TestCase):
    def test_routing_recall_and_explicit_negative_cases(self):
        expected = 0
        found = 0
        forbidden = 0
        false_activations = 0
        failures = []

        for case in CASES:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROUTER),
                    "--task",
                    case["prompt"],
                    "--profile",
                    case.get("profile", "balanced"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = json.loads(result.stdout)
            active = {item["name"] for item in plan["required_skills"]}
            required = set(case.get("require", []))
            excluded = set(case.get("exclude", []))
            missing = required - active
            unexpected = excluded & active
            if missing or unexpected:
                failures.append(
                    f"{case['id']}: missing={sorted(missing)} unexpected={sorted(unexpected)} active={sorted(active)}"
                )
            expected += len(required)
            found += len(required & active)
            forbidden += len(excluded)
            false_activations += len(excluded & active)
            self.assertLessEqual(
                len(active), plan["execution_contract"]["max_active_skills"]
            )

        recall = found / expected
        irrelevant_rate = false_activations / forbidden if forbidden else 0.0
        self.assertGreaterEqual(recall, 0.95, "\n".join(failures))
        self.assertEqual(irrelevant_rate, 0.0, "\n".join(failures))
