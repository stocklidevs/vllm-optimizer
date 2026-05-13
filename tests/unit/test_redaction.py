from vllm_optimizer.redaction import REDACTION, redact_data, redact_text


def test_redact_text_replaces_all_configured_values() -> None:
    redacted, count = redact_text("host 100.84.106.41 path /secret", ["100.84.106.41", "/secret"])

    assert count == 2
    assert redacted == f"host {REDACTION} path {REDACTION}"


def test_redact_data_handles_nested_values() -> None:
    data, count = redact_data({"stdout": "user@100.84.106.41"}, ["100.84.106.41"])

    assert count == 1
    assert data["stdout"] == f"user@{REDACTION}"
