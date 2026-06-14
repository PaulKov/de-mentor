"""Built-in runbook catalog data."""

from typing import List

from mentor_lab.runbook_models import Runbook
from mentor_lab.runbook_route_deep import greenplum_deep_runbook
from mentor_lab.runbook_route_homework import greenplum_homework_runbook
from mentor_lab.runbook_route_prep import greenplum_prep_runbook
from mentor_lab.runbook_route_simple import greenplum_simple_runbook


def default_runbooks() -> List[Runbook]:
    return [
        greenplum_prep_runbook(),
        greenplum_simple_runbook(),
        greenplum_deep_runbook(),
        greenplum_homework_runbook(),
    ]
