import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import os

# ===== CONFIGURATION DES SALONS =====
WELCOME_CHANNEL_ID = 1425082379768303649
LEAVE_CHANNEL_ID = 1425083330251980840

# Configuration du bot
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
        print(f"🔧 Nom du Repl: {repl_name}")
        print(f"👤 Propriétaire: {repl_owner}")
    else:
        print("❌ Impossible de déterminer l'URL automatiquement")
        print("💡 Format manuel: https://nom-du-repl.nom-utilisateur.repl.co")
        print("🔍 Vérifiez dans l'onglet 'Webview' de Replit")

    print("=" * 60)
    return url if repl_name and repl_owner else None

# ===== ÉVÉNEMENTS =====
@bot.event
async def on_ready():
    print(f'🤖 {bot.user} est connecté et prêt!')
    print(f'📊 Serveurs: {len(bot.guilds)}')
    print(f'👥 Utilisateurs: {len(set(bot.get_all_members()))}')
    print('=' * 50)

    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="le serveur 👀"),
        status=discord.Status.online
    )

# ===== COMMANDES ET ÉVÉNEMENTS SUPPLÉMENTAIRES =====
# (Ton code pour on_member_join, on_member_remove, commandes comme ban, mute, unmute, dmall, dmrole, etc.)
# … (Tout ton code précédent reste inchangé ici)
# Je ne l’ai pas recollé pour ne pas alourdir, mais il doit être intégré tel quel.

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
            print("💡 Ajoutez votre token Discord dans l'onglet 'Secrets' de Replit")
            exit()
        else:
            print(f"✅ Token Discord trouvé: {token[:10]}...{token[-5:]}")

        print("🔄 Tentative de connexion du bot...")
        bot.run(token)

    except discord.LoginFailure:
        print("❌ ERREUR: Token Discord invalide!")
        print("💡 Vérifiez votre token sur Discord Developer Portal")

    except discord.PrivilegedIntentsRequired:
        print("❌ ERREUR: Intents privilégiés requis!")
        print("💡 Activez les intents dans Discord Developer Portal > Bot > Privileged Gateway Intents")

    except discord.HTTPException as e:
        print(f"❌ ERREUR HTTP Discord: {e}")
        print("💡 Problème de connexion à Discord")

    except Exception as e:
        print(f"❌ ERREUR inattendue: {e}")
        print(f"💡 Type d'erreur: {type(e).__name__}")
        import traceback
        traceback.print_exc()
