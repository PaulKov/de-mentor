from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]


def test_greenplum_theory_deck_artifact_exists_and_has_32_slides():
    deck = ROOT / "artifacts" / "greenplum-theory.pptx"

    assert deck.exists()
    assert deck.stat().st_size > 50_000

    with ZipFile(deck) as pptx:
        slides = [
            name
            for name in pptx.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        ]

    assert len(slides) == 32


def test_greenplum_theory_deck_source_has_32_slide_modules():
    slides_dir = ROOT / "decks" / "greenplum-theory" / "slides"

    slide_modules = sorted(slides_dir.glob("slide-*.mjs"))

    assert len(slide_modules) == 32
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
    assert "Greenplum vs sharded PostgreSQL" in source
    assert "QD / QE / gang / slices" in source
    assert "QD/QE dispatch deep dive" in source
    assert "Docker lab cluster passport" in source
    assert "woblerr/greenplum:7.1.0" in source
    assert "1 coordinator + 2 primary segments" in source
    assert "gp_segment_configuration" in source
    assert "gp_toolkit.gp_disk_free" in source
    assert "gang" in source
    assert "slice" in source
    assert "gpfdist external table" in source
    assert "Heap vs AO row vs AOCO" in source
    assert "gp_default_storage_options" in source
    assert "appendoptimized=true" in source
    assert "orientation=column" in source
    assert "PARTITION BY RANGE" in source
    assert "PARTITION BY LIST" in source
    assert "PARTITION BY HASH" in source
    assert "DEFAULT partition" in source
    assert "pg_partition_tree" in source
    assert "gp_toolkit.gp_partitions" in source
    assert "leaf partitions" in source
    assert "Greenplum не sharded PostgreSQL" in source
    assert "APPENDIX: как читать EXPLAIN" in source
    assert "Physical joins in MPP" in source
    assert "co-located join" in source
    assert "Broadcast vs Redistribute" in source
    assert "MPP-семейства: где цена архитектуры" in source
    assert "Что ученик должен унести с урока" in source
    assert "PostgreSQL mindset" not in source
    assert "Takeaways" not in source
