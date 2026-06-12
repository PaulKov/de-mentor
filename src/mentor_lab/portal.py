"""Static student portal for self-service lesson execution."""

from html import escape
from pathlib import Path


class StudentPortal:
    """Writes a dependency-free HTML portal for students."""

    def write(self, path: Path, lab_name: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(lab_name), encoding="utf-8")
        return path

    def render(self, lab_name: str) -> str:
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
        ]
        rows = "\n".join(
            f"<li><code>{escape(command)}</code></li>" for command in commands
        )
        return _html_page(
            "Greenplum Student Portal",
            "Self-service route from environment checks to timed challenge.",
            f"<ol>{rows}</ol>",
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
