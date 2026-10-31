"""The parameter reference is generated from code; this keeps it honest."""
import subprocess, sys


def test_parameters_md_is_current():
    r = subprocess.run([sys.executable, "scripts/gen_parameters_md.py", "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr or r.stdout


def test_no_page_promises_an_auto_reject():
    import glob, re
    for p in glob.glob("docs/*.html") + glob.glob("docs/*.md") + ["README.md"]:
        text = re.sub(r"<script>.*?</script>", "", open(p, encoding="utf-8").read(), flags=re.S)
        assert not re.search(r"(?i)\bauto[- ]?reject", text), p
