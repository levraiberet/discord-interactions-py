"""Exemple 08 - Modale avec File Upload (type 19).

Commande:
- !modalefile
"""

import json
import os
import discord
from discord.ext import commands

from discord_interactions import (
    create_button,
    create_button_row,
    create_modal,
    create_label_component,
    create_text_display_component,
    create_text_input,
    create_file_upload_component,
    send_message,
    send_modal,
    respond_to_interaction,
)

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def _extract_modal_fields(modal_data: dict) -> dict:
    values = {}

    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
            return

        if not isinstance(node, dict):
            return

        cid = node.get("custom_id")
        if cid:
            if "value" in node:
                values[cid] = node.get("value")
            elif "values" in node:
                values[cid] = node.get("values")

        if "component" in node:
            walk(node["component"])
        if "components" in node:
            walk(node["components"])

    walk(modal_data.get("components", []))
    return values


@bot.command(name="modalefile")
async def cmd_modale_file(ctx: commands.Context):
    btn = create_button("open_modal_file", label="Ouvrir modale fichier", style="Primary")
    await send_message(ctx, content="Demo modale file upload", components=[create_button_row(btn)])


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data.get("custom_id") != "open_modal_file":
            return

        modal = create_modal(
            "mv_file_upload",
            "Upload de fichier",
            create_text_display_component(
                "Selon le client Discord, le file upload en modale peut etre limite."
            ),
            create_label_component(
                "Titre",
                component=create_text_input("title", "Titre", style="Short", required=True),
            ),
            create_label_component(
                "Piece jointe",
                component=create_file_upload_component(
                    "proof_files",
                    min_values=1,
                    max_values=3,
                    required=True,
                ),
            ),
        )

        await send_modal(
            interaction,
            custom_id=modal["custom_id"],
            title=modal["title"],
            components=modal["components"],
        )
        return

    if interaction.type == discord.InteractionType.modal_submit:
        if interaction.data.get("custom_id") != "mv_file_upload":
            return

        values = _extract_modal_fields(interaction.data)
        text = "Resultat modale:\n```json\n" + json.dumps(values, ensure_ascii=True, indent=2) + "\n```"
        await respond_to_interaction(interaction, content=text, ephemeral=True)


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    bot.run(TOKEN)
