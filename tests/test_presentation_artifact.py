from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]


def test_greenplum_theory_deck_artifact_exists_and_has_22_slides():
    deck = ROOT / "artifacts" / "greenplum-theory.pptx"

    assert deck.exists()
    assert deck.stat().st_size > 50_000

    with ZipFile(deck) as pptx:
        slides = [
            name
            for name in pptx.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        ]

    assert len(slides) == 22


def test_greenplum_theory_deck_source_has_22_slide_modules():
    slides_dir = ROOT / "decks" / "greenplum-theory" / "slides"

    slide_modules = sorted(slides_dir.glob("slide-*.mjs"))

    assert len(slide_modules) == 22
    assert (slides_dir / "shared.mjs").exists()


def test_greenplum_theory_deck_uses_russian_light_theme():
    slides_dir = ROOT / "decks" / "greenplum-theory" / "slides"
    shared = (slides_dir / "shared.mjs").read_text(encoding="utf-8")
    source = "\n".join(
        slide.read_text(encoding="utf-8") for slide in sorted(slides_dir.glob("slide-*.mjs"))
    )

    assert "#F7F7F4" in shared
    assert "#0B1020" not in shared
    assert "Greenplum MPP: мышление дата инженера" in source
    assert "SMP, MPP, EPP" in source
    assert "QD/QE deep dive" in source
    assert "gpfdist external table" in source
    assert "Heap, AO row, AOCO column" in source
    assert "APPENDIX: как читать EXPLAIN" in source
    assert "Physical joins in MPP" in source
    assert "co-located join" in source
    assert "Broadcast vs Redistribute" in source
    assert "MPP-семейства: где цена архитектуры" in source
    assert "Что ученик должен унести с урока" in source
    assert "PostgreSQL mindset" not in source
    assert "Takeaways" not in source
