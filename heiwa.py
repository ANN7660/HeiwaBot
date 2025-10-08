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

# Désactive la commande help intégrée
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
    print("=" * 60)
    return url if repl_name and repl_owner else None

# ===== ÉVÉNEMENTS =====
@bot.event
async def on_ready():
    print(f'🤖 {bot.user} est connecté et prêt!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="le serveur 👀"), status=discord.Status.online)

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="🎉 Bienvenue !", description=f"Bienvenue sur **Heiwa**, {member.mention} !", color=discord.Color.green(), timestamp=datetime.now())
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(LEAVE_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="😢 Au revoir", description=f"{member.display_name} nous a quitté...", color=discord.Color.red(), timestamp=datetime.now())
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

# ===== COMMANDE PING =====
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"🏓 Pong ! Latence : {round(bot.latency * 1000)}ms")

# ===== COMMANDE HELP =====
@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(title="📜 Commandes disponibles", description="Voici les commandes disponibles :", color=discord.Color.blurple())
    embed.add_field(name="!ping", value="Test la latence du bot", inline=False)
    embed.add_field(name="!mute @membre durée raison", value="Mute un membre", inline=False)
    embed.add_field(name="!unmute @membre", value="Démute un membre", inline=False)
    embed.add_field(name="!ban @membre raison", value="Ban un membre", inline=False)
    embed.add_field(name="!unban identifiant", value="Déban un membre", inline=False)
    await ctx.send(embed=embed)

# ===== COMMANDE MUTE =====
@bot.command(name='mute')
@commands.has_permissions(manage_roles=True)
async def mute_member(ctx, member: discord.Member, duration: int = 10, *, raison="Aucune raison fournie"):
    if member == ctx.author:
        return await ctx.send("❌ Tu ne peux pas te mute toi-même !")
    if member.top_role >= ctx.author.top_role:
        return await ctx.send("❌ Tu ne peux pas mute quelqu’un avec un rôle supérieur ou égal au tien !")
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted", color=discord.Color.dark_gray())
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False, add_reactions=False)
    if muted_role in member.roles:
        return await ctx.send("❌ Ce membre est déjà muté !")
    await member.add_roles(muted_role, reason=f"Par {ctx.author} - {raison}")
    embed = discord.Embed(title="🔇 Membre muté", description=f"**{member.display_name}** a été muté pour {duration} minutes", color=discord.Color.orange(), timestamp=datetime.now())
    embed.add_field(name="📝 Raison", value=raison, inline=False)
    embed.add_field(name="👮 Par", value=ctx.author.mention, inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)
    await asyncio.sleep(duration * 60)
    if muted_role in member.roles:
        await member.remove_roles(muted_role, reason="Fin du mute automatique")
        unmute_embed = discord.Embed(title="🔊 Démute automatique", description=f"**{member.display_name}** a été démuté", color=discord.Color.green())
        await ctx.send(embed=unmute_embed)

# ===== COMMANDE UNMUTE =====
@bot.command(name='unmute')
@commands.has_permissions(manage_roles=True)
async def unmute_member(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role or muted_role not in member.roles:
        return await ctx.send("❌ Ce membre n’est pas muté !")
    await member.remove_roles(muted_role, reason=f"Par {ctx.author}")
    embed = discord.Embed(title="🔊 Membre démuté", description=f"**{member.display_name}** a été démuté avec succès !", color=discord.Color.green(), timestamp=datetime.now())
    embed.add_field(name="👮 Par", value=ctx.author.mention, inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

# ===== COMMANDE BAN =====
@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban_member(ctx, member: discord.Member, *, raison="Aucune raison fournie"):
    if member == ctx.author:
        return await ctx.send("❌ Tu ne peux pas te bannir toi-même !")
    if member.top_role >= ctx.author.top_role:
        return await ctx.send("❌ Tu ne peux pas bannir quelqu’un avec un rôle supérieur ou égal au tien !")
    try:
        try:
            dm_embed = discord.Embed(title="🚫 Tu as été banni !", description=f"Serveur : **{ctx.guild.name}**", color=discord.Color.red(), timestamp=datetime.now())
            dm_embed.add_field(name="📝 Raison :", value=raison, inline=False)
            dm_embed.add_field(name="👮 Par :", value=ctx.author.name, inline=False)
            await member.send(embed=dm_embed)
        except:
            pass
        await member.ban(reason=f"{ctx.author} - {raison}")
        embed = discord.Embed(title="🚫 Membre banni", description=f"**{member.display_name}** a été banni du serveur.", color=discord.Color.red(), timestamp=datetime.now())
        embed.add_field(name="📝 Raison", value=raison, inline=False)
        embed.add_field(name="👮 Par", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("❌ Je n’ai pas la permission de bannir ce membre.")

# ===== COMMANDE UNBAN =====
@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban_member(ctx, *, identifiant: str):
    bans = await ctx.guild.bans()
    identifiant = identifiant.lower()
    for ban_entry in bans:
        user = ban_entry.user
        if user.name.lower() == identifiant or str(user.id) == identifiant:
            await ctx.guild.unban(user, reason=f"Par {ctx.author}")
            embed = discord.Embed(title="✅ Membre débanni", description=f"**{user.name}** a été débanni avec succès !", color=discord.Color.green(), timestamp=datetime.now())
            embed.add_field(name="👮 Par", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            return
    await ctx.send("❌ Aucun utilisateur trouvé avec ce nom ou cet ID.")

# ===== LANCEMENT DU BOT =====
if __name__ == "__main__":
    print("🚀 Démarrage du bot Discord...")
    try:
        from keep_alive import keep_alive
        keep_alive()
        import time
        time.sleep(2)
        get_repl_url()
        token = os.environ.get('BOT_TOKEN')
        if not token:
            print("❌ ERREUR: BOT_TOKEN non trouvé dans les secrets!")
            exit()
        print("✅ Token Discord trouvé")
        bot.run(token)
    except Exception as e:
        print(f"❌ ERREUR inattendue: {e}")
