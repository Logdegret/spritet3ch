# Fortnite Sprite Locker — Discord Bot

A small bot that lets everyone in your server track their own sprite variant
collection and print it as a formatted grid (same layout as the web tracker),
ready to drop into a trade thread.

## Commands

| Command | What it does |
|---|---|
| `/collection [user]` | Show your collection grid (or someone else's). |
| `/mark <sprite> <variant> <state>` | Set one cell: **Have / Mastered / Lost / Need**. |
| `/markrow <sprite> <state>` | Set every available variant of a sprite at once. |
| `/sprite <sprite>` | Show a sprite's rarity, element, and lore. |
| `/reset` | Clear your whole collection. |

Each person's data is stored per Discord user id in `collections.json`.

## Example output

```
|NORMAL|GOLD|GUMMY|GALAXY|HOLOFOIL|CUBE|GEM|QUACK
✅Have
👑Mastered
👻Lost — needs re-summon
❌Need
🚫Not available
---------------------------
Water         |✅|❌|✅|✅|✅|🚫|❌|🚫|
...
5/98 collected
```

## Setup

1. **Create the bot application**
   - Go to <https://discord.com/developers/applications> → **New Application**.
   - Open **Bot** → **Add Bot** → **Reset Token** and copy the token.
   - No privileged intents are required (this bot only uses slash commands).

2. **Invite it to your server**
   - Open **OAuth2 → URL Generator**.
   - Scopes: check **`bot`** and **`applications.commands`**.
   - Bot permissions: **Send Messages** (and Embed Links for `/sprite`).
   - Open the generated URL and add it to your server.

3. **Install dependencies** (Python 3.10+)
   ```bash
   cd discord-bot
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Run it**
   ```bash
   export DISCORD_TOKEN="your-token-here"
   python bot.py
   ```
   On first launch the slash commands are registered globally (can take a few
   minutes to appear). To make them show up instantly while testing, sync to a
   single server instead — see the note in `bot.py`'s `on_ready`.

## Files

- `bot.py` — the bot.
- `sprites.json` — sprite/variant data (regenerate from the parent folder if the
  sprite list changes).
- `collections.json` — created automatically; each user's tracked variants.

## Keeping data in sync with the web tracker

The web tracker (`../index.html`) stores progress in your browser's
`localStorage`; the bot stores it server-side per Discord user. They're separate
stores by design (browser vs. shared server). Both use the **same sprite list
and grid format**, so a `/collection` printout and a web **Copy for Discord**
printout line up column-for-column.
