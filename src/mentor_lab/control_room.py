"""Static mentor control room for lesson facilitation."""

from html import escape
from pathlib import Path


class MentorControlRoom:
    """Writes a local HTML dashboard for mentor orchestration."""

    def write(self, path: Path, lab_name: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(lab_name), encoding="utf-8")
        return path

    def render(self, lab_name: str) -> str:
        sections = [
            (
                "Readiness",
                [
                    f"python3 mentor-lab.py readiness {lab_name} --platform macos",
                    f"python3 mentor-lab.py teach {lab_name} simple --stage 1",
                    f"python3 mentor-lab.py orchestrate {lab_name} --route simple --stage 1 --mode recovery",
                    f"python3 mentor-lab.py status {lab_name}",
                    f"python3 mentor-lab.py check {lab_name}",
                    f"python3 mentor-lab.py grade {lab_name}",
                ],
            ),
            (
                "Diagnostics",
                [
                    f"python3 mentor-lab.py observe {lab_name} start --output artifacts/{lab_name}-observe-checklist.md",
                    f"python3 mentor-lab.py diagnostics {lab_name} show segment-skew",
                    f"python3 mentor-lab.py coach-plan {lab_name} --query bad_customer_join --sample",
                    f"python3 mentor-lab.py visualize-plan {lab_name} --query product_join --sample --format mermaid",
                    f"python3 mentor-lab.py scenario {lab_name} start --difficulty medium --seed 42 --dry-run",
                ],
            ),
            (
                "Timed challenge",
                [
                    f"python3 mentor-lab.py challenge {lab_name} start --difficulty hard --minutes 15 --seed 7",
                    f"python3 mentor-lab.py evidence {lab_name} collect redistribute-join --output submissions/redistribute-join.md",
                    f"python3 mentor-lab.py misconception {lab_name} diagnose --text \"partition key это то же самое что distribution key\"",
                    f"python3 mentor-lab.py homework {lab_name} check --submission submissions/homework.md",
                    f"python3 mentor-lab.py calibration {lab_name} show senior",
                    f"python3 mentor-lab.py adaptive-review {lab_name} --submission submissions/query-tuning.md",
                    f"python3 mentor-lab.py debrief {lab_name} --student <name> --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/{lab_name}-debrief.md",
                    f"python3 mentor-lab.py telemetry {lab_name} --pre 40 --post 85 --review 70",
                    f"python3 mentor-lab.py learning-loop {lab_name} --pre 40 --post 85 --submission submissions/query-tuning.md --output artifacts/{lab_name}-learning-loop.md",
                    f"python3 mentor-lab.py replay {lab_name} --student <name> --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/{lab_name}-replay.md",
                ],
            ),
        ]
        content = []
        for title, commands in sections:
            items = "".join(
                f"<li><code>{escape(command)}</code></li>" for command in commands
            )
            content.append(f"<section><h2>{escape(title)}</h2><ul>{items}</ul></section>")
        return _html_page(
            "Greenplum Mentor Control Room",
            "A single facilitation surface for readiness, diagnostics, and assessment.",
            "\n".join(content),
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
    main {{ max-width: 1080px; margin: 0 auto; padding: 36px 20px 52px; }}
    h1 {{ margin: 0 0 8px; font-size: 34px; line-height: 1.15; }}
    h2 {{ font-size: 18px; margin-top: 0; }}
    p {{ color: #565650; }}
    section {{ background: #ffffff; border: 1px solid #d9d9d3; border-radius: 8px; padding: 18px; margin: 16px 0; }}
    li {{ margin: 10px 0; }}
    code {{ background: #f7f7f4; border: 1px solid #d9d9d3; border-radius: 6px; padding: 3px 6px; }}
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
