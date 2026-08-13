import asyncio
import json
import os
import sys
import time

import requests
import websockets

VALID_STATUSES = ("online", "idle", "dnd", "invisible")


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def env_bool(name: str, default: bool = False) -> bool:
    value = env(name, str(default)).lower()
    return value in {"1", "true", "yes", "on"}


TOKEN = env("TOKEN") or env("DISCORD_TOKEN")
STATUS = env("STATUS", "online").lower()
CUSTOM_STATUS = env("CUSTOM_STATUS", "Hey!")
USE_EMOJI = env_bool("USE_EMOJI", False)
EMOJI_NAME = env("EMOJI_NAME", "🔥")
EMOJI_ID = env("EMOJI_ID") or None
EMOJI_ANIMATED = env_bool("EMOJI_ANIMATED", False)
RECONNECT_DELAY = int(env("RECONNECT_DELAY", "5"))

if not TOKEN:
    print("TOKEN (or DISCORD_TOKEN) is required.", file=sys.stderr)
    sys.exit(1)

if STATUS not in VALID_STATUSES:
    print(
        f"Invalid STATUS '{STATUS}'. Use one of: {', '.join(VALID_STATUSES)}",
        file=sys.stderr,
    )
    sys.exit(1)

headers = {"Authorization": TOKEN}

try:
    response = requests.get(
        "https://discord.com/api/v10/users/@me",
        headers=headers,
        timeout=15,
    )
except requests.RequestException as exc:
    print(f"Failed to reach Discord API: {exc}", file=sys.stderr)
    sys.exit(1)

if response.status_code != 200:
    print("Invalid token!", file=sys.stderr)
    sys.exit(1)

user = response.json()
print(f"Logged in as {user['username']} ({user['id']})!")

activities = []
if CUSTOM_STATUS:
    activity = {
        "name": "Custom Status",
        "type": 4,
        "state": CUSTOM_STATUS,
        "id": "custom",
    }
    if USE_EMOJI:
        activity["emoji"] = {
            "name": EMOJI_NAME,
            "id": EMOJI_ID,
            "animated": EMOJI_ANIMATED,
        }
    activities.append(activity)


async def discord_gateway() -> None:
    uri = "wss://gateway.discord.gg/?v=10&encoding=json"

    # Discord READY payloads for large accounts often exceed the library's
    # default 1 MiB frame limit (~7–8 MiB observed), which closes the socket.
    async with websockets.connect(uri, ping_interval=None, max_size=32 * 1024 * 1024) as ws:
        hello = json.loads(await ws.recv())
        heartbeat_interval = hello["d"]["heartbeat_interval"]

        async def heartbeat() -> None:
            while True:
                await asyncio.sleep(heartbeat_interval / 1000)
                await ws.send(json.dumps({"op": 1, "d": None}))

        asyncio.create_task(heartbeat())

        identify = {
            "op": 2,
            "d": {
                "token": TOKEN,
                "properties": {
                    "$os": "linux",
                    "$browser": "chrome",
                    "$device": "pc",
                },
                "presence": {
                    "status": STATUS,
                    "afk": False,
                    "activities": activities,
                },
            },
        }
        await ws.send(json.dumps(identify))
        print(f"Presence set to '{STATUS}'.")

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)
                opcode = data.get("op")

                if opcode == 9:
                    print("Invalid session, reconnecting...")
                    break
                if opcode == 7:
                    print("Gateway requested reconnect...")
                    break
            except Exception as exc:
                print("Connection lost, reconnecting...", exc)
                break


def main() -> None:
    while True:
        try:
            asyncio.run(discord_gateway())
        except KeyboardInterrupt:
            print("Stopped.")
            break
        except Exception as exc:
            print("Gateway error:", exc)
        time.sleep(RECONNECT_DELAY)


if __name__ == "__main__":
    main()
