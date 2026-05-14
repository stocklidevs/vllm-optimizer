from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .ab_confirmation import AbConfirmationError, AbConfirmationInputs, build_ab_confirmation_report
from .artifacts import read_json, read_jsonl, write_json
from .benchmark import BenchmarkError, build_benchmark_plan, load_prompt_set, run_baseline_benchmark
from .discovery import DiscoveryError, load_target, run_discovery
from .default_report import DefaultReportError, DefaultReportInputs, build_default_decision_report
from .experiments import ExperimentValidationError, load_experiment
from .flag_catalog import (
    FlagCatalogError,
    capture_flag_catalog,
    generate_catalog_from_files,
)
from .optimizer_pipeline import OptimizerPipelineError, OptimizerPipelineRequest, run_optimizer_pipeline
from .planner import build_trial_plan
from .promotion import (
    DEFAULT_OBJECTIVE,
    DEFAULT_PROFILE_ID,
    PromotionError,
    build_promotion_preview,
    write_confirmed_promoted_profile,
    write_promoted_profile,
)
from .ranking import rank_results
from .report import ReportError, ReportInputs, build_comparison_report
from .safety import build_dry_run_preview
from .serve_profiles import ServeProfileError, build_serve_plan, load_serve_profile
from .smoke import SmokeServeError, build_smoke_serve_plan, run_smoke_serve
from .ssh import MockExecutor, SshExecutor
from .saturation_report import (
    SaturationInput,
    SaturationReportError,
    SaturationReportInputs,
    build_saturation_report,
)
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
from .workload_report import (
    WorkloadInput,
    WorkloadReportError,
    WorkloadReportInputs,
    build_workload_leaderboard_report,
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
        FlagCatalogError,
        OptimizerPipelineError,
        PromotionError,
        DefaultReportError,
        WorkloadReportError,
        SaturationReportError,
        AbConfirmationError,
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
    sweep_plan_parser.add_argument("--allow-risky-session-flags", action="store_true")
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
    sweep_run_parser.add_argument("--allow-risky-session-flags", action="store_true")
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

    workload_report_parser = subparsers.add_parser(
        "workload-report", help="Generate a workload leaderboard from live sweep rankings"
    )
    workload_report_parser.add_argument("--workload", required=True, nargs="+", help="LABEL=ranking.json")
    workload_report_parser.add_argument("--promoted-profile", nargs="*", default=[], help="LABEL=profile.json")
    workload_report_parser.add_argument("--out", required=True, type=Path)
    workload_report_parser.add_argument("--markdown-out", type=Path)
    workload_report_parser.set_defaults(func=cmd_workload_report)

    optimize_parser = subparsers.add_parser(
        "optimize-workload", help="Run a staged optimization pipeline for one sweep"
    )
    optimize_parser.add_argument("--mode", required=True, choices=["plan", "preview", "run", "report"])
    optimize_parser.add_argument("--sweep", required=True, type=Path)
    optimize_parser.add_argument("--out", required=True, type=Path)
    optimize_parser.add_argument("--config", type=Path)
    optimize_parser.add_argument("--timeout-seconds", type=int, default=1200)
    optimize_parser.add_argument("--continue-on-failure", action="store_true")
    optimize_parser.add_argument("--allow-risky-session-flags", action="store_true")
    optimize_parser.set_defaults(func=cmd_optimize_workload)

    saturation_report_parser = subparsers.add_parser(
        "saturation-report", help="Generate a concurrency saturation report from ranked sweeps"
    )
    saturation_report_parser.add_argument("--ranking", required=True, nargs="+", help="CONCURRENCY=ranking.json")
    saturation_report_parser.add_argument("--out", required=True, type=Path)
    saturation_report_parser.add_argument("--markdown-out", type=Path)
    saturation_report_parser.set_defaults(func=cmd_saturation_report)

    flag_catalog_parser = subparsers.add_parser(
        "flag-catalog", help="Generate a vLLM flag catalog from local help text"
    )
    flag_catalog_parser.add_argument("--policy", required=True, type=Path)
    flag_catalog_parser.add_argument("--help-file", required=True, type=Path)
    flag_catalog_parser.add_argument("--version-file", type=Path)
    flag_catalog_parser.add_argument("--out", required=True, type=Path)
    flag_catalog_parser.set_defaults(func=cmd_flag_catalog)

    flag_capture_parser = subparsers.add_parser(
        "flag-catalog-capture", help="Capture vLLM flag catalog over read-only SSH"
    )
    flag_capture_parser.add_argument("--config", required=True, type=Path)
    flag_capture_parser.add_argument("--profile", required=True, type=Path)
    flag_capture_parser.add_argument("--policy", required=True, type=Path)
    flag_capture_parser.add_argument("--out", required=True, type=Path)
    flag_capture_parser.add_argument("--executor", required=True, choices=["mock", "ssh"])
    flag_capture_parser.add_argument("--mock-results", type=Path)
    flag_capture_parser.set_defaults(func=cmd_flag_catalog_capture)

    promote_preview_parser = subparsers.add_parser(
        "promote-preview", help="Preview promotion of a ranked sweep candidate"
    )
    promote_preview_parser.add_argument("--ranking", required=True, type=Path)
    promote_preview_parser.add_argument("--objective", default=DEFAULT_OBJECTIVE)
    promote_preview_parser.add_argument("--out", required=True, type=Path)
    promote_preview_parser.add_argument("--profile-id", default=DEFAULT_PROFILE_ID)
    promote_preview_parser.set_defaults(func=cmd_promote_preview)

    promote_profile_parser = subparsers.add_parser(
        "promote-profile", help="Generate a recommended profile from a ranked candidate"
    )
    promote_profile_parser.add_argument("--ranking", required=True, type=Path)
    promote_profile_parser.add_argument("--objective", default=DEFAULT_OBJECTIVE)
    promote_profile_parser.add_argument("--profile-out", required=True, type=Path)
    promote_profile_parser.add_argument("--summary-out", required=True, type=Path)
    promote_profile_parser.add_argument("--profile-id", default=DEFAULT_PROFILE_ID)
    promote_profile_parser.add_argument("--force", action="store_true")
    promote_profile_parser.set_defaults(func=cmd_promote_profile)

    promote_confirmed_parser = subparsers.add_parser(
        "promote-confirmed-profile",
        help="Generate a promoted profile only when an A/B report approves it",
    )
    promote_confirmed_parser.add_argument("--confirmation-report", required=True, type=Path)
    promote_confirmed_parser.add_argument("--ranking", required=True, type=Path)
    promote_confirmed_parser.add_argument("--objective", default=DEFAULT_OBJECTIVE)
    promote_confirmed_parser.add_argument("--profile-out", required=True, type=Path)
    promote_confirmed_parser.add_argument("--summary-out", required=True, type=Path)
    promote_confirmed_parser.add_argument("--profile-id", default=DEFAULT_PROFILE_ID)
    promote_confirmed_parser.add_argument("--expected-recommended-label")
    promote_confirmed_parser.add_argument("--force", action="store_true")
    promote_confirmed_parser.set_defaults(func=cmd_promote_confirmed_profile)

    recommended_report_parser = subparsers.add_parser(
        "recommended-report", help="Report whether the promoted profile should remain the default"
    )
    recommended_report_parser.add_argument("--baseline", required=True, type=Path)
    recommended_report_parser.add_argument("--recommended", required=True, type=Path)
    recommended_report_parser.add_argument("--profile", required=True, type=Path)
    recommended_report_parser.add_argument("--source-ranking", type=Path)
    recommended_report_parser.add_argument("--out", required=True, type=Path)
    recommended_report_parser.add_argument("--markdown-out", type=Path)
    recommended_report_parser.set_defaults(func=cmd_recommended_report)

    ab_report_parser = subparsers.add_parser(
        "ab-report", help="Aggregate repeated A/B benchmark summaries"
    )
    ab_report_parser.add_argument("--original-label", required=True)
    ab_report_parser.add_argument("--recommended-label", required=True)
    ab_report_parser.add_argument("--original-summaries", required=True, type=Path, nargs="+")
    ab_report_parser.add_argument("--recommended-summaries", required=True, type=Path, nargs="+")
    ab_report_parser.add_argument("--prompt-set-id", required=True)
    ab_report_parser.add_argument("--noise-percent", type=float, default=1.0)
    ab_report_parser.add_argument("--out", required=True, type=Path)
    ab_report_parser.add_argument("--markdown-out", type=Path)
    ab_report_parser.set_defaults(func=cmd_ab_report)

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
    plan = build_sweep_plan(definition, allow_risky_session_flags=args.allow_risky_session_flags)
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
    plan = read_json(args.plan)
    if plan.get("has_risky_session_flags") and not args.allow_risky_session_flags:
        raise SweepError("risky-session sweep requires --allow-risky-session-flags")
    target = load_target(args.config)
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


def cmd_workload_report(args: argparse.Namespace) -> int:
    promoted_profiles = parse_labeled_paths(args.promoted_profile)
    workloads = []
    for label, ranking_path in parse_labeled_paths(args.workload).items():
        workloads.append(
            WorkloadInput(
                label=label,
                ranking_path=ranking_path,
                promoted_profile_path=promoted_profiles.get(label),
            )
        )
    report = build_workload_leaderboard_report(WorkloadReportInputs(workloads=tuple(workloads)))
    write_json(args.out, report)
    if args.markdown_out is not None:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(report["markdown"], encoding="utf-8")
    print(str(args.out))
    return 0


def cmd_optimize_workload(args: argparse.Namespace) -> int:
    summary = run_optimizer_pipeline(
        OptimizerPipelineRequest(
            mode=args.mode,
            sweep_path=args.sweep,
            out_dir=args.out,
            config_path=args.config,
            timeout_seconds=args.timeout_seconds,
            continue_on_failure=args.continue_on_failure,
            allow_risky_session_flags=args.allow_risky_session_flags,
        )
    )
    print(summary["artifacts"]["pipeline_summary"])
    return 0


def cmd_saturation_report(args: argparse.Namespace) -> int:
    rankings = []
    for label, ranking_path in parse_labeled_paths(args.ranking).items():
        try:
            concurrency = int(label)
        except ValueError as exc:
            raise SaturationReportError(f"expected integer concurrency label, got {label!r}") from exc
        rankings.append(SaturationInput(concurrency=concurrency, ranking_path=ranking_path))
    report = build_saturation_report(SaturationReportInputs(rankings=tuple(rankings)))
    write_json(args.out, report)
    if args.markdown_out is not None:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(report["markdown"], encoding="utf-8")
    print(str(args.out))
    return 0


def parse_labeled_paths(values: list[str]) -> dict[str, Path]:
    parsed = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"expected LABEL=PATH, got {value!r}")
        label, path = value.split("=", 1)
        if not label or not path:
            raise ValueError(f"expected LABEL=PATH, got {value!r}")
        parsed[label] = Path(path)
    return parsed


def cmd_flag_catalog(args: argparse.Namespace) -> int:
    generate_catalog_from_files(args.policy, args.help_file, args.out, args.version_file)
    print(str(args.out))
    return 0


def cmd_flag_catalog_capture(args: argparse.Namespace) -> int:
    target = load_target(args.config)
    profile = load_serve_profile(args.profile)
    if args.executor == "mock":
        if args.mock_results is None:
            raise FlagCatalogError("--mock-results is required when --executor mock is used")
        executor = MockExecutor(read_json(args.mock_results))
    else:
        executor = SshExecutor(target.ssh_destination)
    capture_flag_catalog(target, profile, args.policy, executor, args.out)
    print(str(args.out))
    return 0


def cmd_promote_preview(args: argparse.Namespace) -> int:
    preview = build_promotion_preview(args.ranking, args.objective, args.profile_id)
    write_json(args.out, preview)
    print(str(args.out))
    return 0


def cmd_promote_profile(args: argparse.Namespace) -> int:
    result = write_promoted_profile(
        ranking_path=args.ranking,
        profile_out=args.profile_out,
        summary_out=args.summary_out,
        objective=args.objective,
        profile_id=args.profile_id,
        force=args.force,
    )
    print(result["profile_path"])
    return 0


def cmd_promote_confirmed_profile(args: argparse.Namespace) -> int:
    result = write_confirmed_promoted_profile(
        confirmation_report_path=args.confirmation_report,
        ranking_path=args.ranking,
        profile_out=args.profile_out,
        summary_out=args.summary_out,
        objective=args.objective,
        profile_id=args.profile_id,
        expected_recommended_label=args.expected_recommended_label,
        force=args.force,
    )
    print(result["profile_path"])
    return 0


def cmd_recommended_report(args: argparse.Namespace) -> int:
    report = build_default_decision_report(
        DefaultReportInputs(
            baseline=args.baseline,
            recommended=args.recommended,
            profile=args.profile,
            source_ranking=args.source_ranking,
        )
    )
    write_json(args.out, report)
    if args.markdown_out is not None:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(report["markdown"], encoding="utf-8")
    print(str(args.out))
    return 0


def cmd_ab_report(args: argparse.Namespace) -> int:
    report = build_ab_confirmation_report(
        AbConfirmationInputs(
            original_label=args.original_label,
            recommended_label=args.recommended_label,
            original_summaries=tuple(args.original_summaries),
            recommended_summaries=tuple(args.recommended_summaries),
            prompt_set_id=args.prompt_set_id,
            noise_percent=args.noise_percent,
        )
    )
    write_json(args.out, report)
    if args.markdown_out is not None:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(report["markdown"], encoding="utf-8")
    print(str(args.out))
    return 0
