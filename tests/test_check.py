import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from check import check_routing, check_skill_files  # noqa: E402


def table(*rows):
    return "## Fix\n\n| Finding | Skill |\n| --- | --- |\n" + "".join(f"| {f} | {s} |\n" for f, s in rows)


def make_skill(root: Path, name: str, body: str = "", invoke_only: bool = True) -> Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    fm = f"---\nname: {name}\n" + ("disable-model-invocation: true\n" if invoke_only else "") + "---\n"
    (d / "SKILL.md").write_text(fm + body, encoding="utf-8")
    return d


class CheckTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        imp = make_skill(self.root, "impeccable")
        (imp / "reference").mkdir()
        (imp / "reference" / "critique.md").write_text("", encoding="utf-8")
        make_skill(self.root, "gestures")

    def tearDown(self):
        self._tmp.cleanup()

    def test_unknown_skill(self):
        errs = check_routing(table(("x", "`nonesuch`"), ("y", "`gestures`")), self.root)
        self.assertEqual(len(errs), 1, errs)
        self.assertIn("nonesuch", errs[0])

    def test_unknown_impeccable_command(self):
        self.assertEqual(check_routing(table(("look", "`impeccable critique`")), self.root), [])
        errs = check_routing(table(("type", "`impeccable typeset`")), self.root)
        self.assertEqual(len(errs), 1, errs)
        self.assertIn("typeset", errs[0])

    def test_row_without_skill(self):
        errs = check_routing(table(("orphan finding", "gestures")), self.root)
        self.assertEqual(len(errs), 1, errs)
        self.assertIn("orphan finding", errs[0])

    def test_hardcoded_home(self):
        skills = self.root / "repo-skills"
        for bad in ("C:\\Users\\bob\\x", "/home/bob/x", "C:/Users/bob/x"):
            d = make_skill(skills, "s", body=f"see {bad}\n")
            self.assertTrue(check_skill_files(skills), bad)
        make_skill(skills, "s", body="python \"$HOME/.claude/skills/x\" and C:\\Users\\<you>\\x\n")
        self.assertEqual(check_skill_files(skills), [])
        (d / "scripts").mkdir()
        (d / "scripts" / "tool.py").write_text("P = '/home/bob/x'\n", encoding="utf-8")
        self.assertTrue(check_skill_files(skills), "non-SKILL.md files are checked too")

    def test_no_skill_md_fails(self):
        empty = self.root / "empty"
        empty.mkdir()
        self.assertTrue(check_skill_files(empty))

    def test_frontmatter(self):
        skills = self.root / "repo-skills"
        d = make_skill(skills, "right")
        (d / "SKILL.md").write_text("---\nname: wrong\ndisable-model-invocation: true\n---\n", encoding="utf-8")
        self.assertTrue(any("wrong" in e for e in check_skill_files(skills)))
        make_skill(skills, "right", invoke_only=False)
        self.assertTrue(any("disable-model-invocation" in e for e in check_skill_files(skills)))
        make_skill(skills, "right")
        self.assertEqual(check_skill_files(skills), [])


if __name__ == "__main__":
    unittest.main()
