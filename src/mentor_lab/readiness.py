"""Platform-specific readiness guidance for students before a lab."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ReadinessProfile:
    platform: str
    title: str
    tools: List[str]
    checks: List[str]
    fixes: List[str]

    def render(self, lab_name: str) -> str:
        lines = [
            f"# Readiness Doctor Pro: {lab_name}",
            "",
            f"Platform: {self.title}",
            "",
            "## Required tools",
        ]
        lines.extend(f"- {tool}" for tool in self.tools)
        lines.extend(["", "## Checks"])
        lines.extend(f"- `{check}`" for check in self.checks)
        lines.extend(["", "## Fix actions"])
        lines.extend(f"- {fix}" for fix in self.fixes)
        lines.extend(
            [
                "",
                "## Greenplum smoke",
                "```bash",
                f"python3 mentor-lab.py up {lab_name}",
                f"python3 mentor-lab.py status {lab_name}",
                f"python3 mentor-lab.py check {lab_name} --dry-run",
                "```",
                "",
                "## Minimum resources",
                "- CPU: 4 cores recommended.",
                "- RAM: 8 GB minimum, 12-16 GB comfortable for future Spark/Hadoop labs.",
                "- Disk: 20 GB free for Greenplum lesson, 80+ GB for the full roadmap.",
                "",
            ]
        )
        return "\n".join(lines)


class ReadinessDoctorPro:
    """Renders self-service setup diagnostics for macOS, Windows, and Linux."""

    _PROFILES: Dict[str, ReadinessProfile] = {
        "macos": ReadinessProfile(
            platform="macos",
            title="macOS",
            tools=["Python 3.9+", "Docker Desktop or Colima", "Docker Compose v2"],
            checks=[
                "python3 --version",
                "docker version",
                "docker compose version",
                "sysctl -n hw.ncpu",
            ],
            fixes=[
                "Use Docker Desktop for the simplest path; use Colima only if Docker Desktop is unavailable.",
                "Allocate at least 4 CPU and 8 GB RAM to Docker Desktop.",
                "Run commands from the repository root in Terminal.",
            ],
        ),
        "windows": ReadinessProfile(
            platform="windows",
            title="Windows",
            tools=["Python 3.9+ or py launcher", "Docker Desktop", "WSL 2 backend"],
            checks=[
                "py --version",
                "docker version",
                "docker compose version",
                "wsl --status",
            ],
            fixes=[
                "Enable WSL 2 backend in Docker Desktop settings.",
                "Run `py mentor-lab.py up greenplum` from PowerShell in the repository folder.",
                "Keep the repository on the Windows filesystem or inside one WSL distro, not split across both.",
            ],
        ),
        "linux": ReadinessProfile(
            platform="linux",
            title="Linux",
            tools=["Python 3.9+", "Docker Engine", "docker compose plugin"],
            checks=[
                "python3 --version",
                "docker version",
                "docker compose version",
                "docker info",
            ],
            fixes=[
                "Install Docker Engine and the docker compose plugin from the official packages.",
                "Add the user to the docker group or run through sudo according to local policy.",
                "Verify that the Docker daemon is running before the lesson.",
            ],
        ),
    }

    def render(self, lab_name: str, platform: str) -> str:
        try:
            return self._PROFILES[platform].render(lab_name)
        except KeyError as exc:
            available = ", ".join(sorted(self._PROFILES))
            raise KeyError(f"Unknown platform '{platform}'. Available: {available}.") from exc
