# Greenplum Mentor Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-service first Greenplum lesson package with a cross-platform CLI for mentors and students.

**Architecture:** Documentation, SQL labs, Docker Compose infrastructure, and CLI code are separated by responsibility. The CLI uses a registry of lab definitions and a Docker Compose runner so new systems can be added without changing command semantics.

**Tech Stack:** Python 3.9+, argparse, pytest, Docker Compose, Greenplum Docker image, SQL scripts.

---

### Task 1: CLI Domain And Tests

**Files:**
- Create: `pyproject.toml`
- Create: `tests/test_lab_registry.py`
- Create: `tests/test_docker_compose_runner.py`
- Create: `tests/test_cli.py`
- Create: `src/mentor_lab/domain.py`
- Create: `src/mentor_lab/registry.py`
- Create: `src/mentor_lab/docker_compose.py`
- Create: `src/mentor_lab/cli.py`
- Create: `src/mentor_lab/__main__.py`

- [x] **Step 1: Write failing tests for registry, Docker Compose command generation, and CLI dry-run behavior**

Run: `python3 -m pytest tests -q`

Expected: FAIL with `ModuleNotFoundError: No module named 'mentor_lab'`.

- [x] **Step 2: Implement minimal typed CLI domain**

Create reusable dataclasses for lab metadata, a registry with ready/planned labs, and a Docker Compose runner that supports dry-run output.

- [x] **Step 3: Run tests and keep the public CLI stable**

Run: `python3 -m pytest tests -q`

Expected: PASS.

### Task 2: Lesson Documentation

**Files:**
- Create: `README.md`
- Create: `docs/lessons/01-greenplum/README.md`
- Create: `docs/lessons/01-greenplum/mentor-guide.md`
- Create: `docs/lessons/01-greenplum/student-workbook.md`
- Create: `docs/lessons/01-greenplum/roadmap.md`
- Create: `docs/lessons/01-greenplum/cheat-sheet.md`
- Create: `docs/lessons/01-greenplum/homework.md`

- [x] **Step 1: Add self-service lesson entrypoint**

Write the mentor and student documentation in Russian, with a 60-minute agenda, expected outcomes, and clear commands.

- [x] **Step 2: Add Mermaid roadmap**

Use a roadmap that makes the theory-to-practice flow visible without requiring a separate diagramming tool.

### Task 3: Greenplum Lab Stand

**Files:**
- Create: `labs/greenplum/docker-compose.yml`
- Create: `labs/greenplum/README.md`
- Create: `labs/greenplum/init/00_schema.sql`
- Create: `labs/greenplum/init/01_seed_data.sql`
- Create: `labs/greenplum/init/02_bad_distribution.sql`
- Create: `labs/greenplum/init/03_explain_motion.sql`
- Create: `labs/greenplum/init/04_fix_distribution.sql`

- [x] **Step 1: Add Docker Compose stand**

Define a single-service Greenplum lab with stable credentials, data volume, and initialization script mount.

- [x] **Step 2: Add practice SQL scripts**

Create SQL that demonstrates segment inspection, skew, Motion nodes, and a fixed distribution strategy.

### Task 4: Verification

**Files:**
- Verify all files created above.

- [x] **Step 1: Run automated tests**

Run: `python3 -m pytest tests -q`

Expected: PASS.

- [x] **Step 2: Run CLI smoke checks**

Run:
```bash
python3 mentor-lab.py list
python3 mentor-lab.py info greenplum
python3 mentor-lab.py up greenplum --dry-run
```

Expected: each command exits with code 0 and prints student-friendly instructions.

- [x] **Step 3: Validate Docker Compose syntax when Docker is available**

Run: `docker compose -f labs/greenplum/docker-compose.yml config`

Expected: valid rendered Compose config.
