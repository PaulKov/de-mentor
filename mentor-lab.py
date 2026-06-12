#!/usr/bin/env python3
"""Repository-local launcher for the mentorship lab CLI."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from mentor_lab.cli import main  # noqa: E402


raise SystemExit(main())

