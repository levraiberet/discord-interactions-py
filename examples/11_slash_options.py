"""Exemple 11 - Options avancees des commandes slash.

Commandes:
- /calcul <a> <b> <operation>
- /profil <utilisateur> [visible]
- /couleur <hex>
"""

import os
import discord

from discord_interactions.slash import (
    SlashManager,
    String,
    Integer,
    Boolean,
    User,
    option,
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


@slash.command(description="Effectue un calcul")
@option(Integer("a", "Premier nombre", min_value=-1000, max_value=1000))
@option(Integer("b", "Deuxieme nombre", min_value=-1000, max_value=1000))
@option(String("operation", "Operation a effectuer", choices=[
    ("Addition", "add"),
    ("Soustraction", "sub"),
    ("Multiplication", "mul"),
    ("Division", "div"),
]))
async def calcul(ctx, a: int, b: int, operation: str):
    if operation == "add":
        result = a + b
        symbole = "+"
    elif operation == "sub":
        result = a - b
        symbole = "-"
    elif operation == "mul":
        result = a * b
        symbole = "x"
    elif operation == "div":
        if b == 0:
            await ctx.respond("Division par zero impossible", ephemeral=True)
            return
        result = a / b
        symbole = "/"

    card = (container()
        .accent_color(0x3498DB)
        .add(textDisplay(f"# Calculatrice"))
        .add(separator())
        .add(textDisplay(f"**{a} {symbole} {b} = {result}**"))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
    )


@slash.command(description="Voir le profil d'un utilisateur")
@option(User("utilisateur", "L'utilisateur a voir"))
@option(Boolean("visible", "Visible par tous?", required=False, default=False))
async def profil(ctx, utilisateur: discord.User, visible: bool):
    # Recuperer l'utilisateur depuis l'ID
    user = ctx.bot.get_user(utilisateur) or await ctx.bot.fetch_user(utilisateur)

    card = (container()
        .accent_color(0x2ECC71)
        .add(textDisplay(f"# {user.display_name}"))
        .add(separator())
        .add(textDisplay(
            f"**ID:** `{user.id}`\n"
            f"**Bot:** {'Oui' if user.bot else 'Non'}\n"
            f"**Cree le:** {user.created_at.strftime('%d/%m/%Y')}"
        ))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
        ephemeral=not visible,
    )


@slash.command(description="Definir une couleur hexadecimale")
@option(String(
    "hex",
    "Code couleur (#RRGGBB)",
    pattern=r"^#[0-9A-Fa-f]{6}$",
    pattern_error="Format invalide. Utilisez #RRGGBB (ex: #FF5733)",
))
async def couleur(ctx, hex: str):
    color_int = int(hex[1:], 16)

    card = (container()
        .accent_color(color_int)
        .add(textDisplay(f"# Couleur: {hex}"))
        .add(separator())
        .add(textDisplay(f"Cette bordure est de la couleur {hex}"))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
    )


@client.event
async def on_ready():
    print(f"Bot pret: {client.user}")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    client.run(TOKEN)
