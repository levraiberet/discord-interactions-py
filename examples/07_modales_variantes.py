"""Exemple 07 - Variantes de modales modernes.

Commande:
- !modales
"""

import json
import os
import discord
from discord.ext import commands

from discord_interactions import (
    create_button,
    create_button_row,
    create_text_input,
    create_select_menu,
    create_radio_group,
    create_checkbox_group,
    create_checkbox,
    create_label_component,
    create_text_display_component,
    create_modal,
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


@bot.command(name="modales")
async def cmd_modales(ctx: commands.Context):
    row_1 = create_button_row(
        create_button("open_modal_text", label="Text", style="Primary"),
        create_button("open_modal_select", label="Select", style="Secondary"),
        create_button("open_modal_radio", label="Radio", style="Success"),
    )
    row_2 = create_button_row(
        create_button("open_modal_checks", label="Checkboxes", style="Danger"),
    )

    await send_message(
        ctx,
        content="Choisis une variante de modale",
        components=[row_1, row_2],
    )


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id", "")

        if custom_id == "open_modal_text":
            modal = create_modal(
                "mv_text",
                "Modale Texte",
                create_text_display_component("Text input court + paragraphe"),
                create_label_component("Pseudo", component=create_text_input("pseudo", "Pseudo", style="Short")),
                create_label_component(
                    "Presentation",
                    component=create_text_input("bio", "Presentation", style="Paragraph", required=False),
                ),
            )
        elif custom_id == "open_modal_select":
            modal = create_modal(
                "mv_select",
                "Modale Select",
                create_text_display_component("Select menu dans une modale"),
                create_label_component(
                    "Langue",
                    component=create_select_menu(
                        "lang",
                        placeholder="Choisis",
                        options=[
                            {"label": "Francais", "value": "fr"},
                            {"label": "English", "value": "en"},
                            {"label": "Espanol", "value": "es"},
                        ],
                        min_values=1,
                        max_values=1,
                        required=True,
                    ),
                ),
            )
        elif custom_id == "open_modal_radio":
            modal = create_modal(
                "mv_radio",
                "Modale Radio",
                create_text_display_component("Choix unique via radio group"),
                create_label_component(
                    "Mode",
                    component=create_radio_group(
                        "mode",
                        options=[
                            {"label": "Rapide", "value": "fast"},
                            {"label": "Equilibre", "value": "balanced", "default": True},
                            {"label": "Precision", "value": "precise"},
                        ],
                        required=True,
                    ),
                ),
            )
        elif custom_id == "open_modal_checks":
            modal = create_modal(
                "mv_checks",
                "Modale Checkboxes",
                create_text_display_component("Checkbox group + checkbox simple"),
                create_label_component(
                    "Options",
                    component=create_checkbox_group(
                        "features",
                        options=[
                            {"label": "Logs", "value": "logs", "default": True},
                            {"label": "Backup", "value": "backup"},
                            {"label": "Alerts", "value": "alerts"},
                        ],
                        min_values=0,
                        max_values=3,
                        required=False,
                    ),
                ),
                create_label_component("Consentement", component=create_checkbox("consent", default=False)),
            )
        else:
            return

        await send_modal(
            interaction,
            custom_id=modal["custom_id"],
            title=modal["title"],
            components=modal["components"],
        )
        return

    if interaction.type == discord.InteractionType.modal_submit:
        modal_id = interaction.data.get("custom_id", "")
        if not modal_id.startswith("mv_"):
            return

        values = _extract_modal_fields(interaction.data)
        text = "Resultat modale:\n```json\n" + json.dumps(values, ensure_ascii=True, indent=2) + "\n```"
        await respond_to_interaction(interaction, content=text, ephemeral=True)


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    bot.run(TOKEN)
