"""Static mentor cockpit generator."""

from pathlib import Path


class MentorCockpit:
    """Writes a local HTML dashboard with the lesson's self-service commands."""

    def write(self, path: Path, lab_name: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._render(lab_name), encoding="utf-8")
        return path

    def _render(self, lab_name: str) -> str:
        command = f"python3 mentor-lab.py check {lab_name}"
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Mentor Cockpit</title>
  <style>
    body {{ font-family: Inter, Arial, sans-serif; margin: 40px; background: #f7f7f4; color: #202123; }}
    section {{ background: white; border: 1px solid #d8d7d0; border-radius: 8px; padding: 20px; margin: 16px 0; }}
    code {{ background: #efeee8; padding: 2px 6px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>Mentor Cockpit: {lab_name}</h1>
  <section><h2>Readiness Pro</h2><code>python3 mentor-lab.py readiness {lab_name} --platform macos</code></section>
  <section><h2>Teach mode</h2><code>python3 mentor-lab.py teach {lab_name} simple --stage 1</code></section>
  <section><h2>Live Orchestrator</h2><code>python3 mentor-lab.py orchestrate {lab_name} --route simple --stage 1 --mode recovery</code></section>
  <section><h2>Run state</h2><code>{command}</code></section>
  <section><h2>EXPLAIN Analyzer</h2><code>python3 mentor-lab.py analyze-plan {lab_name} --query bad_customer_join</code></section>
  <section><h2>Query Plan Coach</h2><code>python3 mentor-lab.py coach-plan {lab_name} --query bad_customer_join --sample</code></section>
  <section><h2>Observation</h2><code>python3 mentor-lab.py observe {lab_name} start --output artifacts/{lab_name}-observe-checklist.md</code></section>
  <section><h2>Dataset Generator Pro</h2><code>python3 mentor-lab.py dataset {lab_name} generate --scale small --seed 42 --skew high --late-facts --wide-rows --output artifacts/generated-enterprise.sql</code></section>
  <section><h2>Hidden incidents</h2><code>python3 mentor-lab.py incident list {lab_name}</code></section>
  <section><h2>Assessment</h2><code>python3 mentor-lab.py assessment {lab_name} pre</code></section>
  <section><h2>Review loop</h2><code>python3 mentor-lab.py submit {lab_name} advanced-joins</code></section>
  <section><h2>Evidence pack</h2><code>python3 mentor-lab.py evidence {lab_name} collect redistribute-join --output submissions/redistribute-join.md</code></section>
  <section><h2>Misconception check</h2><code>python3 mentor-lab.py misconception {lab_name} diagnose --text "partition key это то же самое что distribution key"</code></section>
  <section><h2>Homework check</h2><code>python3 mentor-lab.py homework {lab_name} check --submission submissions/homework.md</code></section>
  <section><h2>SQL Autograder</h2><code>python3 mentor-lab.py autograde-sql {lab_name} --submission labs/greenplum/examples/student-solution-example.sql --output artifacts/sql-autograde.md</code></section>
  <section><h2>Calibration</h2><code>python3 mentor-lab.py calibration {lab_name} show senior</code></section>
  <section><h2>Debrief</h2><code>python3 mentor-lab.py debrief {lab_name} --student &lt;name&gt; --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/{lab_name}-debrief.md</code></section>
  <section><h2>Learning loop</h2><code>python3 mentor-lab.py learning-loop {lab_name} --pre 40 --post 85 --submission submissions/query-tuning.md --output artifacts/{lab_name}-learning-loop.md</code></section>
  <section><h2>Replay pack</h2><code>python3 mentor-lab.py replay {lab_name} --student &lt;name&gt; --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/{lab_name}-replay.md</code></section>
  <section><h2>Live smoke</h2><code>python3 mentor-lab.py ci-smoke {lab_name} --dry-run</code></section>
</body>
</html>
"""
