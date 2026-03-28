"""Exemple 09 - Component ops natifs (toggle + pages).

Commandes:
- !toggleops
- !pagesops
- !toggleopsv2
- !pagesopsv2
- !btnonlyembed
- !btnonlycontainerv2
- !disableallid <message_id>
- !disableallreply
"""

import os
import sys
from pathlib import Path
import time
import discord
from discord.ext import commands

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from discord_interactions import (
    ActionRowBuilder,
    ContainerBuilder,
    TextDisplayBuilder,
    create_button,
    create_button_row,
    parse_custom_id,
    get_base_custom_id,
    send_message,
    defer_interaction,
    send_followup,
    row_update_one,
    update_component_one,
    disable_all,
)

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def _page_row(page: int, total: int):
    prev_disabled = page <= 1
    next_disabled = page >= total

    return create_button_row(
        create_button("page_prev", label="Prev", style="Secondary", data={"page": page, "total": total}, disabled=prev_disabled),
        create_button("page_info", label=f"{page}/{total}", style="Primary", data={"page": page, "total": total}, disabled=True),
        create_button("page_next", label="Next", style="Secondary", data={"page": page, "total": total}, disabled=next_disabled),
    )


def _page_row_v2(page: int, total: int) -> ActionRowBuilder:
    return ActionRowBuilder().addComponents(
        create_button("pagev2_prev", label="Prev", style="Secondary", data={"page": page, "total": total}, disabled=(page <= 1)),
        create_button("pagev2_info", label=f"{page}/{total}", style="Primary", data={"page": page, "total": total}, disabled=True),
        create_button("pagev2_next", label="Next", style="Secondary", data={"page": page, "total": total}, disabled=(page >= total)),
    )


def _page_container(page: int, total: int) -> ContainerBuilder:
    return (
        ContainerBuilder()
        .setAccentColor(0x4F46E5)
        .addTextDisplayComponents(TextDisplayBuilder().setContent(f"## Pages V2\nPage {page}/{total} - Contenu de test"))
        .addActionRowComponents(_page_row_v2(page, total))
    )


def _sentinel() -> str:
    return f"S-{int(time.time() * 1000)}"


def _embed_sentinel(message: discord.Message) -> str:
    embeds = getattr(message, "embeds", []) or []
    if not embeds:
        return ""
    footer = embeds[0].footer
    return footer.text if footer else ""


def _container_sentinel(message: discord.Message) -> str:
    comps = getattr(message, "components", []) or []
    for node in comps:
        raw = node.to_dict() if hasattr(node, "to_dict") else node
        for child in raw.get("components", []) or raw.get("children", []) or []:
            if child.get("type") == 10 and isinstance(child.get("content"), str) and child["content"].startswith("SENTINEL:"):
                return child["content"].replace("SENTINEL:", "", 1).strip()
    return ""


@bot.command(name="toggleops")
async def cmd_toggleops(ctx: commands.Context):
    button = create_button("ops_toggle", label="Etat: ON", style="Success", data={"state": "on"})
    await send_message(ctx, content="Toggle test (on/off) - on update les boutons uniquement", components=[create_button_row(button)])


@bot.command(name="pagesops")
async def cmd_pagesops(ctx: commands.Context):
    total = 5
    page = 1
    await send_message(
        ctx,
        content=f"Page {page}/{total} - Contenu de test",
        components=[_page_row(page, total)],
    )


@bot.command(name="toggleopsv2")
async def cmd_toggleops_v2(ctx: commands.Context):
    button = create_button("opsv2_toggle", label="Etat V2: ON", style="Success", data={"state": "on"})
    card = (
        ContainerBuilder()
        .setAccentColor(0x10B981)
        .addTextDisplayComponents(TextDisplayBuilder().setContent("## Toggle V2\nMise a jour d'un seul bouton dans un container"))
        .addActionRowComponents(ActionRowBuilder().addComponents(button))
    )
    await send_message(ctx, components=[card])


@bot.command(name="pagesopsv2")
async def cmd_pagesops_v2(ctx: commands.Context):
    total = 5
    page = 1
    await send_message(ctx, components=[_page_container(page, total)])


@bot.command(name="btnonlyembed")
async def cmd_btnonly_embed(ctx: commands.Context):
    token = _sentinel()
    button = create_button("btnonly_embed", label="Embed BTN: ON", style="Success", data={"state": "on", "sentinel": token})
    embed = discord.Embed(title="Button only test (embed)", description="Le bouton peut changer; la sentinelle embed doit rester identique.")
    embed.set_footer(text=token)
    await send_message(ctx, embed=embed, components=[create_button_row(button)])


@bot.command(name="btnonlycontainerv2")
async def cmd_btnonly_container_v2(ctx: commands.Context):
    token = _sentinel()
    button = create_button("btnonly_v2", label="Container BTN: ON", style="Success", data={"state": "on", "sentinel": token})
    card = (
        ContainerBuilder()
        .setAccentColor(0x0EA5E9)
        .addTextDisplayComponents(TextDisplayBuilder().setContent("## Button only test (container v2)"))
        .addTextDisplayComponents(TextDisplayBuilder().setContent(f"SENTINEL: {token}"))
        .addActionRowComponents(ActionRowBuilder().addComponents(button))
    )
    await send_message(ctx, components=[card])


@bot.command(name="disableallid")
async def cmd_disable_all_id(ctx: commands.Context, message_id: str):
    try:
        target_id = int(message_id)
    except ValueError:
        await ctx.send("ID invalide")
        return

    try:
        msg = await ctx.channel.fetch_message(target_id)
    except Exception:
        await ctx.send("Message introuvable dans ce salon")
        return

    handle = disable_all(msg, delay_ms=0)
    ok = await handle.force_disable()
    await ctx.send("DisableAll OK" if ok else "DisableAll KO (pas de composants ou erreur)")


@bot.command(name="disableallreply")
async def cmd_disable_all_reply(ctx: commands.Context):
    ref = ctx.message.reference
    if not ref or not ref.message_id:
        await ctx.send("Reponds a un message avec cette commande")
        return

    try:
        msg = await ctx.channel.fetch_message(ref.message_id)
    except Exception:
        await ctx.send("Message de reference introuvable")
        return

    handle = disable_all(msg, delay_ms=0)
    ok = await handle.force_disable()
    await ctx.send("DisableAll reply OK" if ok else "DisableAll reply KO")


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    custom_id = interaction.data.get("custom_id", "")
    base_id = get_base_custom_id(custom_id)
    _, data = parse_custom_id(custom_id)

    if base_id == "ops_toggle":
        await defer_interaction(interaction, update=True)

        state = (data or {}).get("state", "on")
        new_state = "off" if state == "on" else "on"
        label = f"Etat: {new_state.upper()}"
        style = "Danger" if new_state == "off" else "Success"

        updated = create_button("ops_toggle", label=label, style=style, data={"state": new_state})
        ok = await update_component_one(
            interaction.message,
            lambda c: get_base_custom_id(c.get("custom_id", "")) == "ops_toggle",
            {
                "custom_id": updated.get("custom_id"),
                "label": updated.get("label"),
                "style": updated.get("style"),
                "disabled": updated.get("disabled", False),
            },
        )
        if not ok:
            await send_followup(interaction, content="Update refuse: cible non unique pour ops_toggle", ephemeral=True)
            return
        await send_followup(interaction, content=f"Toggle -> {new_state}", ephemeral=True)
        return

    if base_id == "btnonly_embed":
        await defer_interaction(interaction, update=True)

        before = _embed_sentinel(interaction.message)
        state = (data or {}).get("state", "on")
        sentinel = (data or {}).get("sentinel", "")
        new_state = "off" if state == "on" else "on"
        updated = create_button("btnonly_embed", label=f"Embed BTN: {new_state.upper()}", style=("Danger" if new_state == "off" else "Success"), data={"state": new_state, "sentinel": sentinel})

        ok = await update_component_one(
            interaction.message,
            lambda c: get_base_custom_id(c.get("custom_id", "")) == "btnonly_embed",
            {
                "custom_id": updated.get("custom_id"),
                "label": updated.get("label"),
                "style": updated.get("style"),
                "disabled": updated.get("disabled", False),
            },
        )

        fresh = await interaction.message.fetch()
        after = _embed_sentinel(fresh)
        if before != after or sentinel != after:
            await send_followup(interaction, content="ERREUR: la sentinelle embed a change", ephemeral=True)
            return

        await send_followup(interaction, content=("OK bouton seul (embed)" if ok else "KO update bouton"), ephemeral=True)
        return

    if base_id == "btnonly_v2":
        await defer_interaction(interaction, update=True)

        before = _container_sentinel(interaction.message)
        state = (data or {}).get("state", "on")
        sentinel = (data or {}).get("sentinel", "")
        new_state = "off" if state == "on" else "on"
        updated = create_button("btnonly_v2", label=f"Container BTN: {new_state.upper()}", style=("Danger" if new_state == "off" else "Success"), data={"state": new_state, "sentinel": sentinel})

        ok = await update_component_one(
            interaction.message,
            lambda c: get_base_custom_id(c.get("custom_id", "")) == "btnonly_v2",
            {
                "custom_id": updated.get("custom_id"),
                "label": updated.get("label"),
                "style": updated.get("style"),
                "disabled": updated.get("disabled", False),
            },
        )

        fresh = await interaction.message.fetch()
        after = _container_sentinel(fresh)
        if before != after or sentinel != after:
            await send_followup(interaction, content="ERREUR: la sentinelle container a change", ephemeral=True)
            return

        await send_followup(interaction, content=("OK bouton seul (container v2)" if ok else "KO update bouton"), ephemeral=True)
        return

    if base_id == "opsv2_toggle":
        await defer_interaction(interaction, update=True)

        state = (data or {}).get("state", "on")
        new_state = "off" if state == "on" else "on"
        label = f"Etat V2: {new_state.upper()}"
        style = "Danger" if new_state == "off" else "Success"

        updated = create_button("opsv2_toggle", label=label, style=style, data={"state": new_state})
        ok = await update_component_one(
            interaction.message,
            lambda c: get_base_custom_id(c.get("custom_id", "")) == "opsv2_toggle",
            {
                "custom_id": updated.get("custom_id"),
                "label": updated.get("label"),
                "style": updated.get("style"),
                "disabled": updated.get("disabled", False),
            },
        )
        if not ok:
            await send_followup(interaction, content="Update refuse: cible non unique pour opsv2_toggle", ephemeral=True)
            return
        await send_followup(interaction, content=f"Toggle V2 -> {new_state}", ephemeral=True)
        return

    if base_id in {"page_prev", "page_next"}:
        await defer_interaction(interaction, update=True)

        page = int((data or {}).get("page", 1))
        total = int((data or {}).get("total", 1))

        if base_id == "page_prev":
            page = max(1, page - 1)
        else:
            page = min(total, page + 1)

        async def page_row_updater(comp):
            cid = get_base_custom_id(comp.get("custom_id", ""))
            if cid == "page_prev":
                return create_button(
                    "page_prev",
                    label="Prev",
                    style="Secondary",
                    data={"page": page, "total": total},
                    disabled=(page <= 1),
                )
            if cid == "page_next":
                return create_button(
                    "page_next",
                    label="Next",
                    style="Secondary",
                    data={"page": page, "total": total},
                    disabled=(page >= total),
                )
            if cid == "page_info":
                return create_button(
                    "page_info",
                    label=f"{page}/{total}",
                    style="Primary",
                    data={"page": page, "total": total},
                    disabled=True,
                )
            return comp

        ok = await row_update_one(
            interaction.message,
            lambda row, _: any(
                get_base_custom_id((x or {}).get("custom_id", "")) in {"page_prev", "page_next", "page_info"}
                for x in (row.get("components") or row.get("children") or [])
            ),
            page_row_updater,
        )
        if not ok:
            await send_followup(interaction, content="Update refuse: cible row non unique pour pagesops", ephemeral=True)
            return
        await send_followup(interaction, content=f"Page active: {page}/{total}", ephemeral=True)
        return

    if base_id in {"pagev2_prev", "pagev2_next"}:
        await defer_interaction(interaction, update=True)

        page = int((data or {}).get("page", 1))
        total = int((data or {}).get("total", 1))

        if base_id == "pagev2_prev":
            page = max(1, page - 1)
        else:
            page = min(total, page + 1)

        async def page_v2_row_updater(comp):
            cid = get_base_custom_id(comp.get("custom_id", ""))
            if cid == "pagev2_prev":
                return create_button("pagev2_prev", label="Prev", style="Secondary", data={"page": page, "total": total}, disabled=(page <= 1))
            if cid == "pagev2_next":
                return create_button("pagev2_next", label="Next", style="Secondary", data={"page": page, "total": total}, disabled=(page >= total))
            if cid == "pagev2_info":
                return create_button("pagev2_info", label=f"{page}/{total}", style="Primary", data={"page": page, "total": total}, disabled=True)
            return comp

        row_ok = await row_update_one(
            interaction.message,
            lambda row, _: any(
                get_base_custom_id((x or {}).get("custom_id", "")) in {"pagev2_prev", "pagev2_next", "pagev2_info"}
                for x in (row.get("components") or row.get("children") or [])
            ),
            page_v2_row_updater,
        )
        if not row_ok:
            await send_followup(interaction, content="Update refuse: cible row non unique pour pagesopsv2", ephemeral=True)
            return

        title_ok = await update_component_one(
            interaction.message,
            lambda c: c.get("type") == 10 and isinstance(c.get("content"), str) and c.get("content", "").startswith("## Pages V2"),
            {"content": f"## Pages V2\nPage {page}/{total} - Contenu de test"},
        )
        if not title_ok:
            await send_followup(interaction, content="Info: row update OK mais titre V2 non unique/non trouve", ephemeral=True)
            return

        await send_followup(interaction, content=f"Page V2 active: {page}/{total}", ephemeral=True)
        return


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Definis DISCORD_BOT_TOKEN")
    bot.run(TOKEN)
