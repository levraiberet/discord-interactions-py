"""Exemple 02 - Boutons + routing simple.

Commande:
- !buttons
"""

import os
import discord
from discord.ext import commands

from discord_interactions import (
    create_button,
    create_button_row,
    parse_custom_id,
    send_message,
    respond_to_interaction,
)

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command(name="buttons")
async def cmd_buttons(ctx: commands.Context):
    row = create_button_row(
        create_button("action", label="Info", style="Secondary", data={"kind": "info"}),
        create_button("action", label="Ping", style="Success", data={"kind": "ping"}),
        create_button("action", label="Danger", style="Danger", data={"kind": "danger"}),
    )
    await send_message(ctx, content="Test boutons", components=[row])


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    base_id, data = parse_custom_id(interaction.data.get("custom_id", ""))
    if base_id != "action":
        return

    kind = data.get("kind", "?")
    text = {
        "info": "Voici des infos",
        "ping": "Pong",
        "danger": "Action sensible",
    }.get(kind, "Action inconnue")

    await respond_to_interaction(interaction, content=text, ephemeral=True)


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    bot.run(TOKEN)
