from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .artifacts import read_json, read_jsonl, write_json
from .discovery import DiscoveryError, load_target, run_discovery
from .experiments import ExperimentValidationError, load_experiment
from .planner import build_trial_plan
from .ranking import rank_results
from .safety import build_dry_run_preview
from .serve_profiles import ServeProfileError, build_serve_plan, load_serve_profile
from .smoke import SmokeServeError, build_smoke_serve_plan, run_smoke_serve
from .ssh import MockExecutor, SshExecutor


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except (
        DiscoveryError,
        ExperimentValidationError,
        ServeProfileError,
        SmokeServeError,
        ValueError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vllm-optimizer")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
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

    discover_parser = subparsers.add_parser("discover", help="Run read-only discovery")
    discover_parser.add_argument("--config", required=True, type=Path)
    discover_parser.add_argument("--out", required=True, type=Path)
    discover_parser.add_argument("--executor", required=True, choices=["mock", "ssh"])
    discover_parser.add_argument("--mock-results", type=Path)
    discover_parser.set_defaults(func=cmd_discover)

    serve_plan_parser = subparsers.add_parser(
        "serve-plan", help="Render a dry-run vLLM serve command from a profile"
    )
    serve_plan_parser.add_argument("--profile", required=True, type=Path)
    serve_plan_parser.add_argument("--out", required=True, type=Path)
    serve_plan_parser.set_defaults(func=cmd_serve_plan)

    smoke_plan_parser = subparsers.add_parser(
        "smoke-serve-plan", help="Render a dry-run smoke serve lifecycle plan"
    )
    smoke_plan_parser.add_argument("--profile", required=True, type=Path)
    smoke_plan_parser.add_argument("--out", required=True, type=Path)
    smoke_plan_parser.set_defaults(func=cmd_smoke_serve_plan)

    smoke_parser = subparsers.add_parser("smoke-serve", help="Run live smoke serve")
    smoke_parser.add_argument("--config", required=True, type=Path)
    smoke_parser.add_argument("--profile", required=True, type=Path)
    smoke_parser.add_argument("--out", required=True, type=Path)
    smoke_parser.add_argument("--timeout-seconds", type=int, default=900)
    smoke_parser.set_defaults(func=cmd_smoke_serve)

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


def cmd_discover(args: argparse.Namespace) -> int:
    target = load_target(args.config)
    if args.executor == "mock":
        if args.mock_results is None:
            raise DiscoveryError("--mock-results is required when --executor mock is used")
        executor = MockExecutor(read_json(args.mock_results))
    else:
        executor = SshExecutor(target.ssh_destination)
    result = run_discovery(target, executor, args.out)
    print(str(args.out))
    return 3 if result["status"] == "connectivity-failed" else 0


def cmd_serve_plan(args: argparse.Namespace) -> int:
    profile = load_serve_profile(args.profile)
    plan = build_serve_plan(profile)
    write_json(args.out, plan)
    print(str(args.out))
    return 0


def cmd_smoke_serve_plan(args: argparse.Namespace) -> int:
    profile = load_serve_profile(args.profile)
    write_json(args.out, build_smoke_serve_plan(profile))
    print(str(args.out))
    return 0


def cmd_smoke_serve(args: argparse.Namespace) -> int:
    target = load_target(args.config)
    profile = load_serve_profile(args.profile)
    result = run_smoke_serve(target, profile, args.out, args.timeout_seconds)
    print(str(args.out))
    return 0 if result["status"] == "completed" else 2
