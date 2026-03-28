"""Exemple 06 - custom_id signes.

Commande:
- !secure
"""

import os
import discord
from discord.ext import commands

from discord_interactions import (
    create_signed_button,
    parse_signed_custom_id,
    create_button_row,
    send_message,
    respond_to_interaction,
)

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
SECRET = os.getenv("CUSTOM_ID_SECRET", "dev-secret-change-me")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command(name="secure")
async def cmd_secure(ctx: commands.Context):
    btn = create_signed_button(
        base_id="secure_action",
        secret=SECRET,
        data={"user_id": ctx.author.id},
        ttl_seconds=300,
        label="Action signee",
        style="Primary",
    )
    await send_message(ctx, content="Bouton signe (5 min)", components=[create_button_row(btn)])


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    custom_id = interaction.data.get("custom_id", "")
    base_id, data, is_valid, reason = parse_signed_custom_id(custom_id, secret=SECRET)

    if base_id != "secure_action":
        return

    if not is_valid:
        await respond_to_interaction(interaction, content=f"Signature invalide: {reason}", ephemeral=True)
        return

    await respond_to_interaction(
        interaction,
        content=f"OK pour <@{data.get('user_id')}>",
        ephemeral=True,
    )


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    bot.run(TOKEN)
