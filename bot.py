import os
import asyncio
import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bot-shield")

TOKEN = os.getenv("DISCORD_TOKEN")
ALLOWED_INVITERS = {
    int(value.strip())
    for value in os.getenv("ALLOWED_INVITER_IDS", "").split(",")
    if value.strip().isdigit()
}
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0") or 0)

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing. Copy .env.example to .env and set it.")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def send_log(guild: discord.Guild, message: str) -> None:
    if not LOG_CHANNEL_ID:
        log.info("%s | %s", guild.name, message)
        return
    channel = guild.get_channel(LOG_CHANNEL_ID)
    if isinstance(channel, discord.TextChannel):
        try:
            await channel.send(message)
        except discord.HTTPException:
            log.exception("Could not send log message")


@bot.event
async def on_ready():
    log.info("Connected as %s (%s)", bot.user, bot.user.id if bot.user else "unknown")
    try:
        synced = await bot.tree.sync()
        log.info("Synced %d application commands", len(synced))
    except discord.HTTPException:
        log.exception("Command sync failed")


@bot.event
async def on_member_join(member: discord.Member):
    if not member.bot:
        return

    # Audit logs can arrive a moment after the member-join event.
    await asyncio.sleep(1.5)
    inviter = None
    try:
        async for entry in member.guild.audit_logs(
            limit=8, action=discord.AuditLogAction.bot_add
        ):
            target = getattr(entry, "target", None)
            if target and target.id == member.id:
                inviter = entry.user
                break
    except discord.Forbidden:
        await send_log(
            member.guild,
            f"⚠️ Impossible de vérifier l'ajout de {member.mention} : "
            "le bot n'a pas la permission Voir les journaux d'audit.",
        )
        return
    except discord.HTTPException:
        log.exception("Audit log lookup failed")
        return

    if inviter is None:
        await send_log(
            member.guild,
            f"⚠️ Nouveau bot détecté : {member.mention}. "
            "Auteur introuvable dans les journaux d'audit ; aucune expulsion automatique.",
        )
        return

    authorized = (
        inviter.id == member.guild.owner_id
        or inviter.id in ALLOWED_INVITERS
    )

    if authorized:
        await send_log(
            member.guild,
            f"✅ Bot autorisé : {member.mention}, ajouté par {inviter.mention}.",
        )
        return

    try:
        await member.kick(reason=f"BOT-SHIELD: ajout non autorisé par {inviter} ({inviter.id})")
        await send_log(
            member.guild,
            f"🛡️ Bot non autorisé expulsé : **{discord.utils.escape_markdown(str(member))}** "
            f"(ID {member.id}), ajouté par {inviter.mention} (ID {inviter.id}).",
        )
    except discord.Forbidden:
        await send_log(
            member.guild,
            f"🚨 Bot non autorisé détecté : {member.mention}, ajouté par {inviter.mention}, "
            "mais je n'ai pas pu l'expulser. Vérifie mon rôle et la permission Expulser des membres.",
        )
    except discord.HTTPException:
        log.exception("Could not kick unauthorized bot")


@bot.tree.command(name="shield-status", description="Vérifie l'état de BOT-SHIELD.")
async def shield_status(interaction: discord.Interaction):
    perms = interaction.guild.me.guild_permissions if interaction.guild and interaction.guild.me else None
    audit_ok = bool(perms and perms.view_audit_log)
    kick_ok = bool(perms and perms.kick_members)
    await interaction.response.send_message(
        f"BOT-SHIELD actif. Journaux d'audit : {'✅' if audit_ok else '❌'} · "
        f"Expulsion : {'✅' if kick_ok else '❌'} · "
        f"Inviteurs autorisés configurés : {len(ALLOWED_INVITERS)}",
        ephemeral=True,
    )


bot.run(TOKEN)
