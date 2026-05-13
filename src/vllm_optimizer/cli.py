from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .artifacts import read_json, read_jsonl, write_json
from .benchmark import BenchmarkError, build_benchmark_plan, load_prompt_set, run_baseline_benchmark
from .discovery import DiscoveryError, load_target, run_discovery
from .experiments import ExperimentValidationError, load_experiment
from .planner import build_trial_plan
from .ranking import rank_results
from .report import ReportError, ReportInputs, build_comparison_report
from .safety import build_dry_run_preview
from .serve_profiles import ServeProfileError, build_serve_plan, load_serve_profile
from .smoke import SmokeServeError, build_smoke_serve_plan, run_smoke_serve
from .ssh import MockExecutor, SshExecutor
from .sweep import (
    SweepError,
    build_sweep_plan,
    build_sweep_preview,
    load_sweep_definition,
    load_sweep_results,
    objective_exit_code,
    rank_sweep_results,
    run_sweep,
)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except (
        DiscoveryError,
        BenchmarkError,
        ExperimentValidationError,
        ServeProfileError,
        SmokeServeError,
        SweepError,
        ReportError,
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

    benchmark_plan_parser = subparsers.add_parser(
        "benchmark-plan", help="Render a dry-run baseline benchmark plan"
    )
    benchmark_plan_parser.add_argument("--profile", required=True, type=Path)
    benchmark_plan_parser.add_argument("--prompts", required=True, type=Path)
    benchmark_plan_parser.add_argument("--out", required=True, type=Path)
    benchmark_plan_parser.set_defaults(func=cmd_benchmark_plan)

    benchmark_run_parser = subparsers.add_parser(
        "benchmark-run", help="Run live baseline benchmark"
    )
    benchmark_run_parser.add_argument("--config", required=True, type=Path)
    benchmark_run_parser.add_argument("--profile", required=True, type=Path)
    benchmark_run_parser.add_argument("--prompts", required=True, type=Path)
    benchmark_run_parser.add_argument("--out", required=True, type=Path)
    benchmark_run_parser.add_argument("--timeout-seconds", type=int, default=1200)
    benchmark_run_parser.set_defaults(func=cmd_benchmark_run)

    sweep_plan_parser = subparsers.add_parser(
        "sweep-plan", help="Generate a deterministic parameter sweep plan"
    )
    sweep_plan_parser.add_argument("--sweep", required=True, type=Path)
    sweep_plan_parser.add_argument("--out", required=True, type=Path)
    sweep_plan_parser.set_defaults(func=cmd_sweep_plan)

    sweep_preview_parser = subparsers.add_parser(
        "sweep-preview", help="Render a dry-run sweep preview"
    )
    sweep_preview_parser.add_argument("--plan", required=True, type=Path)
    sweep_preview_parser.add_argument("--out", required=True, type=Path)
    sweep_preview_parser.set_defaults(func=cmd_sweep_preview)

    sweep_rank_parser = subparsers.add_parser(
        "sweep-rank", help="Rank sweep result artifacts"
    )
    sweep_rank_parser.add_argument("--plan", required=True, type=Path)
    sweep_rank_parser.add_argument("--results", required=True, type=Path)
    sweep_rank_parser.add_argument("--out", required=True, type=Path)
    sweep_rank_parser.set_defaults(func=cmd_sweep_rank)

    sweep_run_parser = subparsers.add_parser(
        "sweep-run", help="Run an approved live sweep sequentially"
    )
    sweep_run_parser.add_argument("--config", required=True, type=Path)
    sweep_run_parser.add_argument("--plan", required=True, type=Path)
    sweep_run_parser.add_argument("--out", required=True, type=Path)
    sweep_run_parser.add_argument("--timeout-seconds", type=int, default=1200)
    sweep_run_parser.add_argument("--continue-on-failure", action="store_true")
    sweep_run_parser.set_defaults(func=cmd_sweep_run)

    report_parser = subparsers.add_parser(
        "report", help="Generate a local comparison report from existing artifacts"
    )
    report_parser.add_argument("--baseline", type=Path)
    report_parser.add_argument("--sweep-ranking", type=Path)
    report_parser.add_argument("--repeated-ranking", type=Path)
    report_parser.add_argument("--out", required=True, type=Path)
    report_parser.add_argument("--markdown-out", type=Path)
    report_parser.set_defaults(func=cmd_report)

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


def cmd_benchmark_plan(args: argparse.Namespace) -> int:
    profile = load_serve_profile(args.profile)
    prompts = load_prompt_set(args.prompts)
    write_json(args.out, build_benchmark_plan(profile, prompts))
    print(str(args.out))
    return 0


def cmd_benchmark_run(args: argparse.Namespace) -> int:
    target = load_target(args.config)
    profile = load_serve_profile(args.profile)
    prompts = load_prompt_set(args.prompts)
    result = run_baseline_benchmark(
        target, profile, prompts, args.out, args.timeout_seconds
    )
    print(str(args.out))
    summary = result["summary"]
    return 0 if summary.get("failure_count", 1) == 0 else 2


def cmd_sweep_plan(args: argparse.Namespace) -> int:
    definition = load_sweep_definition(args.sweep)
    plan = build_sweep_plan(definition)
    write_json(args.out, plan)
    print(str(args.out))
    return 0


def cmd_sweep_preview(args: argparse.Namespace) -> int:
    plan = read_json(args.plan)
    preview = build_sweep_preview(plan)
    write_json(args.out, preview)
    print(str(args.out))
    return 2 if preview["blocked"] else 0


def cmd_sweep_rank(args: argparse.Namespace) -> int:
    plan = read_json(args.plan)
    rows = load_sweep_results(args.results)
    report = rank_sweep_results(plan, rows)
    write_json(args.out, report)
    print(str(args.out))
    return objective_exit_code(report)


def cmd_sweep_run(args: argparse.Namespace) -> int:
    target = load_target(args.config)
    plan = read_json(args.plan)
    prompts = load_prompt_set(Path(plan["prompts_path"]))
    result = run_sweep(
        target,
        plan,
        prompts,
        args.out,
        args.timeout_seconds,
        args.continue_on_failure,
    )
    print(str(args.out))
    return 0 if result["failure_count"] == 0 else 2


def cmd_report(args: argparse.Namespace) -> int:
    report = build_comparison_report(
        ReportInputs(
            baseline=args.baseline,
            sweep_ranking=args.sweep_ranking,
            repeated_ranking=args.repeated_ranking,
        )
    )
    write_json(args.out, report)
    if args.markdown_out is not None:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(report["markdown"], encoding="utf-8")
    print(str(args.out))
    return 0
