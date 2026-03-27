from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from vnext.community.discord_spike import (
    build_capture_dir,
    discord_get_json,
    get_env_value,
    summarize_messages,
    write_json,
)


def parse_args() -> object:
    parser = ArgumentParser()
    parser.add_argument("--channel-id", required=False)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--name", required=False)
    parser.add_argument("--out", required=False)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    dotenv_path = project_root / ".env"

    token = get_env_value("DISCORD_BOT_TOKEN", dotenv_path=dotenv_path)
    channel_id = args.channel_id or get_env_value("DISCORD_CHANNEL_ID", dotenv_path=dotenv_path)
    if not token:
        raise SystemExit("Missing DISCORD_BOT_TOKEN in environment or .env")
    if not channel_id:
        raise SystemExit("Missing channel id. Pass --channel-id or set DISCORD_CHANNEL_ID.")

    payload = discord_get_json(
        f"/channels/{channel_id}/messages?limit={args.limit}",
        token=token,
    )
    if not isinstance(payload, list):
        raise SystemExit("Unexpected Discord response for channel messages")

    channel_label = args.name or channel_id
    safe_label = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in channel_label)
    output_path = (
        Path(args.out)
        if args.out
        else build_capture_dir(project_root) / f"channel-messages-{safe_label}.json"
    )
    write_json(output_path, payload)

    print(output_path)
    for row in summarize_messages(payload):
        print(
            f"{row['id']}\t{row['author_username']}\t{row['timestamp']}\t"
            f"content_length={row['content_length']}\tattachments={row['attachment_count']}\t"
            f"embeds={row['embed_count']}\treference={row['has_message_reference']}"
        )


if __name__ == "__main__":
    main()
