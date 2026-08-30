import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from zipfile import ZipFile

from mentor_lab.cli import main
from mentor_lab.homework_review_lesson04 import Lesson04HomeworkReviewer
from mentor_lab.lesson_catalog import LessonCatalog
from mentor_lab.lesson_routes import resolve_learning_route
from mentor_lab.runbooks import RunbookCatalog
from mentor_lab.spark_lab import SparkProfileCatalog


ROOT = Path(__file__).resolve().parents[1]
LESSON_ROOT = ROOT / "lessons" / "lesson-04"
LAB_ROOT = ROOT / "labs" / "spark"
FULL_DECK = LESSON_ROOT / "artifacts" / "apache-spark-foundations-theory.pptx"
CORE_DECK = LESSON_ROOT / "artifacts" / "apache-spark-foundations-core.pptx"


def invoke(args):
    stdout = StringIO()
    try:
        with redirect_stdout(stdout):
            exit_code = main(args)
    except SystemExit as exc:
        exit_code = int(exc.code)
    return exit_code, stdout.getvalue()


def pptx_slide_count(path: Path) -> int:
    with ZipFile(path) as deck:
        return len(
            [
                name
                for name in deck.namelist()
                if name.startswith("ppt/slides/slide") and name.endswith(".xml")
            ]
        )


def test_lesson_04_catalog_exposes_beginner_pyspark_curriculum():
    catalog = LessonCatalog.default()
    lesson = catalog.get("spark")

    assert lesson.code == "lesson-04"
    assert len(lesson.steps) == 6
    assert sum(step.duration_minutes for step in lesson.steps) == 60
    assert "Big Data" in lesson.steps[0].title
    assert "Driver" in lesson.steps[2].title
    assert "PySpark" in lesson.steps[4].title
    assert "Driver" in catalog.hints("lesson-04", "spark-architecture")[0]
    assert "Exchange" in catalog.hints("pyspark", "spark-shuffle")[0]

    incident = catalog.incident("spark-shuffle-regression")
    assert "Spark UI" in incident.symptoms
    assert len(incident.acceptance_criteria) == 4


def test_lesson_04_route_maps_to_spark_lab_and_next_lesson():
    route = resolve_learning_route("lesson-04")

    assert route.name == "spark-foundations"
    assert route.physical_lab_name == "spark"
    assert route.deck_path.endswith("apache-spark-foundations-theory.pptx")
    assert route.submission_path == "lessons/lesson-04/submissions"
    assert route.next_lesson.code == "05-greenplum-wlm-diagnostics"


def test_lesson_04_documents_lab_and_artifacts_are_self_service_complete():
    required = [
        LESSON_ROOT / "README.md",
        LESSON_ROOT / "docs" / "mentor-guide.md",
        LESSON_ROOT / "docs" / "student-workbook.md",
        LESSON_ROOT / "docs" / "cheat-sheet.md",
        LESSON_ROOT / "docs" / "runbooks" / "simple-path.md",
        LESSON_ROOT / "docs" / "runbooks" / "deep-dive-path.md",
        LESSON_ROOT / "homework" / "assignment.md",
        LESSON_ROOT / "homework" / "rubric.md",
        LAB_ROOT / "docker-compose.yml",
        LAB_ROOT / "README.md",
        LAB_ROOT / "seed" / "generate_lesson04_data.py",
        LAB_ROOT / "examples" / "lesson04_core_pipeline.py",
        LAB_ROOT / "examples" / "lesson04_deep_join.py",
        FULL_DECK,
        CORE_DECK,
    ]

    assert [path.relative_to(ROOT).as_posix() for path in required if not path.exists()] == []
    assert pptx_slide_count(CORE_DECK) == 26
    assert pptx_slide_count(FULL_DECK) == 42

    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            ROOT / "decks" / "apache-spark-foundations" / "content.mjs",
            LESSON_ROOT / "docs" / "mentor-guide.md",
            LESSON_ROOT / "docs" / "student-workbook.md",
            LAB_ROOT / "README.md",
        ]
    )
    for marker in [
        "Big Data",
        "PySpark",
        "Driver",
        "executors",
        "Exchange",
        "Spark UI",
        "BroadcastHashJoin",
        "AQE",
        "evidence",
    ]:
        assert marker in source


def test_lesson_04_decks_have_visible_source_notes():
    with ZipFile(FULL_DECK) as deck:
        note_files = [
            name
            for name in deck.namelist()
            if name.startswith("ppt/notesSlides/notesSlide") and name.endswith(".xml")
        ]
        notes = "\n".join(deck.read(name).decode("utf-8") for name in note_files)

    assert len(note_files) == 42
    assert "[Sources]" in notes
    assert "spark.apache.org" in notes


def test_lesson_04_cli_dry_runs_build_safe_spark_commands():
    cases = [
        (["check", "spark", "--dry-run"], ["spark_master_reachable", "lesson04_smoke.py"]),
        (
            ["seed", "spark", "--profile", "lesson04", "--dry-run"],
            ["generate_lesson04_data.py", "--events 250000", "spark://spark-master:7077"],
        ),
        (
            [
                "spark-submit",
                "spark",
                "labs/spark/examples/lesson04_core_pipeline.py",
                "--dry-run",
                "--",
                "--hold-seconds",
                "30",
            ],
            ["spark-submit", "lesson04_core_pipeline.py", "--hold-seconds 30"],
        ),
    ]

    for args, markers in cases:
        exit_code, output = invoke(args)
        assert exit_code == 0, output
        for marker in markers:
            assert marker in output


def test_lesson_04_profiles_are_laptop_safe_and_actionable():
    assert SparkProfileCatalog.get("tiny").events == 25_000
    assert SparkProfileCatalog.get("lesson04").events == 250_000
    assert SparkProfileCatalog.get("class").events == SparkProfileCatalog.get("lesson04").events
    assert SparkProfileCatalog.get("class").skew_percent == 35
    assert SparkProfileCatalog.get("deep").skew_percent == 55

    try:
        SparkProfileCatalog.get("huge")
    except KeyError as exc:
        message = str(exc)
    else:
        raise AssertionError("Unknown Spark profile must fail")
    assert "lesson04" in message
    assert "tiny" in message


def test_lesson_04_runbooks_and_student_guides_cover_core_deep_and_homework():
    for route in ["prep", "simple", "deep", "homework"]:
        exit_code, output = invoke(["runbook", "spark-foundations", route])
        assert exit_code == 0, output
        assert "Lesson 04" in output
        assert "labs/spark" in output

    deep = RunbookCatalog.default().get("spark-foundations", "deep")
    assert any("27-34" in stage.slides for stage in deep.stages)

    exit_code, bootstrap = invoke(
        ["student", "spark-foundations", "bootstrap", "--platform", "macos"]
    )
    assert exit_code == 0, bootstrap
    assert "seed spark --profile lesson04" in bootstrap
    assert "Spark master UI @ :18080" in bootstrap

    exit_code, readiness = invoke(["readiness", "spark", "--platform", "macos"])
    assert exit_code == 0, readiness
    assert "## Spark smoke" in readiness
    assert "Disk: 10 GB" in readiness
    assert "Greenplum smoke" not in readiness

    exit_code, homework = invoke(["student", "spark-foundations", "homework"])
    assert exit_code == 0, homework
    assert "pipeline.py, evidence.md" in homework
    assert "submission pack" in homework


def test_lesson_04_homework_reviewer_accepts_evidence_and_blocks_driver_collect(tmp_path):
    submission = tmp_path / "submission"
    submission.mkdir()
    (submission / "pipeline.py").write_text(
        """
from pyspark.sql.types import StructType
events = spark.read.schema(StructType([])).parquet(input)
result = events.filter("amount > 0").join(dim, "id").groupBy("day").count()
result.write.mode("overwrite").parquet(output)
result.explain("formatted")
""",
        encoding="utf-8",
    )
    (submission / "evidence.md").write_text(
        """
Exchange marks the shuffle stage. The revenue roundtrip count is reconciled.
Decision: broadcast only after size evidence. Risk: skew; validate the output.
""",
        encoding="utf-8",
    )

    accepted = Lesson04HomeworkReviewer().review(submission)
    assert accepted.accepted, accepted

    pipeline = submission / "pipeline.py"
    pipeline.write_text(pipeline.read_text(encoding="utf-8") + "\nresult.collect()\n", encoding="utf-8")
    rejected = Lesson04HomeworkReviewer().review(submission)
    assert not rejected.accepted
    assert any("collect" in item for item in rejected.missing)


def test_lesson_04_session_control_plane_points_to_spark_materials(tmp_path):
    session_dir = tmp_path / "lesson04-session"
    exit_code, output = invoke(
        [
            "session",
            "spark-foundations",
            "start",
            "--student",
            "Иван",
            "--output",
            str(session_dir),
        ]
    )
    assert exit_code == 0, output

    control_plane = json.loads((session_dir / "session.json").read_text(encoding="utf-8"))[
        "control_plane"
    ]
    assert control_plane["mentor_mode"]["slide_deck"] == (
        "lessons/lesson-04/artifacts/apache-spark-foundations-theory.pptx"
    )
    assert control_plane["student_mode"]["workbook"].endswith("student-workbook.md")
    assert control_plane["next_lesson"]["code"] == "05-greenplum-wlm-diagnostics"
    artifact_paths = {artifact["path"] for artifact in control_plane["artifacts"]}
    assert "labs/spark/examples/lesson04_core_pipeline.py" in artifact_paths
