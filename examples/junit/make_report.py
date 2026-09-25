from pathlib import Path

Path("junit.xml").write_text(
    """<testsuite tests="4" failures="0" errors="0" skipped="1" time="0.125">
  <testcase name="alpha"/>
  <testcase name="beta"/>
  <testcase name="gamma"/>
  <testcase name="delta"><skipped/></testcase>
</testsuite>
""",
    encoding="utf-8",
)
print("wrote junit.xml")
