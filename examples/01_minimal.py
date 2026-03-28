"""Exemple 01 - Bot minimal en francais.

Commande:
- !demo
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


@bot.command(name="demo")
async def cmd_demo(ctx: commands.Context):
    btn = create_button(
        custom_id="demo_click",
        label="Dire bonjour",
        style="Primary",
        data={"user_id": ctx.author.id},
    )
    await send_message(ctx, content="Clique sur le bouton", components=[create_button_row(btn)])


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    base_id, data = parse_custom_id(interaction.data.get("custom_id", ""))
    if base_id != "demo_click":
        return

    await respond_to_interaction(
        interaction,
        content=f"Salut <@{data.get('user_id')}>",
        ephemeral=True,
    )


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    bot.run(TOKEN)
