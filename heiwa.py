import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import os

# ===== CONFIGURATION DES SALONS =====
WELCOME_CHANNEL_ID = 1425082379768303649
LEAVE_CHANNEL_ID = 1425083330251980840

# ===== CONFIG BOT =====
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ===== FONCTION POUR AFFICHER L'URL =====
def get_repl_url():
    repl_name = os.getenv('REPL_SLUG')
    repl_owner = os.getenv('REPL_OWNER')

    print("=" * 60)
    print("🌐 INFORMATIONS URL REPLIT")
    print("=" * 60)

    if repl_name and repl_owner:
        url = f"https://{repl_name}.{repl_owner}.repl.co"
        print(f"✅ URL de votre Repl: {url}")
    else:
        print("❌ Impossible de déterminer l'URL automatiquement")

    return url if repl_name and repl_owner else None


# ===== ÉVÉNEMENTS =====
@bot.event
async def on_ready():
    print(f'🤖 {bot.user} est connecté et prêt!')
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="le serveur 👀"),
        status=discord.Status.online
    )


# AJOUT : Empêche le bot de répondre à ses propres messages
@bot.event
async def on_message(message):
    # Ignore les messages du bot lui-même
    if message.author == bot.user:
        return
    
    # Traite les commandes normalement
    await bot.process_commands(message)


# AJOUT : Gestion des erreurs pour éviter les réponses multiples
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu n'as pas les permissions nécessaires.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Membre introuvable.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Il manque des arguments. Utilise `!help` pour voir la syntaxe.")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore les commandes inexistantes silencieusement
    else:
        print(f"Erreur non gérée: {error}")


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f"Bienvenue sur Heiwa, {member.mention} ! 🎉")


@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(LEAVE_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="Au revoir 👋",
            description=f"{member.name} a quitté le serveur.",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        await channel.send(embed=embed)


# ===== COMMANDES =====
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong ! 🏓 Latence : {round(bot.latency * 1000)}ms")


@bot.command(name="help")
async def custom_help(ctx):
    embed = discord.Embed(
        title="📜 Commandes disponibles",
        description="Voici la liste des commandes",
        color=discord.Color.blue()
    )
    embed.add_field(name="!ping", value="Vérifie la latence du bot", inline=False)
    embed.add_field(name="!mute @membre [durée]", value="Mute un membre", inline=False)
    embed.add_field(name="!unmute @membre", value="Unmute un membre", inline=False)
    embed.add_field(name="!ban @membre [raison]", value="Bannir un membre", inline=False)
    embed.add_field(name="!unban [nom/id]", value="Débannir un membre", inline=False)
    await ctx.send(embed=embed)


# ===== MUTING / UNMUTING =====
@bot.command(name='mute')
@commands.has_permissions(manage_roles=True)
async def mute_member(ctx, member: discord.Member, duration: int = 10, *, raison="Aucune raison fournie"):
    if member == ctx.author:
        return await ctx.send("❌ Tu ne peux pas te mute toi-même !")

    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted", color=discord.Color.dark_gray())
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)

    await member.add_roles(muted_role, reason=raison)
    await ctx.send(f"🔇 {member.mention} est maintenant mute pour {duration} minutes.")

    await asyncio.sleep(duration * 60)
    await member.remove_roles(muted_role, reason="Fin du mute automatique")
    await ctx.send(f"🔊 {member.mention} a été démuté automatiquement.")


@bot.command(name='unmute')
@commands.has_permissions(manage_roles=True)
async def unmute_member(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role in member.roles:
        await member.remove_roles(muted_role, reason="Unmute manuel")
        await ctx.send(f"🔊 {member.mention} a été démuté.")
    else:
        await ctx.send("❌ Ce membre n'est pas muté.")


# ===== BAN / UNBAN =====
@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban_member(ctx, member: discord.Member, *, raison="Aucune raison fournie"):
    if member == ctx.author:
        return await ctx.send("❌ Tu ne peux pas te bannir toi-même !")
    await member.ban(reason=raison)
    await ctx.send(f"🚫 {member.mention} a été banni.\nRaison : {raison}")


@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban_member(ctx, *, identifiant: str):
    bans = await ctx.guild.bans()
    for ban_entry in bans:
        if ban_entry.user.name.lower() == identifiant.lower() or str(ban_entry.user.id) == identifiant:
            await ctx.guild.unban(ban_entry.user)
            await ctx.send(f"✅ {ban_entry.user} a été débanni.")
            return
    await ctx.send("❌ Aucun utilisateur trouvé.")


# ===== LANCEMENT =====
if __name__ == "__main__":
    try:
        from keep_alive import keep_alive
        keep_alive()
        import time
        time.sleep(2)
        get_repl_url()

        token = os.environ.get('BOT_TOKEN')
        if not token:
            print("❌ BOT_TOKEN non trouvé.")
            exit()

        bot.run(token)

    except Exception as e:
        print(f"❌ ERREUR inattendue: {e}")
