"""Deterministic Greenplum dataset generator for live practice."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


_SCALE_ROWS: Dict[str, int] = {
    "small": 5000,
    "medium": 50000,
    "large": 200000,
}

_SKEW_MODULUS: Dict[str, int] = {
    "none": 2000,
    "medium": 200,
    "high": 20,
}


@dataclass(frozen=True)
class DatasetSpec:
    lab_name: str
    scale: str = "small"
    seed: int = 42
    skew: str = "medium"
    late_facts: bool = False
    wide_rows: bool = False


@dataclass(frozen=True)
class GeneratedDataset:
    spec: DatasetSpec
    sql: str

    def write(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.sql, encoding="utf-8")
        return path


class DatasetGenerator:
    """Builds reproducible SQL seed files for Greenplum exercises."""

    _SUPPORTED_LABS = {"greenplum"}

    def manifest(self, lab_name: str) -> str:
        _validate_lab(lab_name)
        lines = [
            "# Dataset Generator Pro: greenplum",
            "",
            "## Scales",
        ]
        for name, rows in _SCALE_ROWS.items():
            lines.append(f"- {name}: {rows} fact rows")
        lines.extend(
            [
                "",
                "## Knobs",
                "- `--skew none|medium|high`: controls customer concentration.",
                "- `--late-facts`: adds old `sale_date` rows for incremental load drills.",
                "- `--wide-rows`: adds a payload column for AOCO/heap discussion.",
                "",
            ]
        )
        return "\n".join(lines)

    def generate(self, spec: DatasetSpec) -> GeneratedDataset:
        _validate_lab(spec.lab_name)
        rows = _rows_for(spec.scale)
        customer_modulus = _skew_modulus_for(spec.skew)
        setseed = _seed_fraction(spec.seed)
        wide_column = ",\n    wide_payload text" if spec.wide_rows else ""
        wide_value = ",\n    repeat('payload_' || sale_id::text, 8) AS wide_payload" if spec.wide_rows else ""
        late_sql = _late_facts_sql(spec, rows, customer_modulus) if spec.late_facts else ""
        sql = f"""-- Dataset Generator Pro
-- lab: {spec.lab_name}
-- scale: {spec.scale}
-- seed: {spec.seed}
-- skew: {spec.skew}
-- late_facts: {str(spec.late_facts).lower()}
-- wide_rows: {str(spec.wide_rows).lower()}

SELECT setseed({setseed});

DROP TABLE IF EXISTS lesson01.generated_fact_sales;

CREATE TABLE lesson01.generated_fact_sales (
    sale_id bigint,
    customer_id bigint,
    product_id bigint,
    status text,
    sale_date date,
    amount numeric(12, 2),
    loaded_at timestamp{wide_column}
)
WITH (appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1)
DISTRIBUTED BY (customer_id);

INSERT INTO lesson01.generated_fact_sales (
    sale_id,
    customer_id,
    product_id,
    status,
    sale_date,
    amount,
    loaded_at{', wide_payload' if spec.wide_rows else ''}
)
SELECT
    sale_id,
    ((sale_id * 37) % {customer_modulus}) + 1 AS customer_id,
    ((sale_id * 17) % 200) + 1 AS product_id,
    CASE
        WHEN sale_id % 100 < 90 THEN 'paid'
        WHEN sale_id % 100 < 97 THEN 'cancelled'
        WHEN sale_id % 100 < 99 THEN 'returned'
        ELSE 'fraud_review'
    END AS status,
    DATE '2026-01-01' + (sale_id % 90) AS sale_date,
    round((10 + random() * 490)::numeric, 2) AS amount,
    current_timestamp AS loaded_at{wide_value}
FROM generate_series(1, {rows}) AS gs(sale_id);
{late_sql}
ANALYZE lesson01.generated_fact_sales;
"""
        return GeneratedDataset(spec=spec, sql=sql)


def _validate_lab(lab_name: str) -> None:
    if lab_name.lower() not in DatasetGenerator._SUPPORTED_LABS:
        raise KeyError(f"Unknown dataset lab: {lab_name}")


def _rows_for(scale: str) -> int:
    try:
        return _SCALE_ROWS[scale]
    except KeyError as exc:
        available = ", ".join(sorted(_SCALE_ROWS))
        raise KeyError(f"Unknown dataset scale '{scale}'. Available: {available}.") from exc


def _skew_modulus_for(skew: str) -> int:
    try:
        return _SKEW_MODULUS[skew]
    except KeyError as exc:
        available = ", ".join(sorted(_SKEW_MODULUS))
        raise KeyError(f"Unknown skew '{skew}'. Available: {available}.") from exc


def _seed_fraction(seed: int) -> str:
    normalized = abs(seed) % 100
    return f"0.{normalized:02d}"


def _late_facts_sql(spec: DatasetSpec, rows: int, customer_modulus: int) -> str:
    start = rows + 1
    end = rows + max(100, round(rows * 0.02))
    wide_value = ",\n    repeat('late_payload_' || sale_id::text, 8) AS wide_payload" if spec.wide_rows else ""
    return f"""
-- late arriving facts: intentionally old sale_date with fresh loaded_at
INSERT INTO lesson01.generated_fact_sales (
    sale_id,
    customer_id,
    product_id,
    status,
    sale_date,
    amount,
    loaded_at{', wide_payload' if spec.wide_rows else ''}
)
SELECT
    sale_id,
    ((sale_id * 37) % {customer_modulus}) + 1 AS customer_id,
    ((sale_id * 17) % 200) + 1 AS product_id,
    'paid' AS status,
    DATE '2025-12-15' + (sale_id % 7) AS sale_date,
    round((10 + random() * 490)::numeric, 2) AS amount,
    current_timestamp AS loaded_at{wide_value}
FROM generate_series({start}, {end}) AS gs(sale_id);
"""
