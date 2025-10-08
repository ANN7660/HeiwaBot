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

bot = commands.Bot(command_prefix='!', intents=intents)


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
        print(f"📋 Copiez cette URL dans UptimeRobot pour maintenir le bot actif!")
    else:
        print("❌ Impossible de déterminer l'URL automatiquement")
    print("=" * 60)
    return url if repl_name and repl_owner else None


# ===== ÉVÉNEMENTS =====
@bot.event
async def on_ready():
    print(f'🤖 {bot.user} est connecté et prêt!')
    print(f'📊 Serveurs: {len(bot.guilds)}')
    print(f'👥 Utilisateurs: {len(set(bot.get_all_members()))}')
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="le serveur 👀"),
        status=discord.Status.online
    )


@bot.event
async def on_member_join(member):
    # Message dans le salon
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel:
        embed = discord.Embed(
            title="🎉 Bienvenue sur Heiwa !",
            description=f"Bienvenue {member.mention} sur **Heiwa** 🎊\nAmuse-toi bien !",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await welcome_channel.send(embed=embed)

    # Message privé
    try:
        dm_embed = discord.Embed(
            title="Bienvenue sur Heiwa 🎉",
            description=f"Salut {member.name}, merci de rejoindre **Heiwa** !\nAmuse-toi bien et lis les règles.",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        dm_embed.set_footer(text="Heiwa Team ❤️")
        await member.send(embed=dm_embed)
    except:
        pass


@bot.event
async def on_member_remove(member):
    leave_channel = bot.get_channel(LEAVE_CHANNEL_ID)
    if leave_channel:
        embed = discord.Embed(
            title="👋 Au revoir !",
            description=f"{member.display_name} a quitté le serveur 😢",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await leave_channel.send(embed=embed)


# ===== COMMANDE HELP =====
@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="📜 Commandes disponibles",
        description="Voici les commandes du bot",
        color=discord.Color.blue()
    )
    embed.add_field(name="!ping", value="Test la latence du bot", inline=False)
    embed.add_field(name="!mute @utilisateur [minutes] [raison]", value="Mute un membre temporairement", inline=False)
    embed.add_field(name="!unmute @utilisateur", value="Démute un membre", inline=False)
    embed.add_field(name="!ban @utilisateur [raison]", value="Bannit un membre", inline=False)
    embed.add_field(name="!unban [nom/id]", value="Débannit un membre", inline=False)
    await ctx.send(embed=embed)


# ===== COMMANDE PING =====
@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latence : **{latency}ms**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


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
        else:
            print(f"✅ Token Discord trouvé: {token[:10]}...{token[-5:]}")

        print("🔄 Tentative de connexion du bot...")
        bot.run(token)

    except discord.LoginFailure:
        print("❌ ERREUR: Token Discord invalide!")

    except discord.PrivilegedIntentsRequired:
        print("❌ ERREUR: Intents privilégiés requis!")

    except discord.HTTPException as e:
        print(f"❌ ERREUR HTTP Discord: {e}")

    except Exception as e:
        print(f"❌ ERREUR inattendue: {e}")
        import traceback
        traceback.print_exc()
