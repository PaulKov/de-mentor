from pathlib import Path

from mentor_lab.seed_profiles import SeedProfileCatalog


def test_seed_profile_catalog_exposes_realistic_learning_modes():
    catalog = SeedProfileCatalog.default(Path("/workspace"))

    profiles = catalog.list("greenplum")
    names = [profile.name for profile in profiles]

    assert names[:3] == ["balanced", "skewed", "enterprise"]
    assert "late-facts" in names
    assert "bad-statistics" in names
    assert "bad-partitioning" in names
    assert "wide-aoco" in names
    assert "small-dimension-broadcast" in names
    assert catalog.get("greenplum", "skewed").file_path == Path(
        "/workspace/labs/greenplum/seed/skewed.sql"
    )


def test_unknown_seed_profile_error_names_available_profiles():
    catalog = SeedProfileCatalog.default(Path("/workspace"))

    try:
        catalog.get("greenplum", "tiny")
    except KeyError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected unknown seed profile to raise KeyError")

    assert "tiny" in message
    assert "balanced" in message
    assert "enterprise" in message
