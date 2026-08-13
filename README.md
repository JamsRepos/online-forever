# Online Forever

Docker image of [SealedSaucer/Online-Forever](https://github.com/SealedSaucer/Online-Forever) for Unraid and other Docker hosts. It keeps a Discord user account showing as online (or idle / DND) by holding a gateway connection.

**Image:** `ghcr.io/jamsrepos/online-forever:latest`

## Disclaimer

Automating a Discord user account is against [Discord's Terms of Service](https://discord.com/terms) and [Community Guidelines](https://discord.com/guidelines). Accounts can be suspended or terminated. This project is not affiliated with Discord Inc. Use it at your own risk.

**Never share your Discord token.** Anyone with it can use your account without the password or 2FA.

## Unraid

Search for **online-forever** in Community Applications. Set your Discord token, start the container, then check the log for `Logged in as ...`. There is no web UI.

## Docker Compose

```bash
cp .env.example .env
# edit .env and set TOKEN
docker compose up -d
```

## Environment variables

| Variable | Default | Description |
| --- | --- | --- |
| `TOKEN` | *(required)* | Discord user token. `DISCORD_TOKEN` is also accepted. |
| `STATUS` | `online` | `online`, `idle`, `dnd`, or `invisible`. |
| `CUSTOM_STATUS` | `Hey!` | Custom status text. Leave empty to disable. |
| `USE_EMOJI` | `false` | Set `true` to attach an emoji to the custom status. |
| `EMOJI_NAME` | `🔥` | Unicode emoji or custom emoji name. |
| `EMOJI_ID` | *(empty)* | Required for custom (non-unicode) emojis. |
| `EMOJI_ANIMATED` | `false` | Set `true` for an animated custom emoji. |
| `RECONNECT_DELAY` | `5` | Seconds to wait before reconnecting. |
| `TZ` | `Europe/London` | Container timezone. |

## License

[GNU General Public License v3.0](LICENSE), same as the upstream project. See [NOTICE](NOTICE).
