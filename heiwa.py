import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import os
import sys

# ===== CONFIGURATION DES SALONS =====
WELCOME_CHANNEL_ID = 1423555370948886581
LEAVE_CHANNEL_ID = 1425083330251980840

# ===== CONFIG BOT =====
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ===== PROTECTION CONTRE INSTANCES MULTIPLES =====
processed_commands = {}  # Cache des commandes récentes

def is_duplicate_command(ctx):
    """Vérifie si la commande a déjà été traitée récemment"""
    key = f"{ctx.message.id}_{ctx.command.name}"
    current_time = datetime.now().timestamp()
    
    # Nettoyage du cache (supprime les entrées > 5 secondes)
    to_remove = [k for k, v in processed_commands.items() if current_time - v > 5]
    for k in to_remove:
        del processed_commands[k]
    
    # Vérifie si déjà traité
    if key in processed_commands:
        return True
    
    processed_commands[key] = current_time
    return False


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
    print(f'📊 Instance ID: {id(bot)}')  # Debug pour voir les instances
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="le serveur 👀"),
        status=discord.Status.online
    )


@bot.event
async def on_message(message):
    # Ignore les messages du bot lui-même
    if message.author == bot.user:
        return
    
    # Traite les commandes normalement
    await bot.process_commands(message)


@bot.event
async def on_command(ctx):
    """Hook appelé avant chaque commande"""
    if is_duplicate_command(ctx):
        print(f"⚠️ Commande dupliquée détectée: {ctx.command.name}")
        # Stop l'exécution de la commande
        raise commands.CommandError("Duplicate")


@bot.event
async def on_command_error(ctx, error):
    # Ignore les doublons silencieusement
    if isinstance(error, commands.CommandError) and str(error) == "Duplicate":
        return
    
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


# Événement de départ retiré


# ===== COMMANDES =====
@bot.command(name="ping")
async def ping(ctx):
    embed = discord.Embed(
        title="🏓 Pong !",
        description=f"Latence : **{round(bot.latency * 1000)}ms**",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"Demandé par {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    await ctx.send(embed=embed)


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
        embed = discord.Embed(
            title="❌ Erreur",
            description="Tu ne peux pas te mute toi-même !",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed)

    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted", color=discord.Color.dark_gray())
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)

    await member.add_roles(muted_role, reason=raison)
    
    embed = discord.Embed(
        title="🔇 Membre mute",
        description=f"{member.mention} a été mute",
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )
    embed.add_field(name="Durée", value=f"{duration} minutes", inline=True)
    embed.add_field(name="Raison", value=raison, inline=True)
    embed.set_footer(text=f"Par {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    await ctx.send(embed=embed)

    await asyncio.sleep(duration * 60)
    await member.remove_roles(muted_role, reason="Fin du mute automatique")
    
    embed_unmute = discord.Embed(
        title="🔊 Démute automatique",
        description=f"{member.mention} a été démuté automatiquement",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    await ctx.send(embed=embed_unmute)


@bot.command(name='unmute')
@commands.has_permissions(manage_roles=True)
async def unmute_member(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role in member.roles:
        await member.remove_roles(muted_role, reason="Unmute manuel")
        embed = discord.Embed(
            title="🔊 Membre démuté",
            description=f"{member.mention} a été démuté avec succès",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Par {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Erreur",
            description="Ce membre n'est pas muté.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


# ===== BAN / UNBAN =====
@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban_member(ctx, member: discord.Member, *, raison="Aucune raison fournie"):
    if member == ctx.author:
        embed = discord.Embed(
            title="❌ Erreur",
            description="Tu ne peux pas te bannir toi-même !",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed)
    
    await member.ban(reason=raison)
    embed = discord.Embed(
        title="🚫 Membre banni",
        description=f"{member.mention} a été banni du serveur",
        color=discord.Color.dark_red(),
        timestamp=datetime.now()
    )
    embed.add_field(name="Raison", value=raison, inline=False)
    embed.set_footer(text=f"Par {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    await ctx.send(embed=embed)


@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban_member(ctx, *, identifiant: str):
    bans = await ctx.guild.bans()
    for ban_entry in bans:
        if ban_entry.user.name.lower() == identifiant.lower() or str(ban_entry.user.id) == identifiant:
            await ctx.guild.unban(ban_entry.user)
            embed = discord.Embed(
                title="✅ Membre débanni",
                description=f"**{ban_entry.user}** a été débanni avec succès",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Par {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            await ctx.send(embed=embed)
            return
    
    embed = discord.Embed(
        title="❌ Erreur",
        description="Aucun utilisateur trouvé avec cet identifiant.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)


# ===== LANCEMENT =====
if __name__ == "__main__":
    try:
        # Pour Render, pas besoin de keep_alive
        # Mais garde-le si tu l'utilises encore
        try:
            from keep_alive import keep_alive
            keep_alive()
            import time
            time.sleep(2)
        except ImportError:
            print("ℹ️ keep_alive non disponible (normal sur Render)")
        
        get_repl_url()

        token = os.environ.get('BOT_TOKEN')
        if not token:
            print("❌ BOT_TOKEN non trouvé.")
            sys.exit(1)

        print("🚀 Démarrage du bot...")
        bot.run(token)

    except Exception as e:
        print(f"❌ ERREUR inattendue: {e}")
        sys.exit(1)

