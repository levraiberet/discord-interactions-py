"""Exemple 16 - Allowed mentions + disable auto par message_id.

Commandes:
- !allowedparse
- !containerexpire [secondes]
- !expireid <message_id> <secondes>
"""

import os
import sys
from pathlib import Path

import discord
from discord.ext import commands

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from discord_interactions import (
    ActionRowBuilder,
    ContainerBuilder,
    TextDisplayBuilder,
    create_button,
    defer_interaction,
    disable_all_by_message_id,
    get_base_custom_id,
    send_followup,
    send_message,
)

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command(name="allowedparse")
async def cmd_allowed_parse(ctx: commands.Context):
    # Style Discord.js-like: parse vide, on whiteliste uniquement l'auteur.
    allowed_mentions = {
        "parse": [],
        "users": [ctx.author.id],
        "roles": [],
        "repliedUser": False,
    }

    await send_message(
        ctx,
        content=(
            f"Salut <@{ctx.author.id}>. "
            "Le @everyone est ecrit mais ne ping pas: @everyone"
        ),
        allowed_mentions=allowed_mentions,
    )


@bot.command(name="containerexpire")
async def cmd_container_expire(ctx: commands.Context, seconds: int = 20):
    seconds = max(1, min(seconds, 3600))

    button = create_button("demo_click", label="Je marche encore", style="Primary")
    card = (
        ContainerBuilder()
        .setAccentColor(0x0EA5E9)
        .addTextDisplayComponents(
            TextDisplayBuilder().setContent(
                f"## Expiration auto\nCe container sera verrouille dans {seconds}s."
            )
        )
        .addActionRowComponents(ActionRowBuilder().addComponents(button))
    )

    msg = await send_message(ctx, components=[card])
    disable_all_by_message_id(ctx.channel, msg.id, delay_ms=seconds * 1000)

    await ctx.send(f"Top. Le message `{msg.id}` sera desactive dans {seconds}s.")


@bot.command(name="expireid")
async def cmd_expire_id(ctx: commands.Context, message_id: str, seconds: int):
    try:
        target_id = int(message_id)
    except ValueError:
        await ctx.send("ID invalide.")
        return

    seconds = max(1, min(seconds, 3600))
    disable_all_by_message_id(ctx.channel, target_id, delay_ms=seconds * 1000)
    await ctx.send(f"Planifie: disable all du message `{target_id}` dans {seconds}s.")


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    custom_id = interaction.data.get("custom_id", "")
    base_id = get_base_custom_id(custom_id)

    if base_id == "demo_click":
        await defer_interaction(interaction, update=False)
        await send_followup(
            interaction,
            content="Interaction recue. Si tu vois ce message, le container n'est pas encore expire.",
            ephemeral=True,
        )


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    bot.run(TOKEN)
