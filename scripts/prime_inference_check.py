"""Check Prime Inference auth by listing available models."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from urllib.error import HTTPError, URLError
from typing import Any, Dict, List


def fetch_models(base_url: str, api_key: str, team_id: str | None) -> List[str]:
    url = base_url.rstrip("/") + "/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    if team_id:
        headers["X-Prime-Team-ID"] = team_id
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload: Dict[str, Any] = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
        print(f"Request failed with status {exc.code}.", file=sys.stderr)
        if body:
            print(body, file=sys.stderr)
        sys.exit(2)
    except URLError as exc:
        print(f"Network error: {exc.reason}", file=sys.stderr)
        sys.exit(2)

    data = payload.get("data")
    if isinstance(data, list):
        return [item.get("id", "") for item in data if isinstance(item, dict) and item.get("id")]
    if isinstance(payload, list):
        return [item.get("id", "") for item in payload if isinstance(item, dict) and item.get("id")]
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Prime Inference auth by listing models.")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    api_key = os.getenv("PRIME_API_KEY", "").strip()
    if not api_key:
        print("Missing PRIME_API_KEY in environment.")
        sys.exit(1)

    base_url = os.getenv("PRIME_INFERENCE_BASE_URL", "https://api.pinference.ai/api/v1")
    team_id = os.getenv("PRIME_TEAM_ID", "").strip() or None

    models = fetch_models(base_url, api_key, team_id)
    if not models:
        print("No models returned. Check credentials and team scope.")
        sys.exit(2)

    limit = max(1, args.limit)
    preview = models[:limit]
    print(f"models_returned={len(models)}")
    for model_id in preview:
        print(model_id)


if __name__ == "__main__":
    main()
