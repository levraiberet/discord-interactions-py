"""Exemple 14 - Autocomplete pour commandes slash.

Commandes:
- /pays <pays> (autocomplete)
- /chercher <requete> (autocomplete dynamique)
"""

import os
import discord

from discord_interactions.slash import (
    SlashManager,
    String,
    option,
    filter_choices,
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

# Liste de pays
PAYS = [
    "France", "Belgique", "Suisse", "Canada", "Luxembourg",
    "Monaco", "Senegal", "Maroc", "Tunisie", "Algerie",
    "Cameroun", "Cote d'Ivoire", "Madagascar", "Haiti",
]

# Liste d'items
ITEMS = [
    {"id": 1, "nom": "Epee de feu", "type": "arme", "rarete": "rare"},
    {"id": 2, "nom": "Bouclier de glace", "type": "armure", "rarete": "epique"},
    {"id": 3, "nom": "Potion de vie", "type": "consommable", "rarete": "commun"},
    {"id": 4, "nom": "Potion de mana", "type": "consommable", "rarete": "commun"},
    {"id": 5, "nom": "Arc elfique", "type": "arme", "rarete": "legendaire"},
    {"id": 6, "nom": "Casque du dragon", "type": "armure", "rarete": "epique"},
    {"id": 7, "nom": "Anneau de puissance", "type": "accessoire", "rarete": "rare"},
    {"id": 8, "nom": "Amulette magique", "type": "accessoire", "rarete": "rare"},
]

RARETE_COLORS = {
    "commun": 0x95A5A6,
    "rare": 0x3498DB,
    "epique": 0x9B59B6,
    "legendaire": 0xF39C12,
}


@slash.command(description="Selectionner un pays francophone")
@option(String("pays", "Choisir un pays", autocomplete=True))
async def pays(ctx, pays: str):
    if pays not in PAYS:
        await ctx.respond(f"Pays inconnu: {pays}", ephemeral=True)
        return

    card = (container()
        .accent_color(0x3498DB)
        .add(textDisplay(f"# {pays}"))
        .add(separator())
        .add(textDisplay(f"Tu as choisi **{pays}** comme pays francophone."))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
    )


@slash.autocomplete("pays", "pays")
async def pays_autocomplete(actx):
    return filter_choices([(p, p) for p in PAYS], actx.value)


@slash.command(description="Chercher un item")
@option(String("requete", "Nom de l'item", autocomplete=True))
async def chercher(ctx, requete: str):
    item = next((i for i in ITEMS if i["nom"].lower() == requete.lower()), None)

    if not item:
        await ctx.respond(f"Item introuvable: {requete}", ephemeral=True)
        return

    color = RARETE_COLORS.get(item["rarete"], 0x95A5A6)

    card = (container()
        .accent_color(color)
        .add(textDisplay(f"# {item['nom']}"))
        .add(separator())
        .add(textDisplay(
            f"**Type:** {item['type'].capitalize()}\n"
            f"**Rarete:** {item['rarete'].capitalize()}\n"
            f"**ID:** `{item['id']}`"
        ))
    )

    await respond_to_interaction(
        ctx.interaction,
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
    )


@slash.autocomplete("chercher", "requete")
async def chercher_autocomplete(actx):
    query = actx.value.lower()
    results = []

    for item in ITEMS:
        nom = item["nom"]
        if query in nom.lower():
            results.append((f"{nom} [{item['rarete']}]", nom))

    return results[:25]


@client.event
async def on_ready():
    print(f"Bot pret: {client.user}")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    client.run(TOKEN)
