"""Command-line interface for Terraform plan summaries."""

import argparse
import json
from pathlib import Path
import sys

from .report import summarize_plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Summarize resource changes in Terraform plan JSON."
    )
    parser.add_argument("plan_json", type=Path, help="file produced by terraform show -json")
    args = parser.parse_args(argv)

    try:
        with args.plan_json.open(encoding="utf-8") as plan_file:
            plan = json.load(plan_file)
        summary = summarize_plan(plan)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"tf-plan-summary: {error}", file=sys.stderr)
        return 2

    print(summary.render())
    return 0