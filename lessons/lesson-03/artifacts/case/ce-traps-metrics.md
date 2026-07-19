# CE traps: ORCA vs Legacy (greenplum-625)

Two complementary demos — **different SQL shapes**, each chosen so the target optimizer naturally picks a Nested Loop family plan under missing/stale stats.

| Case | Script | Optimizer | Bad shape | Est vs actual | After TEMP |
| --- | --- | --- | --- | --- | --- |
| **ORCA** | `lesson03-orca-ce-trap.sql` | `optimizer=on` | Nested Loop + Index Scan, Broadcast of “1 row” | ~1 → 80 000, `loops=80000` | Hash Join ~21 ms |
| **Legacy** | `lesson03-legacy-ce-trap.sql` | `optimizer=off`, `enable_nestloop=on` | Nested Loop **Semi** Join + Nested Loop | ~15–29 → 40 060/seg | Hash Join ~22 ms |

## Why two shapes?

On this lab, **the same 3-CTE join** often makes ORCA pick Nested Loop, while Legacy still prefers Hash Join despite `est≪actual`.  
Legacy’s reliable trap is **EXISTS / semi-join** + index on a replicated dim — Nested Loop Semi Join without disabling `enable_hashjoin`.

## Teaching points

1. “ORCA always HashJoin” is false — under-estimate + indexed dim → Index Nested Loop.
2. Legacy defaults on the image: `enable_nestloop=off`; demo turns it **on** (production-like).
3. TEMP + ANALYZE fixes **cardinality of the stage**, then both engines pick Hash Join.
4. Lab scale (2 seg, 80k) — teach plan **shape**, not absolute wall-clock drama.

Raw runs: `orca-ce-trap-run.txt`, `legacy-ce-trap-run.txt`.  
Compatibility alias: `lesson03-nlj-cte-temp-case.sql` → `\i` ORCA script.
