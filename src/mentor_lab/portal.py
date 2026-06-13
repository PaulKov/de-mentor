"""Static student portal for self-service lesson execution."""

from html import escape
from pathlib import Path


class StudentPortal:
    """Writes a dependency-free HTML portal for students."""

    def write(self, path: Path, lab_name: str, version: str = "v1") -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(lab_name, version=version), encoding="utf-8")
        return path

    def render(self, lab_name: str, version: str = "v1") -> str:
        if version == "v2":
            return self._render_v2(lab_name)
        if version != "v1":
            raise ValueError("Portal version must be v1 or v2.")
        commands = [
            f"python3 mentor-lab.py doctor",
            f"python3 mentor-lab.py up {lab_name}",
            f"python3 mentor-lab.py assessment {lab_name} pre",
            f"python3 mentor-lab.py lesson {lab_name}",
            f"python3 mentor-lab.py visualize-plan {lab_name} --query bad_customer_join --sample --format html --output artifacts/{lab_name}-plan.html",
            f"python3 mentor-lab.py diagnostics {lab_name} list",
            f"python3 mentor-lab.py scenario {lab_name} start --difficulty medium --seed 42 --dry-run",
            f"python3 mentor-lab.py challenge {lab_name} start --difficulty hard --minutes 15 --seed 7",
            f"python3 mentor-lab.py submit {lab_name} query-tuning",
            f"python3 mentor-lab.py evidence {lab_name} collect redistribute-join --output submissions/redistribute-join.md",
            f"python3 mentor-lab.py misconception {lab_name} diagnose --text \"partition key это то же самое что distribution key\"",
            f"python3 mentor-lab.py homework {lab_name} check --submission submissions/homework.md",
            f"python3 mentor-lab.py debrief {lab_name} --student <name> --submission submissions/query-tuning.md --pre 40 --post 85",
        ]
        rows = "\n".join(
            f"<li><code>{escape(command)}</code></li>" for command in commands
        )
        return _html_page(
            "Greenplum Student Portal",
            "Self-service route from environment checks to timed challenge.",
            f"<ol>{rows}</ol>",
        )

    def _render_v2(self, lab_name: str) -> str:
        steps = [
            ("Readiness", f"python3 mentor-lab.py doctor"),
            ("Start Greenplum", f"python3 mentor-lab.py up {lab_name}"),
            ("Pre-assessment", f"python3 mentor-lab.py assessment {lab_name} pre"),
            ("Visual plan", f"python3 mentor-lab.py visualize-plan {lab_name} --query bad_customer_join --sample --format html --output artifacts/{lab_name}-plan.html"),
            ("Evidence pack", f"python3 mentor-lab.py evidence {lab_name} collect redistribute-join --output submissions/redistribute-join.md"),
            ("Misconception check", f"python3 mentor-lab.py misconception {lab_name} diagnose --text \"partition key это то же самое что distribution key\""),
            ("Homework check", f"python3 mentor-lab.py homework {lab_name} check --submission submissions/homework.md"),
            ("Debrief", f"python3 mentor-lab.py debrief {lab_name} --student <name> --submission submissions/query-tuning.md --pre 40 --post 85"),
        ]
        step_cards = "\n".join(
            (
                f'<article class="step" data-progress="{index}/{len(steps)}">'
                f"<h2>{escape(title)}</h2><code>{escape(command)}</code>"
                '<label><input type="checkbox"> done</label></article>'
            )
            for index, (title, command) in enumerate(steps, start=1)
        )
        body = f"""
<section class="hero">
  <p>Interactive route with progress, hints, evidence checklist, and export-ready submission structure.</p>
</section>
<section class="grid">{step_cards}</section>
<section>
  <h2>Evidence checklist</h2>
  <ul>
    <li>EXPLAIN / EXPLAIN ANALYZE fragment</li>
    <li><code>gp_segment_id</code> skew check</li>
    <li>Physical cause: distribution key, join key, Motion</li>
    <li>Change and validation before/after</li>
  </ul>
</section>
<section>
  <h2>Misconception hints</h2>
  <code>python3 mentor-lab.py misconception {escape(lab_name)} diagnose --text "partition key это то же самое что distribution key"</code>
</section>
<section>
  <h2>Export submission</h2>
  <textarea aria-label="submission draft"># Submission

## Symptom

## EXPLAIN evidence

## Segment evidence

## Physical cause

## Change

## Validation

## Residual risk
</textarea>
</section>
"""
        return _html_page(
            "Greenplum Student Portal v2",
            "Interactive self-service trainer for evidence-first Greenplum practice.",
            body,
        )


def _html_page(title: str, subtitle: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    body {{ margin: 0; font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f7f7f4; color: #202123; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 36px 20px 52px; }}
    h1 {{ margin: 0 0 8px; font-size: 34px; line-height: 1.15; }}
    p {{ color: #565650; }}
    li {{ margin: 12px 0; }}
    code {{ background: #ffffff; border: 1px solid #d9d9d3; border-radius: 6px; padding: 3px 6px; }}
    ol {{ background: #ffffff; border: 1px solid #d9d9d3; border-radius: 8px; padding: 18px 24px 18px 42px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; }}
    .step, section {{ background: #ffffff; border: 1px solid #d9d9d3; border-radius: 8px; padding: 16px; margin: 14px 0; }}
    textarea {{ width: 100%; min-height: 260px; border: 1px solid #d9d9d3; border-radius: 8px; padding: 12px; font: inherit; }}
  </style>
</head>
<body>
<main>
  <h1>{escape(title)}</h1>
  <p>{escape(subtitle)}</p>
  {body}
</main>
</body>
</html>
"""
