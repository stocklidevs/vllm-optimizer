from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .artifacts import read_json, read_jsonl, write_json
from .experiments import ExperimentValidationError, load_experiment
from .planner import build_trial_plan
from .ranking import rank_results
from .safety import build_dry_run_preview


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except (ExperimentValidationError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vllm-optimizer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Generate a deterministic trial plan")
    plan_parser.add_argument("--experiment", required=True, type=Path)
    plan_parser.add_argument("--out", required=True, type=Path)
    plan_parser.set_defaults(func=cmd_plan)

    dry_run_parser = subparsers.add_parser("dry-run", help="Preview remote actions")
    dry_run_parser.add_argument("--plan", required=True, type=Path)
    dry_run_parser.add_argument("--out", required=True, type=Path)
    dry_run_parser.add_argument("--allow-blocked-preview", action="store_true")
    dry_run_parser.set_defaults(func=cmd_dry_run)

    rank_parser = subparsers.add_parser("rank", help="Rank benchmark result artifacts")
    rank_parser.add_argument("--plan", required=True, type=Path)
    rank_parser.add_argument("--results", required=True, type=Path)
    rank_parser.add_argument("--out", required=True, type=Path)
    rank_parser.set_defaults(func=cmd_rank)

    return parser


def cmd_plan(args: argparse.Namespace) -> int:
    experiment = load_experiment(args.experiment)
    plan = build_trial_plan(experiment)
    write_json(args.out, plan)
    print(str(args.out))
    return 0


def cmd_dry_run(args: argparse.Namespace) -> int:
    plan = read_json(args.plan)
    preview = build_dry_run_preview(plan)
    write_json(args.out, preview)
    print(str(args.out))
    if preview["blocked_action_count"] and not args.allow_blocked_preview:
        return 2
    return 0


def cmd_rank(args: argparse.Namespace) -> int:
    plan = read_json(args.plan)
    results = read_jsonl(args.results)
    report = rank_results(plan, results)
    write_json(args.out, report)
    print(str(args.out))
    return 0
