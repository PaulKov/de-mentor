# Metrics — Secrets #18 NOT IN → Broadcast

Stand: `labs/greenplum-625`, DB `mentor`, `SET optimizer = on`.  
Script: `labs/greenplum-625/examples/lesson03-secret18-not-in-broadcast.sql`.

| Phase | Shape to expect (2-seg lab) | Notes |
| --- | --- | --- |
| A `NOT IN` | `Hash Left Anti Semi (Not-In)` + **Broadcast** of `sec18_t2` | Form matters more than wall time |
| B `NOT EXISTS` | `Hash Anti Join`, co-located on `n` | No full Broadcast of t2 |
| C `LEFT JOIN … IS NULL` | Hash Left + null filter | Watch duplicates if t2 not unique |

Lab capture (2026-07-19, 2 seg, 400k×400k):

```text
A NOT IN:      Broadcast Motion of t2 + Hash Left Anti Semi (Not-In); 285.413 ms
B NOT EXISTS:  Hash Anti Join, no Broadcast; 234.709 ms
C LEFT JOIN:   Hash Left Join local; 267.845 ms
```

Do **not** claim production 100M-row orders of magnitude from this lab — teach **plan shape**.
