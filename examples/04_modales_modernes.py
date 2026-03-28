"""Exemple 04 - Modales modernes (Label + composants natifs).

Commande:
- !modal
"""

import os
import discord
from discord.ext import commands

from discord_interactions import (
    create_button,
    create_button_row,
    create_text_input,
    create_label_component,
    create_text_display_component,
    create_radio_group,
    create_checkbox_group,
    create_checkbox,
    create_modal,
    send_message,
    send_modal,
    respond_to_interaction,
)

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command(name="modal")
async def cmd_modal(ctx: commands.Context):
    open_btn = create_button("open_modal_demo", label="Ouvrir la modale", style="Primary")
    await send_message(ctx, content="Clique pour ouvrir", components=[create_button_row(open_btn)])


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data.get("custom_id") != "open_modal_demo":
            return

        name_input = create_text_input("name", "Nom", style="Short")
        radio = create_radio_group(
            "mode",
            options=[
                {"label": "Rapide", "value": "fast"},
                {"label": "Precision", "value": "precise"},
            ],
            required=True,
        )
        checks = create_checkbox_group(
            "options",
            options=[
                {"label": "Logs", "value": "logs"},
                {"label": "Backup", "value": "backup"},
            ],
            min_values=0,
            max_values=2,
            required=False,
        )
        single_check = create_checkbox("consent", default=False)

        modal = create_modal(
            "demo_modal_modern",
            "Config",
            create_text_display_component("Exemple complet des champs modernes"),
            create_label_component("Ton nom", component=name_input),
            create_label_component("Mode", component=radio),
            create_label_component("Options", component=checks),
            create_label_component("Confirmer", component=single_check),
        )

        await send_modal(
            interaction,
            custom_id=modal["custom_id"],
            title=modal["title"],
            components=modal["components"],
        )
        return

    if interaction.type == discord.InteractionType.modal_submit:
        if interaction.data.get("custom_id") != "demo_modal_modern":
            return

        await respond_to_interaction(interaction, content="Modale recue", ephemeral=True)


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    bot.run(TOKEN)
