"""Lesson 03 slide specs — core lecture is the default export.

- CORE (problem-first, ~38 slides): lesson03_core_slide_specs.CORE_SLIDES
- APPENDIX (deep reference): lesson03_appendix_slide_specs.APPENDIX_SLIDES

`SLIDES` aliases CORE for the main PPTX / existing imports.
"""

from __future__ import annotations

from lesson03_appendix_slide_specs import APPENDIX_SLIDES, GPDB_6X, GPDB_ORCA
from lesson03_core_slide_specs import CORE_SLIDES, GPDB_ARCHIVE

# Backward-compatible names used by build_lesson03_pptx.py and tests.
SLIDES = CORE_SLIDES

__all__ = [
    "SLIDES",
    "CORE_SLIDES",
    "APPENDIX_SLIDES",
    "GPDB_6X",
    "GPDB_ORCA",
    "GPDB_ARCHIVE",
]
