"""Run: python -m app.jobs.sync_finance_only_permissions [--apply] [--tenant CODE ...]

Dry run by default. ``--apply`` performs the writes (BR-CRM-047 / REQ-CRM-028).
"""

from __future__ import annotations

import argparse
import logging

from app.jobs.sync_finance_only_permissions import (
    run_sync_finance_only_permissions,
)

logging.basicConfig(level=logging.INFO)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Synchronise customer.suspend to FINANCE_USER only across all tenants "
            "(BR-CRM-047). Defaults to a dry run."
        )
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="perform the writes (default: dry run, writes nothing)",
    )
    parser.add_argument(
        "--tenant",
        action="append",
        dest="tenants",
        metavar="CODE",
        help="limit the run to this tenant code (repeatable)",
    )
    args = parser.parse_args(argv)

    result = run_sync_finance_only_permissions(
        apply=args.apply,
        tenant_codes=tuple(args.tenants) if args.tenants else None,
    )
    print(
        f"apply={result.apply} "
        f"tenants_scanned={result.tenants_scanned} "
        f"tenants_eligible={result.tenants_eligible} "
        f"tenants_changed={result.tenants_changed} "
        f"tenants_skipped={result.tenants_skipped} "
        f"skip_reasons={result.skip_reasons}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
