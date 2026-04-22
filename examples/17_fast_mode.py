"""Exemple 17 - Mode fast (version allegee mais complete).

Commandes:
- !fastticket
- !fastpoll <question>

Montre:
- creation rapide de containers/boutons
- reception des boutons avec ButtonRouter
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
    ButtonRouter,
    quick_button,
    quick_row,
    quick_send_container,
    respond_to_interaction,
)

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
router = ButtonRouter()

# Petit stockage in-memory pour le sondage
votes = {}


@bot.command(name="fastticket")
async def cmd_fast_ticket(ctx: commands.Context):
    ticket_id = f"T-{ctx.message.id % 10000:04d}"

    close_btn = quick_button(
        "fast_ticket_close",
        "Fermer",
        style="Danger",
        data={"ticket_id": ticket_id, "owner_id": ctx.author.id},
    )

    await quick_send_container(
        ctx,
        title="Ticket support",
        lines=[
            f"ID: `{ticket_id}`",
            f"Createur: {ctx.author.mention}",
            "Statut: ouvert",
        ],
        color=0x57F287,
        buttons=[close_btn],
        separator_between_lines=True,
    )


@bot.command(name="fastpoll")
async def cmd_fast_poll(ctx: commands.Context, *, question: str):
    poll_id = str(ctx.message.id)
    options = ["Oui", "Non", "Peut-etre"]

    votes[poll_id] = {idx: set() for idx in range(len(options))}

    buttons = [
        quick_button(
            "fast_poll_vote",
            f"{label} (0)",
            style="Primary",
            data={"poll_id": poll_id, "idx": idx, "label": label},
        )
        for idx, label in enumerate(options)
    ]

    await ctx.send(
        f"Sondage: **{question}**",
        components=[quick_row(buttons)],
    )


@router.on("fast_ticket_close")
async def on_fast_ticket_close(interaction: discord.Interaction, data: dict):
    owner_id = int(data.get("owner_id", 0))
    ticket_id = data.get("ticket_id", "?")

    if interaction.user.id != owner_id:
        await respond_to_interaction(
            interaction,
            content="Seul le createur peut fermer ce ticket.",
            ephemeral=True,
        )
        return

    await respond_to_interaction(
        interaction,
        content=f"Ticket `{ticket_id}` ferme.",
        update=True,
    )


@router.on("fast_poll_vote")
async def on_fast_poll_vote(interaction: discord.Interaction, data: dict):
    poll_id = str(data.get("poll_id", ""))
    option_idx = int(data.get("idx", 0))

    if poll_id not in votes:
        await respond_to_interaction(interaction, content="Sondage expire.", ephemeral=True)
        return

    # Un seul vote par personne
    for bucket in votes[poll_id].values():
        bucket.discard(interaction.user.id)
    votes[poll_id][option_idx].add(interaction.user.id)

    # Reconstruction rapide des boutons a partir de la structure actuelle
    row = interaction.message.components[0]
    buttons = []
    for idx, component in enumerate(getattr(row, "children", [])):
        base_label = component.label.rsplit(" (", 1)[0]
        count = len(votes[poll_id].get(idx, set()))
        buttons.append(
            quick_button(
                "fast_poll_vote",
                f"{base_label} ({count})",
                style="Primary",
                data={"poll_id": poll_id, "idx": idx, "label": base_label},
            )
        )

    await respond_to_interaction(interaction, content="Vote enregistre.", ephemeral=True)
    await interaction.message.edit(components=[quick_row(buttons)])


@bot.event
async def on_interaction(interaction: discord.Interaction):
    handled = await router.handle(interaction)
    if handled:
        return


@bot.event
async def on_ready():
    print(f"Bot pret: {bot.user}")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    bot.run(TOKEN)
