# Discord API Spike

## Purpose

Learn the Discord API enough to decide whether Discord is a viable discovery
surface for community-signal capture.

The spike is not about building ingestion infrastructure yet. It is about
answering one gating question:

Can a bot we control reliably read real message content and recent history in
the target servers and channels we care about?

## Gating Questions

1. Can the bot read message `content` in the relevant servers?
2. Can the bot fetch recent message history from the relevant channels?
3. What channel shapes matter in practice:
   - text channels
   - forum channels
   - active threads
   - archived threads
4. What raw message fields are actually returned for our access path?
5. What permissions and intents are required in practice?

If the answer to `1` or `2` is no, Discord is not a strong primary source for
our pipeline.

## Minimal Bot Configuration

Enable only:

1. `GUILDS`
2. `GUILD_MESSAGES`
3. `MESSAGE_CONTENT`

Do not add more intents until the spike proves they are needed.

For the first test server, the bot needs channel permissions that allow:

1. `VIEW_CHANNEL`
2. `READ_MESSAGE_HISTORY`

It may also need send permissions if we later test interaction or ack flows,
but not for read-only history capture.

## Official API Surfaces To Prove

REST:

1. list guild channels
2. fetch recent messages from a channel
3. inspect thread-related endpoints for active and archived threads

Gateway:

1. verify which events and fields are available with the selected intents
2. confirm whether we need Gateway at all for v1

Initial bias:

1. use REST for daily snapshots
2. defer Gateway until or unless we need near-real-time deltas

## Spike Checklist

1. Create a Discord application and bot in the Developer Portal.
2. Enable `GUILDS`, `GUILD_MESSAGES`, and `MESSAGE_CONTENT`.
3. Invite the bot into one safe test server.
4. Identify 1 to 3 representative channels:
   - one normal text channel
   - one thread-bearing channel if available
   - one high-noise channel if useful for contrast
5. Prove channel discovery:
   - fetch guild channels
   - save raw channel payload
6. Prove message-history access:
   - fetch recent messages from each target channel
   - save raw message payloads
7. Inspect returned fields:
   - `content`
   - `embeds`
   - `attachments`
   - `author`
   - `timestamp`
   - reply / reference fields
8. Prove thread handling if present:
   - active threads
   - archived threads if accessible
9. Save all raw samples locally.
10. Write a short findings note:
   - what worked
   - what fields are available
   - what is missing
   - whether Discord remains viable

## Sample Artifacts To Save

Save under a dedicated spike area first, not the long-term ingestion path.

- `research/analysis/discord-api-spike/<date>/guild-channels.json`
- `research/analysis/discord-api-spike/<date>/channel-messages-<channel>.json`
- `research/analysis/discord-api-spike/<date>/thread-list-<channel>.json`
- `research/analysis/discord-api-spike/<date>/findings.md`

The point is to preserve raw payload examples before we decide on final schema.

## First Test Script Plan

### 1. `scripts/discord_spike_fetch_channels.py`

Inputs:

- `DISCORD_BOT_TOKEN`
- `DISCORD_GUILD_ID`

Behavior:

1. call the guild channel listing endpoint
2. write the raw response to disk
3. print a compact summary:
   - channel id
   - channel name
   - channel type

Output:

- raw `guild-channels.json`

### 2. `scripts/discord_spike_fetch_messages.py`

Inputs:

- `DISCORD_BOT_TOKEN`
- `DISCORD_CHANNEL_ID`
- optional `limit`

Behavior:

1. call the channel message-history endpoint
2. write the raw response to disk
3. print a compact field summary for each message:
   - message id
   - author
   - timestamp
   - content length
   - attachment count
   - embed count

Output:

- raw `channel-messages-<channel>.json`

### 3. `scripts/discord_spike_fetch_threads.py`

Inputs:

- `DISCORD_BOT_TOKEN`
- `DISCORD_CHANNEL_ID`

Behavior:

1. call the relevant thread listing endpoint for the chosen channel shape
2. write the raw response to disk
3. print a compact summary of thread ids and names

Output:

- raw `thread-list-<channel>.json`

### 4. `scripts/discord_spike_summarize_findings.py`

Inputs:

- saved raw spike payloads

Behavior:

1. inspect returned message objects
2. summarize available fields
3. highlight missing fields or permission issues
4. emit a short markdown findings note

Output:

- `findings.md`

## Implementation Notes

Keep the spike deliberately simple:

1. use Python
2. use plain HTTP requests first
3. save raw JSON unchanged
4. do not design the full normalization layer yet
5. do not build daily scheduling yet

The spike should answer viability, not build the system.

## Success Criteria

The spike is successful if we can show:

1. the bot can list channels in the test server
2. the bot can fetch recent messages from target channels
3. returned message payloads contain useful `content`
4. thread access is understood well enough to decide whether it matters for v1
5. we have enough raw samples to design the real schema around actual data

## Likely Infrastructure Implications

If the spike succeeds:

1. raw daily snapshots can be REST-based
2. Gateway can stay optional for v1
3. the ingestion system should preserve raw channel payloads and raw message
   payloads separately
4. normalization and signal analysis should be built only after sample review

If the spike fails:

1. Discord should not be the primary automated discovery source
2. it may still be a manual lead surface
3. we should prioritize other communities with cheaper and more stable access

## Official Docs

Use official Discord docs for the spike:

1. https://docs.discord.com/developers/docs/topics/gateway
2. https://docs.discord.com/developers/resources/message
3. https://docs.discord.com/developers/resources/channel
4. https://docs.discord.com/developers/reference
