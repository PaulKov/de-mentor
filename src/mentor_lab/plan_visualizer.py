"""Mermaid and HTML visualizations for Greenplum EXPLAIN analyses."""

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import List

from mentor_lab.explain_analyzer import ExplainAnalysis


@dataclass(frozen=True)
class PlanVisual:
    """Rendered visual representation of an EXPLAIN analysis."""

    mermaid: str
    title: str
    risks: List[str]


class PlanVisualizer:
    """Builds learner-friendly diagrams from parsed Greenplum plan signals."""

    def to_mermaid(self, analysis: ExplainAnalysis) -> str:
        lines = [
            "flowchart TD",
            '    QD["Coordinator / QD"]',
            '    IC["Interconnect"]',
            '    QE["Segments / QE gangs"]',
            "    QD --> IC",
            "    IC --> QE",
        ]
        previous = "QE"
        for index, motion in enumerate(_detected_motions(analysis), start=1):
            node = f"M{index}"
            lines.append(f'    {previous} --> {node}["{motion}"]')
            previous = node
        if analysis.join_algorithms:
            joins = ", ".join(analysis.join_algorithms)
            lines.append(f'    {previous} --> J["{joins}"]')
            previous = "J"
        if analysis.hash_keys:
            keys = "<br/>".join(escape(key) for key in analysis.hash_keys)
            lines.append(f'    {previous} --> K["Hash keys<br/>{keys}"]')
        lines.append('    QD -. "final rows" .-> R["Client result"]')
        return "\n".join(lines) + "\n"

    def to_visual(self, analysis: ExplainAnalysis) -> PlanVisual:
        return PlanVisual(
            mermaid=self.to_mermaid(analysis),
            title="Greenplum EXPLAIN Visualizer",
            risks=analysis.risks,
        )

    def to_html(self, analysis: ExplainAnalysis) -> str:
        visual = self.to_visual(analysis)
        risk_items = "\n".join(f"<li>{escape(risk)}</li>" for risk in visual.risks)
        plan = escape(analysis.plan)
        mermaid = escape(visual.mermaid)
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(visual.title)}</title>
  <style>
    body {{
      margin: 0;
      font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #202123;
      background: #f7f7f4;
    }}
    main {{ max-width: 1040px; margin: 0 auto; padding: 32px 20px 48px; }}
    h1 {{ font-size: 32px; line-height: 1.15; margin: 0 0 12px; }}
    h2 {{ font-size: 18px; margin-top: 28px; }}
    pre {{
      overflow: auto;
      border: 1px solid #d9d9d3;
      background: #ffffff;
      border-radius: 8px;
      padding: 16px;
      line-height: 1.45;
    }}
    .panel {{
      border: 1px solid #d9d9d3;
      background: #ffffff;
      border-radius: 8px;
      padding: 20px;
      margin-top: 18px;
    }}
  </style>
  <script type="module">
    import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
    mermaid.initialize({{ startOnLoad: true, theme: "neutral" }});
  </script>
</head>
<body>
<main>
  <h1>{escape(visual.title)}</h1>
  <p>Motion nodes, slices, join algorithms, and coordinator paths as a visual learning artifact.</p>
  <section class="panel">
    <div class="mermaid">
{mermaid}
    </div>
  </section>
  <h2>Risks</h2>
  <ul>{risk_items}</ul>
  <h2>Raw plan</h2>
  <pre>{plan}</pre>
</main>
</body>
</html>
"""

    def write_html(self, path: Path, analysis: ExplainAnalysis) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_html(analysis), encoding="utf-8")
        return path


def _detected_motions(analysis: ExplainAnalysis) -> List[str]:
    motions: List[str] = []
    for motion, count in analysis.motion_counts.items():
        for _ in range(count):
            motions.append(motion)
    return motions or ["No Motion"]
