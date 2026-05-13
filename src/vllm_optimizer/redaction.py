from __future__ import annotations

import json
from typing import Any

REDACTION = "[REDACTED]"


def redact_text(value: str, secrets: list[str]) -> tuple[str, int]:
    result = value
    count = 0
    for secret in sorted({item for item in secrets if item}, key=len, reverse=True):
        occurrences = result.count(secret)
        if occurrences:
            result = result.replace(secret, REDACTION)
            count += occurrences
    return result, count


def redact_data(data: Any, secrets: list[str]) -> tuple[Any, int]:
    encoded = json.dumps(data, sort_keys=True)
    redacted, count = redact_text(encoded, secrets)
    return json.loads(redacted), count
