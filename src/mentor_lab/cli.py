"""Cross-platform CLI for mentorship lab stands.

The CLI intentionally uses only the Python standard library. A student can run
it from the repository checkout without installing Python packages:

    python3 mentor-lab.py up greenplum
    py mentor-lab.py up greenplum
"""

from __future__ import annotations

from typing import Optional, Sequence

from mentor_lab.cli_parser import build_parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "handler"):
        parser.print_help()
        return 0
    return args.handler(args)


def console() -> None:
    raise SystemExit(main())


_build_parser = build_parser
