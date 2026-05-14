from pathlib import Path

from vllm_optimizer.artifacts import read_json, write_json
from vllm_optimizer.cli import main


def test_ab_report_cli_writes_json_and_markdown(tmp_path: Path) -> None:
    original = _write_summaries(tmp_path, "original", [1000, 1010, 990], [45, 46, 45])
    recommended = _write_summaries(tmp_path, "recommended", [950, 960, 940], [49, 50, 49])
    out = tmp_path / "ab.json"
    markdown = tmp_path / "ab.md"

    exit_code = main(
        [
            "ab-report",
            "--original-label",
            "original",
            "--recommended-label",
            "recommended",
            "--original-summaries",
            *[str(path) for path in original],
            "--recommended-summaries",
            *[str(path) for path in recommended],
            "--prompt-set-id",
            "qwen-baseline-v1",
            "--out",
            str(out),
            "--markdown-out",
            str(markdown),
        ]
    )

    assert exit_code == 0
    report = read_json(out)
    assert report["decision"]["status"] == "switch-to-recommended"
    assert "switch-to-recommended" in markdown.read_text(encoding="utf-8")


def test_ab_report_cli_rejects_missing_summary(tmp_path: Path) -> None:
    good = _write_summaries(tmp_path, "recommended", [1000], [48])

    exit_code = main(
        [
            "ab-report",
            "--original-label",
            "original",
            "--recommended-label",
            "recommended",
            "--original-summaries",
            str(tmp_path / "missing.json"),
            "--recommended-summaries",
            str(good[0]),
            "--prompt-set-id",
            "qwen-baseline-v1",
            "--out",
            str(tmp_path / "ab.json"),
        ]
    )

    assert exit_code == 2


def _write_summaries(tmp_path: Path, label: str, latencies: list[float], throughputs: list[float]) -> list[Path]:
    paths = []
    for index, (latency, throughput) in enumerate(zip(latencies, throughputs, strict=True), start=1):
        path = tmp_path / f"{label}-{index}.json"
        write_json(
            path,
            {
                "success_count": 3,
                "failure_count": 0,
                "mean_latency_ms": latency,
                "total_tokens": 145,
                "aggregate_tokens_per_second": throughput,
            },
        )
        paths.append(path)
    return paths
