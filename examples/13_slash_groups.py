"""Exemple 13 - Groupes de commandes slash.

Commandes:
- /config view
- /config set <option> <valeur>
- /config reset
"""

import os
import discord

from discord_interactions.slash import (
    SlashManager,
    String,
    option,
    guild_only,
    has_permissions,
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

# Stockage simple (en memoire)
configs = {}

# Creer un groupe de commandes
config = slash.group("config", "Gerer la configuration du serveur")


@config.command(description="Voir la configuration actuelle")
@guild_only()
async def view(ctx):
    guild_config = configs.get(ctx.guild.id, {})

    if not guild_config:
        await ctx.respond("Aucune configuration definie", ephemeral=True)
        return

    config_text = "\n".join([f"**{k}:** `{v}`" for k, v in guild_config.items()])

    card = (container()
        .accent_color(0x3498DB)
        .add(textDisplay("# Configuration"))
        .add(separator())
        .add(textDisplay(config_text))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
    )


@config.command(description="Modifier une option")
@option(String("key", "L'option a modifier", choices=[
    ("Prefix", "prefix"),
    ("Langue", "lang"),
    ("Mode debug", "debug"),
]))
@option(String("valeur", "La nouvelle valeur"))
@has_permissions(manage_guild=True)
@guild_only()
async def set(ctx, key: str, valeur: str):
    if ctx.guild.id not in configs:
        configs[ctx.guild.id] = {}

    configs[ctx.guild.id][key] = valeur

    card = (container()
        .accent_color(0x2ECC71)
        .add(textDisplay("# Configuration mise a jour"))
        .add(separator())
        .add(textDisplay(f"**{key}** = `{valeur}`"))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
    )


@config.command(description="Reinitialiser la configuration")
@has_permissions(administrator=True)
@guild_only()
async def reset(ctx):
    configs.pop(ctx.guild.id, None)

    card = (container()
        .accent_color(0xE74C3C)
        .add(textDisplay("# Configuration reinitialisee"))
        .add(textDisplay("Toutes les options ont ete supprimees."))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
    )


@client.event
async def on_ready():
    print(f"Bot pret: {client.user}")
    print("Groupes de commandes:")
    for name, group in slash._groups.items():
        print(f"  /{name}")
        for cmd_name in group.commands:
            print(f"    /{name} {cmd_name}")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    client.run(TOKEN)
