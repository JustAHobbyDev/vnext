from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from vnext.community.discord_spike import (
    build_capture_dir,
    discord_get_json,
    get_env_value,
    summarize_channels,
    write_json,
)


def parse_args() -> object:
    parser = ArgumentParser()
    parser.add_argument("--guild-id", required=False)
    parser.add_argument("--out", required=False)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    dotenv_path = project_root / ".env"

    token = get_env_value("DISCORD_BOT_TOKEN", dotenv_path=dotenv_path)
    guild_id = args.guild_id or get_env_value("DISCORD_GUILD_ID", dotenv_path=dotenv_path)
    if not token:
        raise SystemExit("Missing DISCORD_BOT_TOKEN in environment or .env")
    if not guild_id:
        raise SystemExit("Missing guild id. Pass --guild-id or set DISCORD_GUILD_ID.")

    payload = discord_get_json(f"/guilds/{guild_id}/channels", token=token)
    if not isinstance(payload, list):
        raise SystemExit("Unexpected Discord response for guild channels")

    output_path = (
        Path(args.out)
        if args.out
        else build_capture_dir(project_root) / "guild-channels.json"
    )
    write_json(output_path, payload)

    print(output_path)
    for row in summarize_channels(payload):
        print(
            f"{row['id']}\t{row['name']}\t"
            f"type={row['type']}\tparent={row['parent_id']}"
        )


if __name__ == "__main__":
    main()
