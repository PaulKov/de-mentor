"""Post-lesson replay packs that combine feedback, evidence, and next prep."""

from dataclasses import dataclass
from pathlib import Path

from mentor_lab.debrief import DebriefGenerator
from mentor_lab.learning_loop import LearningLoopBuilder


@dataclass(frozen=True)
class LessonReplayPack:
    lab_name: str
    student_name: str
    submission_path: Path
    debrief_text: str
    learning_loop_text: str

    def render(self) -> str:
        return "\n".join(
            [
                f"# Lesson Replay Pack: {self.student_name} / {self.lab_name.capitalize()}",
                "",
                f"Submission: `{self.submission_path.as_posix()}`",
                "",
                "## Как использовать",
                "- Отправить ученику student-facing части debrief и learning loop.",
                "- Оставить mentor notes себе для начала следующего урока.",
                "- В начале Lesson 02 открыть missing evidence и один короткий EXPLAIN.",
                "",
                "## Debrief",
                self.debrief_text.strip(),
                "",
                "## Learning Loop",
                self.learning_loop_text.strip(),
                "",
                "## Что принести на Lesson 02",
                "- Один исправленный submission с EXPLAIN/gp_segment_id evidence.",
                "- Один вопрос по partition pruning или statistics.",
                "- Короткий before/after: что изменилось в плане после фикса.",
                "",
            ]
        )

    def write(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(), encoding="utf-8")
        return path


class LessonReplayBuilder:
    """Builds a replay pack from the same inputs as debrief and learning loop."""

    @classmethod
    def default(cls) -> "LessonReplayBuilder":
        return cls(DebriefGenerator.default(), LearningLoopBuilder.default())

    def __init__(
        self,
        debriefs: DebriefGenerator,
        learning_loops: LearningLoopBuilder,
    ) -> None:
        self._debriefs = debriefs
        self._learning_loops = learning_loops

    def build(
        self,
        lab_name: str,
        student_name: str,
        submission_path: Path,
        pre_score: int,
        post_score: int,
    ) -> LessonReplayPack:
        debrief = self._debriefs.generate(
            lab_name=lab_name,
            student_name=student_name,
            submission_path=submission_path,
            pre_score=pre_score,
            post_score=post_score,
        )
        learning_loop = self._learning_loops.build(
            lab_name=lab_name,
            pre_score=pre_score,
            post_score=post_score,
            submission_path=submission_path,
        )
        return LessonReplayPack(
            lab_name=lab_name,
            student_name=student_name,
            submission_path=submission_path,
            debrief_text=debrief.render(),
            learning_loop_text=learning_loop.render(),
        )
