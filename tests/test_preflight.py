import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "design-pipeline" / "scripts"))

import preflight  # noqa: E402
from preflight import Route, parse_routing, preflight as run  # noqa: E402

SAMPLE = """# Routing

## Critique

| Finding | Skill |
| --- | --- |
| look | `impeccable critique` |

## Fix

| Finding | Skill |
|---|---|
| hard cut | `choreograph` `animate` |
"""


def make_skill(root: Path, name: str) -> Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(f"---\nname: {name}\n---\n", encoding="utf-8")
    return d


def all_skills() -> list[str]:
    seen = []
    for r in parse_routing(preflight.ROUTING.read_text(encoding="utf-8")):
        for s in r.skills:
            if s not in seen:
                seen.append(s)
    return seen


def install_all(root: Path) -> None:
    for s in all_skills():
        d = make_skill(root, s)
        if s == "ui-ux-pro-max":
            (d / "scripts").mkdir()
            (d / "scripts" / "search.py").write_text("", encoding="utf-8")


class PreflightTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.root = self.tmp / "skills"
        self.settings = self.tmp / "settings.json"
        self.settings.write_text("{}", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def go(self):
        return run(preflight.ROUTING, self.root, self.settings)

    def test_parse_routing(self):
        routes = parse_routing(SAMPLE)
        self.assertEqual(routes, [
            Route("Critique", "look", ("impeccable",), ("critique",)),
            Route("Fix", "hard cut", ("choreograph", "animate"), ()),
        ])

    def test_all_present(self):
        install_all(self.root)
        lines, code = self.go()
        self.assertEqual(code, 0, lines)
        self.assertTrue(all(line.startswith("ok") for line in lines), lines)

    def test_missing_skill_names_phase(self):
        install_all(self.root)
        (self.root / "gestures" / "SKILL.md").unlink()
        lines, code = self.go()
        self.assertEqual(code, 1)
        hit = [line for line in lines if line.startswith("MISSING gestures")]
        self.assertEqual(len(hit), 1, lines)
        self.assertIn("Fix", hit[0])
        self.assertIn("finger", hit[0])

    def test_override_off_reports_disabled(self):
        install_all(self.root)
        self.settings.write_text(json.dumps({"skillOverrides": {"choreograph": "off"}}), encoding="utf-8")
        lines, code = self.go()
        self.assertEqual(code, 1)
        self.assertTrue(any(line.startswith("DISABLED choreograph") for line in lines), lines)

    def test_missing_settings(self):
        install_all(self.root)
        self.settings.unlink()
        lines, _ = self.go()
        self.assertTrue(any("could not read skillOverrides" in line for line in lines), lines)
        self.assertTrue(any(line.startswith("ok gestures") for line in lines), lines)

    def test_invalid_settings_json(self):
        install_all(self.root)
        self.settings.write_text("{not json", encoding="utf-8")
        lines, _ = self.go()
        self.assertTrue(any("could not read skillOverrides" in line for line in lines), lines)
        self.assertTrue(any(line.startswith("ok gestures") for line in lines), lines)

    def test_no_skills_root(self):
        lines, code = self.go()
        self.assertEqual(code, 1)
        missing = [line for line in lines if line.startswith("MISSING ") and "/scripts/" not in line]
        self.assertEqual(len(missing), len(all_skills()), lines)

    def test_search_script_checked(self):
        install_all(self.root)
        (self.root / "ui-ux-pro-max" / "scripts" / "search.py").unlink()
        lines, code = self.go()
        self.assertEqual(code, 1)
        self.assertTrue(any(line.startswith("MISSING ui-ux-pro-max/scripts/search.py") for line in lines), lines)

    def test_shallowest_copy_wins(self):
        # Upstream impeccable carries test fixtures that are SKILL.md files named impeccable,
        # deeper in the tree than the real skill. The real one is the shallowest.
        # Both arrangements, so the result cannot depend on the walk order.
        for fixture_dir, real_dir in (("a", "z"), ("z", "a")):
            root = self.tmp / f"order-{fixture_dir}"
            make_skill(root / fixture_dir / "tests" / "fixture", "impeccable")
            real = make_skill(root / real_dir, "impeccable")
            self.assertEqual(preflight.installed_skills(root)["impeccable"], real, fixture_dir)

    def test_symlinked_skill_is_found(self):
        # Skills installed as directory symlinks (common on macOS and Linux). Path.rglob stops
        # following them on Python 3.13+.
        real = make_skill(self.tmp / "elsewhere", "gestures")
        self.root.mkdir()
        try:
            (self.root / "gestures").symlink_to(real, target_is_directory=True)
        except OSError:
            self.skipTest("this platform refuses symlinks")
        self.assertIn("gestures", preflight.installed_skills(self.root))

    def test_settings_with_bom(self):
        # PowerShell 5.1 writes UTF-8 with a BOM.
        install_all(self.root)
        self.settings.write_bytes(b"\xef\xbb\xbf" + json.dumps({"skillOverrides": {"gestures": "off"}}).encode())
        lines, code = self.go()
        self.assertEqual(code, 1)
        self.assertTrue(any(line.startswith("DISABLED gestures") for line in lines), lines)

    def test_paths_with_spaces(self):
        self.root = self.tmp / "with space" / "skills"
        install_all(self.root)
        lines, code = self.go()
        self.assertEqual(code, 0, lines)


if __name__ == "__main__":
    unittest.main()
