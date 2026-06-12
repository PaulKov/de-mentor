"""Static lesson content for the Greenplum academy module."""

from dataclasses import dataclass
from typing import Dict, Iterable, List


_LESSON_ALIASES = {
    "greenplum": "lesson-01",
    "gp": "lesson-01",
    "greenplum-01": "lesson-01",
}

_HINT_TOPIC_ALIASES = {
    "skew-investigation": "skew",
    "distribution-skew": "skew",
    "data-skew": "skew",
    "motion-nodes": "motion",
    "explain-motion": "motion",
    "explain": "plan-reading",
    "plan": "plan-reading",
    "plan-reading-ladder": "plan-reading",
    "joins": "physical-joins",
    "join-physics": "physical-joins",
    "greenplum-joins": "physical-joins",
    "systems": "mpp-systems",
    "architecture-types": "mpp-systems",
    "smp-mpp-epp": "mpp-systems",
    "design-review": "capstone",
    "mart-design": "capstone",
}

_INCIDENT_ALIASES = {
    "skew": "skewed-distribution",
    "skew-investigation": "skewed-distribution",
    "marketplace-slow-report": "skewed-distribution",
    "product": "slow-product-analytics",
    "daily-mart": "broken-daily-mart",
    "bulk-load": "bad-bulk-load",
}


@dataclass(frozen=True)
class LessonStep:
    number: int
    title: str
    kind: str
    duration_minutes: int
    goal: str
    mentor_action: str
    student_action: str
    expected_outcome: str


@dataclass(frozen=True)
class Incident:
    code: str
    title: str
    symptoms: str
    mission: str
    acceptance_criteria: List[str]


@dataclass(frozen=True)
class Lesson:
    code: str
    title: str
    steps: List[LessonStep]

    def step(self, human_index: int) -> LessonStep:
        for step in self.steps:
            if step.number == human_index:
                return step
        raise KeyError(f"Unknown step {human_index} for {self.code}.")


class LessonCatalog:
    """Read-only catalog for lessons, hints, and incident scenarios."""

    def __init__(
        self,
        lessons: Iterable[Lesson],
        hints: Dict[str, Dict[str, List[str]]],
        incidents: Iterable[Incident],
    ) -> None:
        self._lessons = {lesson.code: lesson for lesson in lessons}
        self._hints = hints
        self._incidents = {incident.code: incident for incident in incidents}

    @classmethod
    def default(cls) -> "LessonCatalog":
        return cls(
            lessons=[
                Lesson(
                    code="lesson-01",
                    title="Greenplum MPP Foundations",
                    steps=[
                        LessonStep(
                            1,
                            "Why MPP changes SQL thinking",
                            "theory",
                            5,
                            "Shift from single-node SQL to distributed execution.",
                            "Frame the warehouse problem and ask what changes when data is split.",
                            "Explain where a query executes and what can become expensive.",
                            "Student names coordinator, segments, and network as execution factors.",
                        ),
                        LessonStep(
                            2,
                            "Coordinator, segments, and interconnect",
                            "theory",
                            10,
                            "Build a mental model of Greenplum topology.",
                            "Draw the architecture and connect it to physical data placement.",
                            "Map a table row to a segment and describe query dispatch.",
                            "Student can explain master/coordinator vs segment responsibilities.",
                        ),
                        LessonStep(
                            3,
                            "Distribution key design",
                            "practice",
                            10,
                            "Choose a distribution key using cardinality and join patterns.",
                            "Show bad and good table definitions.",
                            "Compare status, customer_id, and product_id as distribution keys.",
                            "Student rejects low-cardinality keys for large facts.",
                        ),
                        LessonStep(
                            4,
                            "Data skew diagnostics",
                            "practice",
                            10,
                            "Measure uneven work across segments.",
                            "Ask the student to query gp_segment_id.",
                            "Run skew checks and interpret the segment distribution.",
                            "Student identifies a 99/1 skew as a production risk.",
                        ),
                        LessonStep(
                            5,
                            "EXPLAIN and Motion nodes",
                            "practice",
                            10,
                            "Read network movement in Greenplum plans.",
                            "Compare plans for bad and corrected tables.",
                            "Find Redistribute Motion and Gather Motion in EXPLAIN output.",
                            "Student connects Redistribute Motion to non-colocated joins.",
                        ),
                        LessonStep(
                            6,
                            "Incident investigation",
                            "incident",
                            10,
                            "Turn diagnostics into a short RCA.",
                            "Give the marketplace slow-report scenario.",
                            "Find the likely root cause and propose a fix.",
                            "Student writes a concise incident summary with evidence.",
                        ),
                        LessonStep(
                            7,
                            "Architecture design review",
                            "capstone",
                            12,
                            "Design a first analytical mart in Greenplum.",
                            "Review grain, distribution, partitioning, and risks.",
                            "Defend a model for daily marketplace revenue analytics.",
                            "Student can justify grain before physical optimization.",
                        ),
                        LessonStep(
                            8,
                            "Rubric and next practice loop",
                            "assessment",
                            3,
                            "Convert the lesson into measurable next steps.",
                            "Run grading and explain follow-up work.",
                            "Read the report and pick a homework focus.",
                            "Student leaves with a concrete improvement backlog.",
                        ),
                        LessonStep(
                            9,
                            "Advanced: EXPLAIN reading ladder",
                            "advanced",
                            8,
                            "Read a plan as scan -> local work -> join -> Motion -> global work.",
                            "Ask the student to explain a plan without jumping straight to a fix.",
                            "Annotate scans, join algorithms, Motion nodes, and Rows out.",
                            "Student separates local algorithm cost from MPP data movement cost.",
                        ),
                        LessonStep(
                            10,
                            "Advanced: physical joins in MPP",
                            "advanced",
                            10,
                            "Connect co-located, broadcast, and redistribute join patterns to distribution keys.",
                            "Compare customer_id and product_id joins on the same fact table.",
                            "Predict whether each join needs Broadcast Motion or Redistribute Motion.",
                            "Student explains why one distribution key optimizes one dominant join pattern.",
                        ),
                        LessonStep(
                            11,
                            "Advanced: system architecture trade-offs",
                            "advanced",
                            7,
                            "Classify SMP, MPP, EPP, lakehouse, and HTAP trade-offs.",
                            "Give three platform scenarios and ask for the architecture choice.",
                            "Choose a system class and name the bottleneck it optimizes for.",
                            "Student understands that every architecture moves the bottleneck somewhere.",
                        ),
                    ],
                )
            ],
            hints={
                "lesson-01": {
                    "skew": [
                        "Start by grouping the fact table by gp_segment_id.",
                        "A low-cardinality distribution key usually maps many rows to the same segment.",
                        "Recreate the fact with DISTRIBUTED BY on a high-cardinality join key.",
                    ],
                    "motion": [
                        "Run EXPLAIN before EXPLAIN ANALYZE to keep the first read simple.",
                        "Look for Redistribute Motion when join keys are not colocated.",
                        "Compare the plan against fact_sales_good and explain what changed.",
                    ],
                    "capstone": [
                        "Define the fact grain before choosing physical keys.",
                        "Separate partitioning for pruning from distribution for data placement.",
                        "Write down the query patterns that your key choice optimizes.",
                    ],
                    "plan-reading": [
                        "Start with Motion nodes, then walk down to the scans that feed them.",
                        "Compare estimated rows with actual Rows out before blaming the optimizer.",
                        "Name the physical reason in one sentence: join key, distribution key, skew, or final gather.",
                    ],
                    "physical-joins": [
                        "A co-located join means both inputs are already on the same segments by the join key.",
                        "Broadcast Motion is acceptable only when the broadcast side is small after filters.",
                        "Redistribute Motion is the normal price of joining on a key that is not the distribution key.",
                    ],
                    "mpp-systems": [
                        "SMP optimizes for simplicity and vertical scale, not unlimited analytical parallelism.",
                        "MPP optimizes big scans and joins by splitting data and compute, but makes network part of the plan.",
                        "EPP and lakehouse systems improve elasticity and storage openness, but move the hard work to cost, metadata, and shuffle control.",
                    ],
                }
            },
            incidents=[
                Incident(
                    code="skewed-distribution",
                    title="Marketplace revenue report became slow",
                    symptoms=(
                        "Revenue by region query shows Redistribute Motion and one segment "
                        "does almost all work after a new sales fact was deployed."
                    ),
                    mission=(
                        "Find whether the slowdown is caused by distribution skew, a "
                        "non-colocated join, or missing statistics. Produce a short RCA."
                    ),
                    acceptance_criteria=[
                        "Show segment distribution for the bad fact table.",
                        "Identify the low-cardinality distribution key.",
                        "Show the Redistribute Motion in EXPLAIN.",
                        "Propose a corrected distribution strategy and validation query.",
                    ],
                ),
                Incident(
                    code="slow-product-analytics",
                    title="Hidden incident: product analytics query regressed",
                    symptoms=(
                        "Category revenue report now shows Broadcast Motion on a dimension "
                        "and a large final Gather after a product enrichment release."
                    ),
                    mission=(
                        "Decide whether the broadcast is acceptable, identify the real "
                        "bottleneck, and propose a validation query."
                    ),
                    acceptance_criteria=[
                        "Show the product join EXPLAIN plan.",
                        "Separate Broadcast Motion cost from Redistribute Motion cost.",
                        "Explain why customer_id distribution does not optimize product_id joins.",
                        "Propose whether to keep broadcast, change model grain, or add an aggregate mart.",
                    ],
                ),
                Incident(
                    code="broken-daily-mart",
                    title="Hidden incident: daily mart model is physically wrong",
                    symptoms=(
                        "A daily revenue mart is partitioned by load date while business "
                        "queries filter by sale_date and region."
                    ),
                    mission=(
                        "Review grain, partitioning, distribution, and query patterns before "
                        "choosing a physical redesign."
                    ),
                    acceptance_criteria=[
                        "State the mart grain.",
                        "Explain why load_date is not the pruning key for the target workload.",
                        "Choose a distribution key and partition key separately.",
                        "Name validation EXPLAIN checks.",
                    ],
                ),
                Incident(
                    code="bad-bulk-load",
                    title="Hidden incident: bulk load saturates coordinator",
                    symptoms=(
                        "A large CSV load is routed through client/coordinator COPY and "
                        "blocks interactive BI queries."
                    ),
                    mission=(
                        "Choose a parallel load path and explain why master should stay "
                        "control plane, not the data pipe."
                    ),
                    acceptance_criteria=[
                        "Compare COPY through coordinator with gpfdist external table.",
                        "Explain which process reads data in each path.",
                        "Name compression/protocol consideration for gpfdist.",
                        "Propose a repeatable load command.",
                    ],
                ),
            ],
        )

    def get(self, code: str) -> Lesson:
        try:
            return self._lessons[normalize_lesson_code(code)]
        except KeyError as exc:
            available = ", ".join(self._lessons)
            raise KeyError(f"Unknown lesson '{code}'. Available lessons: {available}.") from exc

    def hints(self, lesson_code: str, topic: str) -> List[str]:
        lesson_hints = self._hints.get(normalize_lesson_code(lesson_code), {})
        normalized_topic = normalize_hint_topic(topic)
        try:
            return lesson_hints[normalized_topic]
        except KeyError as exc:
            available = ", ".join(sorted(lesson_hints))
            raise KeyError(f"Unknown hint topic '{topic}'. Available topics: {available}.") from exc

    def incidents(self) -> List[Incident]:
        return list(self._incidents.values())

    def incident(self, code: str) -> Incident:
        normalized_code = normalize_incident_code(code)
        try:
            return self._incidents[normalized_code]
        except KeyError as exc:
            available = ", ".join(self._incidents)
            raise KeyError(f"Unknown incident '{code}'. Available incidents: {available}.") from exc


def normalize_lesson_code(code: str) -> str:
    normalized = code.strip().lower()
    if normalized in _LESSON_ALIASES:
        return _LESSON_ALIASES[normalized]
    if normalized.isdigit():
        return f"lesson-{int(normalized):02d}"
    if normalized.startswith("lesson-") and normalized[-2:].isdigit():
        return normalized
    return normalized


def normalize_hint_topic(topic: str) -> str:
    normalized = topic.strip().lower()
    return _HINT_TOPIC_ALIASES.get(normalized, normalized)


def normalize_incident_code(code: str) -> str:
    normalized = code.strip().lower()
    return _INCIDENT_ALIASES.get(normalized, normalized)
