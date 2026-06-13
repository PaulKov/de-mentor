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
  <section><h2>Run state</h2><code>{command}</code></section>
  <section><h2>EXPLAIN Analyzer</h2><code>python3 mentor-lab.py analyze-plan {lab_name} --query bad_customer_join</code></section>
  <section><h2>Hidden incidents</h2><code>python3 mentor-lab.py incident list {lab_name}</code></section>
  <section><h2>Assessment</h2><code>python3 mentor-lab.py assessment {lab_name} pre</code></section>
  <section><h2>Review loop</h2><code>python3 mentor-lab.py submit {lab_name} advanced-joins</code></section>
  <section><h2>Learning loop</h2><code>python3 mentor-lab.py learning-loop {lab_name} --pre 40 --post 85 --submission submissions/query-tuning.md --output artifacts/{lab_name}-learning-loop.md</code></section>
</body>
</html>
"""
