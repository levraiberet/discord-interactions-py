"""Exemple 03 - Select menus.

Commande:
- !selects
"""

import os
import discord
from discord.ext import commands

from discord_interactions import (
    create_select_menu,
    create_select_row,
    create_user_select_menu,
    parse_custom_id,
    send_message,
    respond_to_interaction,
)

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command(name="selects")
async def cmd_selects(ctx: commands.Context):
    lang = create_select_menu(
        custom_id="langue",
        placeholder="Choisis une langue",
        options=[
            {"label": "Francais", "value": "fr"},
            {"label": "English", "value": "en"},
            {"label": "Espanol", "value": "es"},
        ],
    )
    users = create_user_select_menu("users_demo", placeholder="Choisis un membre", min_values=1, max_values=2)

    await send_message(
        ctx,
        content="Selects de demonstration",
        components=[create_select_row(lang), create_select_row(users)],
    )


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    custom_id = interaction.data.get("custom_id", "")
    base_id, _ = parse_custom_id(custom_id) if ":" in custom_id else (custom_id, {})

    values = interaction.data.get("values", [])

    if base_id == "langue":
        await respond_to_interaction(interaction, content=f"Langue: {values}", ephemeral=True)
    elif base_id == "users_demo":
        await respond_to_interaction(interaction, content=f"Users: {values}", ephemeral=True)


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    bot.run(TOKEN)
