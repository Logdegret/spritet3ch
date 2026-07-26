"""
Fortnite Sprite Locker — Discord bot
------------------------------------
Slash commands let each Discord user track their own sprite variant collection
and print it as a formatted code block (ready to paste in a trade thread).

Commands:
  /collection [user]              Show your collection grid (or another user's).
  /mark <sprite> <variant> <state>  Set one cell: have / mastered / lost / need.
  /markrow <sprite> <state>       Set every available variant of a sprite at once.
  /reset                          Clear your whole collection.
  /sprite <sprite>                Show info/lore about a sprite.

Storage: a simple JSON file (collections.json) keyed by Discord user id.
Run:     python bot.py   (needs DISCORD_TOKEN env var — see README.md)
"""

import json
import os
from pathlib import Path

import discord
from discord import app_commands

# ---------------------------------------------------------------- data + storage
BASE = Path(__file__).parent
DATA = json.loads((BASE / "sprites.json").read_text())
VARIANTS = DATA["variants"]                      # e.g. ["Normal","Gold",...]
SPRITES = DATA["sprites"]                          # list of dicts
BY_KEY = {s["key"]: s for s in SPRITES}
TOTAL = DATA["total"]

STORE = BASE / "collections.json"
_collections = json.loads(STORE.read_text()) if STORE.exists() else {}

# symbols used in the exported grid
SYM = {"own": "✅", "master": "👑", "lost": "👻", "need": "❌", "na": "🚫"}
STATE_LABEL = {"own": "Have ✅", "master": "Mastered 👑", "lost": "Lost 👻", "need": "Need ❌"}


def save():
    STORE.write_text(json.dumps(_collections, indent=1))


def user_coll(uid: str) -> dict:
    return _collections.setdefault(str(uid), {})


def cell_state(coll: dict, key: str, variant: str) -> str:
    """Return own/master/lost or 'need' for an available variant."""
    return coll.get(f"{key}|{variant}", "need")


# ---------------------------------------------------------------- grid rendering
def render_grid(uid: str, display_name: str) -> str:
    coll = user_coll(uid)
    pad = max(len(s["name"]) for s in SPRITES) + 1
    lines = []
    lines.append("|" + "|".join(v.upper() for v in VARIANTS))
    lines.append("✅Have")
    lines.append("👑Mastered")
    lines.append("👻Lost — needs re-summon")
    lines.append("❌Need")
    lines.append("🚫Not available")
    lines.append("-" * 27)
    have = 0
    for s in SPRITES:
        cells = ""
        for v in VARIANTS:
            if v not in s["available"]:
                cells += "|" + SYM["na"]
                continue
            st = cell_state(coll, s["key"], v)
            cells += "|" + SYM.get(st, SYM["need"])
            if st in ("own", "master"):
                have += 1
        lines.append(s["name"].ljust(pad) + cells + "|")
    lines.append("")
    lines.append(f"{have}/{TOTAL} collected")
    body = "\n".join(lines)
    return f"**{display_name}'s Sprite Locker**\n```\n{body}\n```"


# ---------------------------------------------------------------- discord client
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

VARIANT_CHOICES = [app_commands.Choice(name=v, value=v) for v in VARIANTS]
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
    save()
    await interaction.response.send_message(
        f"Set **{s['name']} — {variant.value}** → {STATE_LABEL[state.value]}", ephemeral=True
    )


@tree.command(name="markrow", description="Set every available variant of a sprite at once.")
@app_commands.choices(sprite=SPRITE_CHOICES, state=STATE_CHOICES)
async def markrow(
    interaction: discord.Interaction,
    sprite: app_commands.Choice[str],
    state: app_commands.Choice[str],
):
    s = BY_KEY[sprite.value]
    coll = user_coll(interaction.user.id)
    for v in s["available"]:
        k = f"{sprite.value}|{v}"
        if state.value == "need":
            coll.pop(k, None)
        else:
            coll[k] = state.value
    save()
    await interaction.response.send_message(
        f"Set all {len(s['available'])} variants of **{s['name']}** → {STATE_LABEL[state.value]}",
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
    emb.add_field(name="Variants", value=", ".join(s["available"]) or "—", inline=False)
    await interaction.response.send_message(embed=emb)


@tree.command(name="reset", description="Clear your entire collection.")
async def reset(interaction: discord.Interaction):
    _collections[str(interaction.user.id)] = {}
    save()
    await interaction.response.send_message("🧹 Your collection has been cleared.", ephemeral=True)


if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise SystemExit("Set the DISCORD_TOKEN environment variable (see README.md).")
    client.run(token)
