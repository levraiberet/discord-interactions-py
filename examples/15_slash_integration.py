"""Exemple 15 - Integration slash + containers + boutons.

Commandes:
- /ticket (ouvre un ticket avec container)
- /sondage <question> <option1> <option2> (sondage avec boutons)
"""

import os
import discord
from discord.ext import commands

from discord_interactions.slash import (
    SlashManager,
    String,
    option,
    guild_only,
)
from discord_interactions import (
    container,
    textDisplay,
    separator,
    section,
    create_button,
    create_action_row,
    respond_to_interaction,
    parse_custom_id,
    MessageFlags,
)

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
slash = SlashManager(bot, auto_sync=True)

# Stockage des votes (en memoire)
votes = {}


@slash.command(description="Creer un ticket de support")
@guild_only()
async def ticket(ctx):
    ticket_id = f"T-{ctx.interaction.id % 10000:04d}"

    # Construire un container moderne
    card = (container()
        .accent_color(0x57F287)
        .add(textDisplay(f"# Ticket de Support\n**ID:** `{ticket_id}`"))
        .add(separator())
        .add(textDisplay(
            f"**Createur:** {ctx.user.mention}\n"
            f"**Canal:** {ctx.channel.mention}\n"
            f"**Status:** Ouvert"
        ))
        .add(separator())
        .add(section()
            .text("Cliquez pour fermer ce ticket")
            .button(create_button(
                label="Fermer",
                custom_id="ticket_close",
                data={"id": ticket_id, "user": ctx.user.id},
                style="Danger",
            ))
        )
    )

    await respond_to_interaction(
        ctx.interaction,
        content=f"Ticket cree: **{ticket_id}**",
        components=[card.build()],
        flags=MessageFlags.IS_COMPONENTS_V2,
    )


@slash.command(description="Creer un sondage avec boutons")
@option(String("question", "La question du sondage"))
@option(String("option1", "Premiere option"))
@option(String("option2", "Deuxieme option"))
@option(String("option3", "Troisieme option", required=False))
@guild_only()
async def sondage(ctx, question: str, option1: str, option2: str, option3: str = None):
    sondage_id = str(ctx.interaction.id)
    options = [option1, option2]
    if option3:
        options.append(option3)

    # Initialiser les votes
    votes[sondage_id] = {i: set() for i in range(len(options))}

    # Creer les boutons
    buttons = []
    for i, opt in enumerate(options):
        buttons.append(create_button(
            label=f"{opt} (0)",
            custom_id="sondage_vote",
            data={"sondage": sondage_id, "option": i},
            style="Primary",
        ))

    embed = discord.Embed(
        title=f"Sondage: {question}",
        description="Clique sur un bouton pour voter!",
        color=discord.Color.blue(),
    )
    embed.set_footer(text=f"Cree par {ctx.user.name}")

    await respond_to_interaction(
        ctx.interaction,
        embed=embed,
        components=[create_action_row(buttons)],
    )


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    custom_id = interaction.data.get("custom_id", "")
    base_id, data = parse_custom_id(custom_id)

    # Gestion des votes
    if base_id == "sondage_vote":
        sondage_id = data.get("sondage")
        option_idx = data.get("option", 0)

        if sondage_id not in votes:
            await respond_to_interaction(
                interaction,
                content="Ce sondage n'est plus actif",
                ephemeral=True,
            )
            return

        # Retirer l'ancien vote si present
        for opt_votes in votes[sondage_id].values():
            opt_votes.discard(interaction.user.id)

        # Ajouter le nouveau vote
        votes[sondage_id][option_idx].add(interaction.user.id)

        # Mettre a jour les boutons avec les nouveaux compteurs
        original = interaction.message
        old_buttons = original.components[0].children

        new_buttons = []
        for i, btn in enumerate(old_buttons):
            count = len(votes[sondage_id].get(i, set()))
            # Extraire le label original sans le compteur
            label_parts = btn.label.rsplit(" (", 1)
            base_label = label_parts[0]

            new_buttons.append(create_button(
                label=f"{base_label} ({count})",
                custom_id="sondage_vote",
                data={"sondage": sondage_id, "option": i},
                style="Primary",
            ))

        await respond_to_interaction(
            interaction,
            content="Vote enregistre!",
            ephemeral=True,
        )

        # Editer le message original avec les nouveaux compteurs
        await original.edit(components=[create_action_row(new_buttons)])

    # Gestion fermeture ticket
    elif base_id == "ticket_close":
        ticket_id = data.get("id")
        creator_id = data.get("user")

        if interaction.user.id != creator_id:
            await respond_to_interaction(
                interaction,
                content="Seul le createur peut fermer ce ticket",
                ephemeral=True,
            )
            return

        await respond_to_interaction(
            interaction,
            content=f"Ticket **{ticket_id}** ferme par {interaction.user.mention}",
            update=True,
        )


@bot.event
async def on_ready():
    print(f"Bot pret: {bot.user}")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    bot.run(TOKEN)
