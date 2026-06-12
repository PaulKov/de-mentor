"""Core domain objects for self-service mentorship labs."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class LabDefinition:
    """A deployable or planned data platform lab.

    The definition is intentionally infrastructure-agnostic: commands can use
    Docker Compose today and another backend later without changing lesson docs.
    """

    name: str
    title: str
    description: str
    status: str
    compose_file: Path
    service_name: str
    default_user: str
    default_database: str
    port: int
    docs_path: Path

    def compose_path(self, project_root: Path) -> Path:
        """Return the absolute Docker Compose file path for this lab."""

        return project_root / self.compose_file

    def docs_full_path(self, project_root: Path) -> Path:
        """Return the absolute documentation path for this lab."""

        return project_root / self.docs_path


class UnknownLabError(KeyError):
    """Raised when a requested lab is not registered."""

    def __init__(self, requested_name: str, available_names: Iterable[str]) -> None:
        available = ", ".join(available_names)
        self.message = (
            f"Unknown lab '{requested_name}'. Available labs: {available}."
        )
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class LabRegistry:
    """Read-only catalog of ready and planned labs."""

    def __init__(self, labs: Iterable[LabDefinition]) -> None:
        self._labs = {lab.name: lab for lab in labs}

    def list(self) -> List[LabDefinition]:
        """Return labs in registration order."""

        return list(self._labs.values())

    def get(self, name: str) -> LabDefinition:
        """Return a lab by name or raise a user-friendly error."""

        try:
            return self._labs[name]
        except KeyError as exc:
            raise UnknownLabError(name, self._labs.keys()) from exc

