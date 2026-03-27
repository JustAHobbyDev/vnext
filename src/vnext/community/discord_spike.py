from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json
import os


DISCORD_API_BASE = "https://discord.com/api/v10"


def load_dotenv_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    env: dict[str, str] = {}
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        value = value.strip()
        if value and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        env[key.strip()] = value
    return env


def get_env_value(name: str, *, dotenv_path: Path | None = None) -> str | None:
    if value := os.getenv(name):
        return value
    if dotenv_path is None:
        return None
    return load_dotenv_file(dotenv_path).get(name)


def build_capture_dir(project_root: Path, capture_date: date | None = None) -> Path:
    capture_date = capture_date or datetime.now(UTC).date()
    return (
        project_root
        / "research"
        / "analysis"
        / "discord-api-spike"
        / capture_date.isoformat()
    )


def discord_get_json(path: str, *, token: str, timeout_seconds: int = 30) -> object:
    request = Request(
        f"{DISCORD_API_BASE}{path}",
        headers={
            "Authorization": f"Bot {token}",
            "User-Agent": "MiroFish-vnext-discord-spike/0.1",
        },
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Discord API HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Discord API connection failed: {exc}") from exc


def summarize_channels(channels: list[dict[str, object]]) -> list[dict[str, object]]:
    summary = []
    for channel in channels:
        summary.append(
            {
                "id": channel.get("id"),
                "name": channel.get("name"),
                "type": channel.get("type"),
                "parent_id": channel.get("parent_id"),
                "thread_metadata_present": bool(channel.get("thread_metadata")),
            }
        )
    return summary


def summarize_messages(messages: list[dict[str, object]]) -> list[dict[str, object]]:
    summary = []
    for message in messages:
        content = message.get("content") or ""
        attachments = message.get("attachments") or []
        embeds = message.get("embeds") or []
        author = message.get("author") or {}
        summary.append(
            {
                "id": message.get("id"),
                "author_username": author.get("username"),
                "timestamp": message.get("timestamp"),
                "content_length": len(content),
                "attachment_count": len(attachments),
                "embed_count": len(embeds),
                "has_message_reference": bool(message.get("message_reference")),
            }
        )
    return summary


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True))
