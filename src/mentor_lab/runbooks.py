"""Mentor runbook catalog facade."""

from typing import Dict, Iterable

from mentor_lab.runbook_defaults import default_runbooks
from mentor_lab.runbook_models import Runbook, RunbookStage

class RunbookCatalog:
    """Read-only catalog for CLI-printable mentor routes."""

    def __init__(self, runbooks: Iterable[Runbook]) -> None:
        self._runbooks: Dict[str, Dict[str, Runbook]] = {}
        for runbook in runbooks:
            self._runbooks.setdefault(runbook.lab_name, {})[runbook.route] = runbook

    @classmethod
    def default(cls) -> "RunbookCatalog":
        """Create the built-in lesson routes."""

        return cls(default_runbooks())

    def get(self, lab_name: str, route: str) -> Runbook:
        """Return one route or raise KeyError with a user-facing message."""

        try:
            return self._runbooks[lab_name][route]
        except KeyError as exc:
            raise KeyError(f"Unknown runbook route: {lab_name} {route}") from exc
