"""Run: python -m app.jobs.expire_due_trial_subscriptions"""

from __future__ import annotations

import logging

from app.jobs.expire_due_trial_subscriptions import run_expire_due_trial_subscriptions

logging.basicConfig(level=logging.INFO)


def main() -> None:
    result = run_expire_due_trial_subscriptions()
    print(f"processed={result.processed} failed={result.failed}")


if __name__ == "__main__":
    main()
