# Principal SCD2 locus case (greenplum-625, GPORCA)

Script: `labs/greenplum-625/examples/lesson03-principal-scd2-locus.sql`  
Deep-dive: `lessons/lesson-03/docs/deep-dives/principal-scd2-locus-redistribute.md`

| Phase | Setup | Redistribute? | Notes (lab 2 seg) |
| --- | --- | --- | --- |
| A | `DISTRIBUTED BY (biz_key, version_id)` + CTE `max(version)` join | **Yes ×2** | Hash Key: `biz_key` — composite ≠ single-key locus |
| B | TEMP `tmp_scd2_latest DISTRIBUTED BY (biz_key)` | **Yes on fact** | Aggregate fixed; fact still composite-hashed |
| C | Fact `DISTRIBUTED BY (biz_key)` + same CTE join | **No** | Local HashAggregate + Hash Join |
| D | `int` ⋈ `int8` both `DISTRIBUTED BY (id)` | **Yes** | Hash Key: `(id)::bigint` cast |

Inspiration: Greenplum Secrets TG #19 (SCD2 CTE), #22 (int/int8).

Raw: `principal-scd2-locus-run.txt`.
