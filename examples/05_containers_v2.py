"""Exemple 05 - Containers V2.

Commande:
- !card
"""

import os
import discord
from discord.ext import commands

from discord_interactions import (
    ContainerBuilder,
    TextDisplayBuilder,
    SeparatorBuilder,
    ActionRowBuilder,
    create_button,
    send_message,
    MessageFlags,
)

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command(name="card")
async def cmd_card(ctx: commands.Context):
    like_btn = create_button("card_like", label="Like", style="Primary")

    card = (
        ContainerBuilder()
        .setAccentColor(0x5865F2)
        .addTextDisplayComponents(TextDisplayBuilder().setContent("## Carte exemple"))
        .addSeparatorComponents(SeparatorBuilder())
        .addTextDisplayComponents(TextDisplayBuilder().setContent("Message en container v2"))
        .addActionRowComponents(ActionRowBuilder().addComponents(like_btn))
    )

    await send_message(ctx, components=[card], flags=MessageFlags.IS_COMPONENTS_V2)


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return
    if interaction.data.get("custom_id") != "card_like":
        return
    await interaction.response.send_message("Like recu", ephemeral=True)


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    bot.run(TOKEN)
