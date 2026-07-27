"""
Fortnite Sprite Locker — Discord bot + sync API
------------------------------------------------
Slash commands let each Discord user track their own sprite variant collection
and print it as a formatted code block (ready to paste in a trade thread).

This process also runs a small HTTP API (aiohttp) alongside the bot so the web
tracker (index.html) can read/write the SAME collection data. A user links the
two with a short-lived one-time code from `/synccode`.

Commands:
  /collection [user]                Show your collection grid (or another user's).
  /mark <sprite> <variant> <state>  Set one cell: have / mastered / lost / need.
  /markrow <sprite> <state>         Set every released variant of a sprite at once.
  /synccode                         Get a one-time code to link the web tracker.
  /reset                            Clear your whole collection.
  /sprite <sprite>                  Show info/lore about a sprite.

New members get a DM explaining `/synccode` (requires the "Server Members
Intent" toggle in the Discord Developer Portal — see README.md).

Storage: JSON files next to this script (collections.json, sessions.json).
Run:     python bot.py   (needs DISCORD_TOKEN env var — see README.md)
"""

import json
import os
import secrets
import string
import time
from pathlib import Path

import discord
from aiohttp import web
from discord import app_commands

WEBSITE_URL = "https://logdegret.github.io/FortniteSprites/"
API_PORT = int(os.environ.get("API_PORT", "8080"))
SYNC_CODE_TTL = 10 * 60  # seconds

# ---------------------------------------------------------------- data + storage
BASE = Path(__file__).parent
DATA = json.loads((BASE / "sprites.json").read_text())
VARIANTS = DATA["variants"]                      # e.g. ["Normal","Gold",...]
SPRITES = DATA["sprites"]                          # list of dicts
BY_KEY = {s["key"]: s for s in SPRITES}

# Datamined but not live in-game yet. Kept out of every grid, command and count so
# nobody can "collect" something that doesn't exist. Must match UNRELEASED_V in
# gen_html.py — drop an entry from both the day it actually ships.
UNRELEASED = {"Gem", "Quack"}
SHARE_VARIANTS = [v for v in VARIANTS if v not in UNRELEASED]


def live_variants(s: dict) -> list:
    """Released variants this sprite actually has."""
    return [v for v in s["available"] if v not in UNRELEASED]


TOTAL = sum(len(live_variants(s)) for s in SPRITES)

COLL_STORE = BASE / "collections.json"
SESSION_STORE = BASE / "sessions.json"
_collections: dict = json.loads(COLL_STORE.read_text()) if COLL_STORE.exists() else {}
_sessions: dict = json.loads(SESSION_STORE.read_text()) if SESSION_STORE.exists() else {}
_sync_codes: dict = {}   # code -> {discord_id, display_name, expires}

# symbols used in the exported grid
SYM = {"own": "✅", "master": "👑", "lost": "👻", "need": "❌"}
STATE_LABEL = {"own": "Have ✅", "master": "Mastered 👑", "lost": "Lost 👻", "need": "Need ❌"}


def save_collections():
    COLL_STORE.write_text(json.dumps(_collections, indent=1))


def save_sessions():
    SESSION_STORE.write_text(json.dumps(_sessions, indent=1))


def user_coll(uid) -> dict:
    return _collections.setdefault(str(uid), {})


def cell_state(coll: dict, key: str, variant: str) -> str:
    """Return own/master/lost or 'need' for an available variant."""
    return coll.get(f"{key}|{variant}", "need")


def make_sync_code(discord_id, display_name: str) -> str:
    # purge expired codes
    now = time.time()
    for c in [c for c, v in _sync_codes.items() if v["expires"] < now]:
        _sync_codes.pop(c, None)
    alphabet = string.ascii_uppercase.replace("O", "").replace("I", "") + string.digits.replace("0", "").replace("1", "")
    code = "".join(secrets.choice(alphabet) for _ in range(6))
    _sync_codes[code] = {"discord_id": str(discord_id), "display_name": display_name, "expires": now + SYNC_CODE_TTL}
    return code


# ---------------------------------------------------------------- grid rendering
def render_grid(uid, display_name: str) -> str:
    coll = user_coll(uid)
    lines = ["✅Have 👑Mastered 👻Lost ❌Need", ""]
    have = 0
    for s in SPRITES:
        cells = []
        for v in live_variants(s):
            st = cell_state(coll, s["key"], v)
            cells.append(v + SYM.get(st, SYM["need"]))
            if st in ("own", "master"):
                have += 1
        lines.append(f"{s['name']}: " + " ".join(cells))
    lines.append("")
    lines.append(f"{have}/{TOTAL} collected")
    body = "\n".join(lines)
    return f"**{display_name}'s Sprite Locker**\n```\n{body}\n```"


# ---------------------------------------------------------------- discord client
intents = discord.Intents.default()
intents.members = True   # needed for the on-join welcome DM — enable "Server Members Intent" in the dev portal too
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

VARIANT_CHOICES = [app_commands.Choice(name=v, value=v) for v in SHARE_VARIANTS]
SPRITE_CHOICES = [app_commands.Choice(name=s["name"], value=s["key"]) for s in SPRITES][:25]
STATE_CHOICES = [
    app_commands.Choice(name="Have ✅", value="own"),
    app_commands.Choice(name="Mastered 👑", value="master"),
    app_commands.Choice(name="Lost 👻", value="lost"),
    app_commands.Choice(name="Need ❌ (clear)", value="need"),
]


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user} — {len(SPRITES)} sprites, {TOTAL} variants.")


@client.event
async def on_member_join(member: discord.Member):
    try:
        await member.send(
            f"👋 Welcome to **{member.guild.name}**!\n\n"
            f"I track everyone's Fortnite **Sprite** variant collection here, and it syncs with "
            f"the web tracker so you can see it as a nice grid and copy a trade-ready list.\n\n"
            f"**To link your web tracker to your Discord collection:**\n"
            f"1️⃣ Run `/synccode` in the server — I'll give you a one-time code.\n"
            f"2️⃣ Open {WEBSITE_URL} and click **Sync with Discord**.\n"
            f"3️⃣ Paste the code in — you're linked!\n\n"
            f"After that, `/collection`, `/mark`, and `/markrow` here update the exact same "
            f"collection you see on the website (and vice versa).\n\n"
            f"Not synced yet? No problem — `/collection` still works and just tracks locally to Discord."
        )
    except discord.Forbidden:
        pass  # member has DMs disabled — nothing we can do


@tree.command(name="collection", description="Show a sprite collection grid (yours by default).")
@app_commands.describe(user="Whose collection to show (defaults to you).")
async def collection(interaction: discord.Interaction, user: discord.User | None = None):
    target = user or interaction.user
    await interaction.response.send_message(render_grid(target.id, target.display_name))


@tree.command(name="mark", description="Set the state of one sprite variant.")
@app_commands.describe(sprite="Which sprite", variant="Which variant", state="New state")
@app_commands.choices(sprite=SPRITE_CHOICES, variant=VARIANT_CHOICES, state=STATE_CHOICES)
async def mark(
    interaction: discord.Interaction,
    sprite: app_commands.Choice[str],
    variant: app_commands.Choice[str],
    state: app_commands.Choice[str],
):
    s = BY_KEY[sprite.value]
    if variant.value in UNRELEASED:
        await interaction.response.send_message(
            f"🚫 **{variant.value}** isn't in the game yet — nothing to collect.", ephemeral=True
        )
        return
    if variant.value not in s["available"]:
        await interaction.response.send_message(
            f"🚫 **{s['name']} — {variant.value}** isn't an available variant.", ephemeral=True
        )
        return
    coll = user_coll(interaction.user.id)
    k = f"{sprite.value}|{variant.value}"
    if state.value == "need":
        coll.pop(k, None)
    else:
        coll[k] = state.value
    save_collections()
    await interaction.response.send_message(
        f"Set **{s['name']} — {variant.value}** → {STATE_LABEL[state.value]}", ephemeral=True
    )


@tree.command(name="markrow", description="Set every released variant of a sprite at once.")
@app_commands.choices(sprite=SPRITE_CHOICES, state=STATE_CHOICES)
async def markrow(
    interaction: discord.Interaction,
    sprite: app_commands.Choice[str],
    state: app_commands.Choice[str],
):
    s = BY_KEY[sprite.value]
    coll = user_coll(interaction.user.id)
    live = live_variants(s)
    for v in live:
        k = f"{sprite.value}|{v}"
        if state.value == "need":
            coll.pop(k, None)
        else:
            coll[k] = state.value
    save_collections()
    await interaction.response.send_message(
        f"Set all {len(live)} variants of **{s['name']}** → {STATE_LABEL[state.value]}",
        ephemeral=True,
    )


@tree.command(name="sprite", description="Show info about a sprite.")
@app_commands.choices(sprite=SPRITE_CHOICES)
async def sprite_info(interaction: discord.Interaction, sprite: app_commands.Choice[str]):
    s = BY_KEY[sprite.value]
    color = {"Rare": 0x2E7FE0, "Epic": 0x9B4DFF, "Legendary": 0xF0A500, "Mythic": 0xE04B4B}.get(
        s["rarity"], 0x5865F2
    )
    emb = discord.Embed(title=s["name"], description=s.get("desc") or "No description.", color=color)
    emb.add_field(name="Rarity", value=s["rarity"])
    if s.get("element"):
        emb.add_field(name="Element", value=s["element"])
    emb.add_field(name="Variants", value=", ".join(live_variants(s)) or "—", inline=False)
    await interaction.response.send_message(embed=emb)


@tree.command(name="reset", description="Clear your entire collection.")
async def reset(interaction: discord.Interaction):
    _collections[str(interaction.user.id)] = {}
    save_collections()
    await interaction.response.send_message("🧹 Your collection has been cleared.", ephemeral=True)


@tree.command(name="synccode", description="Get a one-time code to link the web tracker to your collection.")
async def synccode(interaction: discord.Interaction):
    code = make_sync_code(interaction.user.id, interaction.user.display_name)
    await interaction.response.send_message(
        f"🔗 Your sync code: **{code}**\n"
        f"Open {WEBSITE_URL}, click **Sync with Discord**, and paste this code in.\n"
        f"It expires in {SYNC_CODE_TTL // 60} minutes and can only be used once.",
        ephemeral=True,
    )


# ---------------------------------------------------------------- HTTP API (for the website)
def cors(resp: web.Response) -> web.Response:
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Sync-Token"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


async def handle_options(request: web.Request) -> web.Response:
    return cors(web.Response())


async def handle_health(request: web.Request) -> web.Response:
    return cors(web.json_response({"ok": True, "sprites": len(SPRITES), "total": TOTAL}))


async def handle_redeem(request: web.Request) -> web.Response:
    try:
        body = await request.json()
        code = str(body.get("code", "")).strip().upper()
    except Exception:
        return cors(web.json_response({"ok": False, "error": "bad request"}, status=400))

    entry = _sync_codes.get(code)
    if not entry or entry["expires"] < time.time():
        _sync_codes.pop(code, None)
        return cors(web.json_response({"ok": False, "error": "Invalid or expired code."}, status=400))

    _sync_codes.pop(code, None)  # single-use
    token = secrets.token_urlsafe(24)
    _sessions[token] = {"discord_id": entry["discord_id"], "display_name": entry["display_name"]}
    save_sessions()
    return cors(web.json_response({"ok": True, "token": token, "display_name": entry["display_name"]}))


def _session_for(request: web.Request):
    token = request.headers.get("X-Sync-Token") or request.query.get("token")
    return token, _sessions.get(token) if token else None


async def handle_get_state(request: web.Request) -> web.Response:
    token, sess = _session_for(request)
    if not sess:
        return cors(web.json_response({"ok": False, "error": "Not synced."}, status=401))
    coll = user_coll(sess["discord_id"])
    return cors(web.json_response({"ok": True, "display_name": sess["display_name"], "state": coll}))


async def handle_set(request: web.Request) -> web.Response:
    token, sess = _session_for(request)
    if not sess:
        return cors(web.json_response({"ok": False, "error": "Not synced."}, status=401))
    try:
        body = await request.json()
    except Exception:
        return cors(web.json_response({"ok": False, "error": "bad request"}, status=400))

    coll = user_coll(sess["discord_id"])
    if "key" in body:  # set a single cell
        k, v = body["key"], body.get("value")
        if v:
            coll[k] = v
        else:
            coll.pop(k, None)
    elif "state" in body and isinstance(body["state"], dict):  # bulk replace
        _collections[str(sess["discord_id"])] = {k: v for k, v in body["state"].items() if v}
    save_collections()
    return cors(web.json_response({"ok": True}))


async def handle_reset(request: web.Request) -> web.Response:
    token, sess = _session_for(request)
    if not sess:
        return cors(web.json_response({"ok": False, "error": "Not synced."}, status=401))
    _collections[str(sess["discord_id"])] = {}
    save_collections()
    return cors(web.json_response({"ok": True}))


def build_web_app() -> web.Application:
    app = web.Application()
    routes = [
        ("GET", "/api/health", handle_health),
        ("POST", "/api/redeem", handle_redeem),
        ("GET", "/api/state", handle_get_state),
        ("POST", "/api/set", handle_set),
        ("POST", "/api/reset", handle_reset),
    ]
    for method, path, handler in routes:
        app.router.add_route(method, path, handler)
        app.router.add_route("OPTIONS", path, handle_options)
    return app


async def main():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise SystemExit("Set the DISCORD_TOKEN environment variable (see README.md).")

    runner = web.AppRunner(build_web_app())
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", API_PORT)
    await site.start()
    print(f"Sync API listening on 127.0.0.1:{API_PORT}")

    async with client:
        await client.start(token)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
