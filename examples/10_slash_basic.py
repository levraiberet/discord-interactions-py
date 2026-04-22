"""Exemple 10 - Commandes slash basiques.

Commandes:
- /ping
- /salut <nom>
- /info

Note: Utilise discord.Client au lieu de commands.Bot pour eviter
les conflits avec le tree de discord.py
"""

import os
import discord

from discord_interactions.slash import (
    SlashManager,
    String,
    option,
    cooldown,
)
from discord_interactions import (
    container,
    textDisplay,
    separator,
    respond_to_interaction,
    MessageFlags,
)

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")


intents = discord.Intents.default()
client = discord.Client(intents=intents)

slash = SlashManager(client, auto_sync=True)

@slash.command(description="Verifie la latence du bot")
@cooldown(1, 5)
async def ping(ctx):
    latence = round(ctx.bot.latency * 1000)

    # Reponse avec container
    card = (container()
        .accent_color(0x57F287)
        .add(textDisplay(f"# Pong!\n**Latence:** {latence}ms"))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
    )


@slash.command(description="Salue quelqu'un")
@option(String("nom", "Le nom de la personne", max_length=32))
async def salut(ctx, nom: str):
    card = (container()
        .accent_color(0x5865F2)
        .add(textDisplay(f"# Bonjour, {nom}!"))
        .add(separator())
        .add(textDisplay(f"Salutation de la part de {ctx.user.mention}"))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
    )


@slash.command(description="Informations sur le serveur")
async def info(ctx):
    if not ctx.guild:
        await ctx.respond("Cette commande fonctionne uniquement dans un serveur", ephemeral=True)
        return

    guild = ctx.guild
    card = (container()
        .accent_color(0xEB459E)
        .add(textDisplay(f"# {guild.name}"))
        .add(separator())
        .add(textDisplay(
            f"**Membres:** {guild.member_count}\n"
            f"**Channels:** {len(guild.channels)}\n"
            f"**Roles:** {len(guild.roles)}\n"
            f"**ID:** `{guild.id}`"
        ))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
    )


@client.event
async def on_ready():
    print(f"Bot pret: {client.user}")
    print("Commandes slash enregistrees:")
    for cmd in slash.get_all_commands():
        print(f"  /{cmd.name}")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    client.run(TOKEN)
