from datetime import date
from pathlib import Path

from vnext.community.discord_spike import (
    build_capture_dir,
    load_dotenv_file,
    summarize_channels,
    summarize_messages,
)


def test_load_dotenv_file_parses_basic_values(tmp_path: Path) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "\n".join(
            [
                "# comment",
                "DISCORD_BOT_TOKEN=abc123",
                "DISCORD_GUILD_ID='456'",
                'OTHER="quoted value"',
            ]
        )
    )

    parsed = load_dotenv_file(dotenv)

    assert parsed["DISCORD_BOT_TOKEN"] == "abc123"
    assert parsed["DISCORD_GUILD_ID"] == "456"
    assert parsed["OTHER"] == "quoted value"


def test_build_capture_dir_uses_iso_date() -> None:
    path = build_capture_dir(Path("/tmp/project"), date(2026, 3, 26))

    assert path == Path("/tmp/project/research/analysis/discord-api-spike/2026-03-26")


def test_summarize_channels_and_messages_extracts_high_signal_fields() -> None:
    channels = summarize_channels(
        [
            {
                "id": "10",
                "name": "ideas",
                "type": 0,
                "parent_id": "1",
                "thread_metadata": {"archived": False},
            }
        ]
    )
    messages = summarize_messages(
        [
            {
                "id": "20",
                "content": "Watching $LITE",
                "attachments": [{"id": "a"}],
                "embeds": [{"type": "link"}],
                "timestamp": "2026-03-26T00:00:00Z",
                "message_reference": {"message_id": "19"},
                "author": {"username": "tester"},
            }
        ]
    )

    assert channels == [
        {
            "id": "10",
            "name": "ideas",
            "type": 0,
            "parent_id": "1",
            "thread_metadata_present": True,
        }
    ]
    assert messages == [
        {
            "id": "20",
            "author_username": "tester",
            "timestamp": "2026-03-26T00:00:00Z",
            "content_length": 14,
            "attachment_count": 1,
            "embed_count": 1,
            "has_message_reference": True,
        }
    ]
