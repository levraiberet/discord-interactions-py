"""Exemple 12 - Cooldowns et permissions.

Commandes:
- /spam (cooldown 10s)
- /annonce (cooldown serveur)
- /owner (owner only)
- /solde, /travail (shared cooldown)
"""

import os
import discord

from discord_interactions.slash import (
    SlashManager,
    String,
    User,
    option,
    cooldown,
    guild_cooldown,
    SharedCooldown,
    owner_only,
    guild_only,
    CommandOnCooldown,
)
from discord_interactions import (
    container,
    textDisplay,
    separator,
    respond_to_interaction,
    MessageFlags,
)

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)
slash = SlashManager(client, owner_ids={OWNER_ID}, auto_sync=True)


@slash.command(description="Test de cooldown")
@cooldown(1, 10)
async def spam(ctx):
    card = (container()
        .accent_color(0xE74C3C)
        .add(textDisplay("# Message envoye!"))
        .add(textDisplay("Tu peux reutiliser cette commande dans 10 secondes."))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
    )


@slash.command(description="Annonce limitee par serveur")
@guild_cooldown(3, 60)
@guild_only()
async def annonce(ctx):
    card = (container()
        .accent_color(0xF39C12)
        .add(textDisplay(f"# Annonce de {ctx.user.display_name}"))
        .add(separator())
        .add(textDisplay("Cette commande est limitee a 3 fois par minute pour tout le serveur."))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
    )


@slash.command(description="Commande owner")
@owner_only()
async def owner(ctx):
    card = (container()
        .accent_color(0x9B59B6)
        .add(textDisplay("# Acces Owner"))
        .add(textDisplay("Tu es un owner du bot!"))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
        ephemeral=True,
    )


# Shared cooldown
economie_cd = SharedCooldown("economie", rate=5, per=60)


@slash.command(description="Voir ton solde")
@economie_cd.apply
async def solde(ctx):
    import random
    coins = random.randint(100, 10000)

    card = (container()
        .accent_color(0xF1C40F)
        .add(textDisplay("# Portefeuille"))
        .add(separator())
        .add(textDisplay(f"**Solde:** {coins} pieces"))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
    )


@slash.command(description="Travailler pour gagner des pieces")
@economie_cd.apply
async def travail(ctx):
    import random
    gain = random.randint(10, 100)

    card = (container()
        .accent_color(0x2ECC71)
        .add(textDisplay("# Travail"))
        .add(separator())
        .add(textDisplay(f"Tu as gagne **{gain}** pieces!"))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
    )


@slash.on_error
async def handle_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        await ctx.respond(
            f"Attends **{error.retry_after:.1f}s** avant de reutiliser cette commande",
            ephemeral=True,
        )
        return
    raise error


@client.event
async def on_ready():
    print(f"Bot pret: {client.user}")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    if OWNER_ID == 0:
        print("Warning: OWNER_ID non defini")
    client.run(TOKEN)
