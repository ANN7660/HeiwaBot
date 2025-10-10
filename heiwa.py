import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import os
from keep_alive import keep_alive

# ===== CONFIGURATION DES SALONS =====
# Remplace ces IDs par ceux de tes salons Discord
WELCOME_CHANNEL_ID = 1384523345705570487  # ID du salon de bienvenue
LEAVE_CHANNEL_ID = 9876543210987654321    # ID du salon des départs

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='+', intents=intents)

# Événement de connexion
@bot.event
async def on_ready():
    print(f'🤖 {bot.user} est connecté et prêt!')
    print(f'📊 Serveurs: {len(bot.guilds)}')
    print(f'👥 Utilisateurs: {len(set(bot.get_all_members()))}')
    print('=' * 50)

    # Statut du bot
    await bot.change_presence(
        activity=discord.Game(name="HK je t'aime 💖"),
        status=discord.Status.dnd
    )

# Message de bienvenue avec ID
@bot.event
async def on_member_join(member):
    # Essaie d'abord avec l'ID configuré
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    
    # Si pas trouvé, utilise l'ancien système de recherche par nom
    if not welcome_channel:
        welcome_channels = ['bienvenue', 'général', 'welcome', 'general']
        for channel_name in welcome_channels:
            welcome_channel = discord.utils.get(member.guild.channels, name=channel_name)
            if welcome_channel:
                break
        
        # Si toujours pas trouvé, utilise le salon système
        if not welcome_channel:
            welcome_channel = member.guild.system_channel

    if welcome_channel:
        # Message simple sans embed avec nombre de membres
        member_count = len(member.guild.members)
        await welcome_channel.send(
            f"<a:whitearrow:1426212535262248960> Bienvenue {member.mention} profite bien sur **Heiwa** !\n\n"
            f"<a:whitearrow:1426212535262248960> Nous sommes actuellement **{member_count}** membres sur le serveur ! 🎉"
        )
    else:
        print(f"⚠️ Aucun salon de bienvenue trouvé (ID configuré: {WELCOME_CHANNEL_ID})")
    
    # MP de bienvenue personnalisé
    try:
        dm_embed = discord.Embed(
            title="🎉 Bienvenue sur Heiwa !",
            description=f"""
            Salut {member.mention} ! 👋
            
            Bienvenue sur notre serveur **Heiwa** ! On est ravis de t'accueillir dans notre communauté 🔥
            
            **📝 Pour bien commencer :**
            • N'hésite pas à **parler** dans les salons
            • **Présente-toi** pour qu'on apprenne à te connaître
            • Découvre les différents salons et trouve ta place
            • Amuse-toi bien et respecte les autres membres !
            
            Si tu as des questions, l'équipe est là pour t'aider 😊
            
            **Profite bien de ton séjour parmi nous !** ✨
            """,
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        dm_embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)
        dm_embed.set_footer(text=f"Équipe {member.guild.name}", icon_url=member.guild.icon.url if member.guild.icon else None)
        
        await member.send(embed=dm_embed)
        print(f"✅ MP de bienvenue envoyé à {member.display_name}")
        
    except discord.Forbidden:
        print(f"❌ Impossible d'envoyer un MP à {member.display_name} (MPs fermés)")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi du MP à {member.display_name}: {e}")

# Message de départ désactivé

# ===== COMMANDES POUR CONFIGURER LES SALONS =====

@bot.command(name='set_welcome')
@commands.has_permissions(administrator=True)
async def set_welcome_channel(ctx, channel: discord.TextChannel):
    """🏠 Définit le salon de bienvenue"""
    global WELCOME_CHANNEL_ID
    WELCOME_CHANNEL_ID = channel.id
    
    embed = discord.Embed(
        title="✅ Salon de bienvenue configuré",
        description=f"Les messages de bienvenue seront envoyés dans {channel.mention}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='set_leave')
@commands.has_permissions(administrator=True)  
async def set_leave_channel(ctx, channel: discord.TextChannel):
    """👋 Définit le salon des départs"""
    global LEAVE_CHANNEL_ID
    LEAVE_CHANNEL_ID = channel.id
    
    embed = discord.Embed(
        title="✅ Salon des départs configuré", 
        description=f"Les messages de départ seront envoyés dans {channel.mention}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='channels_config')
@commands.has_permissions(administrator=True)
async def show_channels_config(ctx):
    """📋 Affiche la configuration des salons"""
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    leave_channel = bot.get_channel(LEAVE_CHANNEL_ID)
    
    embed = discord.Embed(
        title="⚙️ Configuration des salons",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🏠 Bienvenue", 
        value=welcome_channel.mention if welcome_channel else "❌ Non configuré",
        inline=False
    )
    
    embed.add_field(
        name="👋 Départs",
        value=leave_channel.mention if leave_channel else "❌ Non configuré", 
        inline=False
    )
    
    await ctx.send(embed=embed)

# ===== COMMANDES DM ALL =====

@bot.command(name='dmall', aliases=['dm_all', 'msgall'])
@commands.has_permissions(administrator=True)
async def dm_all_members(ctx, *, message):
    """📩 Envoie un message privé à tous les membres du serveur"""
    
    # Confirmation de sécurité
    embed = discord.Embed(
        title="⚠️ Confirmation DM ALL",
        description=f"Veux-tu envoyer ce message à **{len(ctx.guild.members)}** membres ?",
        color=discord.Color.yellow()
    )
    embed.add_field(name="📝 Message", value=f"```{message[:500]}{'...' if len(message) > 500 else ''}```", inline=False)
    embed.add_field(name="⏰ Temps limite", value="30 secondes", inline=True)
    embed.add_field(name="⚡ Estimation", value=f"~{len(ctx.guild.members) * 2} secondes", inline=True)
    
    confirm_msg = await ctx.send(embed=embed)
    await confirm_msg.add_reaction("✅")
    await confirm_msg.add_reaction("❌")
    
    def check(reaction, user):
        return (user == ctx.author and 
                str(reaction.emoji) in ["✅", "❌"] and 
                reaction.message.id == confirm_msg.id)
    
    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
        
        if str(reaction.emoji) == "❌":
            await confirm_msg.edit(content="❌ Envoi annulé.", embed=None)
            await confirm_msg.clear_reactions()
            return
            
        if str(reaction.emoji) == "✅":
            await confirm_msg.delete()
            
            # Message de progression
            progress_embed = discord.Embed(
                title="📤 Envoi en cours...",
                description="Envoi des messages privés aux membres",
                color=discord.Color.blue()
            )
            progress_msg = await ctx.send(embed=progress_embed)
            
            # Statistiques d'envoi
            sent_count = 0
            failed_count = 0
            bot_count = 0
            
            # MESSAGE D'INVITATION HYPE ! 🔥
            dm_embed = discord.Embed(
                title="🔥 NOUVEAU SERVEUR DISCORD - REJOINS-NOUS ! 🔥",
                description=f"""
                **{message}**
                
                🎮 **Pourquoi nous rejoindre ?**
                • 🚀 Communauté active et fun
                • 🎊 Events réguliers et concours 
                • 🤝 Team sympathique et accueillante
                • 🏆 Gaming, discussions, et bien plus !
                • 🔴 Serveur tout neuf, sois parmi les premiers !
                
                **👇 CLIQUE ICI POUR NOUS REJOINDRE 👇**
                🌟 **https://discord.gg/BZ6EQkJv6F** 🌟
                """,
                color=discord.Color.gold(),  # Couleur dorée pour attirer l'œil
                timestamp=datetime.now()
            )
            
            # Ajout de champs attractifs
            dm_embed.add_field(name="🎯 Statut", value="**🆕 NOUVEAU SERVEUR**", inline=True)
            dm_embed.add_field(name="⚡ Ambiance", value="**🔥 ULTRA ACTIVE**", inline=True) 
            dm_embed.add_field(name="🎁 Bonus", value="**🌟 EARLY MEMBERS**", inline=True)
            
            # Call-to-action en bas
            dm_embed.add_field(name="🚨 ACTION REQUISE", 
                             value="**Rejoins maintenant et deviens un membre VIP !**\n🔗 https://discord.gg/BZ6EQkJv6F", 
                             inline=False)
            
            # Footer accrocheur
            dm_embed.set_footer(text="⏰ Offre limitée - Ne rate pas ta chance ! ⭐")
            
            # Image du serveur pour crédibilité
            if ctx.guild.icon:
                dm_embed.set_thumbnail(url=ctx.guild.icon.url)
            
            # Envoi aux membres
            for i, member in enumerate(ctx.guild.members):
                # Skip les bots
                if member.bot:
                    bot_count += 1
                    continue
                
                # Skip l'auteur de la commande
                if member == ctx.author:
                    continue
                
                try:
                    await member.send(embed=dm_embed)
                    sent_count += 1
                    
                    # Mise à jour du progrès toutes les 10 personnes
                    if (i + 1) % 10 == 0:
                        progress_embed.description = f"📤 Envoyé à **{sent_count}** membres\n❌ Échecs: **{failed_count}**"
                        await progress_msg.edit(embed=progress_embed)
                    
                    # Délai pour éviter le rate limit
                    await asyncio.sleep(1.5)
                    
                except discord.Forbidden:
                    # L'utilisateur a bloqué les MPs ou les a désactivés
                    failed_count += 1
                except discord.HTTPException:
                    # Erreur réseau ou autre
                    failed_count += 1
                except Exception as e:
                    print(f"Erreur DM pour {member}: {e}")
                    failed_count += 1
            
            # Résultats finaux
            final_embed = discord.Embed(
                title="📊 Résultats DM ALL",
                color=discord.Color.green() if failed_count < sent_count else discord.Color.orange()
            )
            final_embed.add_field(name="✅ Messages envoyés", value=sent_count, inline=True)
            final_embed.add_field(name="❌ Échecs", value=failed_count, inline=True)
            final_embed.add_field(name="🤖 Bots ignorés", value=bot_count, inline=True)
            final_embed.add_field(name="📈 Taux de succès", 
                                value=f"{round((sent_count / (sent_count + failed_count)) * 100, 1)}%" if sent_count + failed_count > 0 else "0%", 
                                inline=True)
            final_embed.set_footer(text=f"Terminé par {ctx.author.display_name}")
            
            await progress_msg.edit(embed=final_embed)
            
    except asyncio.TimeoutError:
        await confirm_msg.edit(content="⏰ Temps écoulé. Envoi annulé.", embed=None)
        await confirm_msg.clear_reactions()

# Commande DM ROLE (bonus)
@bot.command(name='dmrole', aliases=['dm_role'])
@commands.has_permissions(administrator=True)
async def dm_role_members(ctx, role: discord.Role, *, message):
    """📩 Envoie un MP à tous les membres d'un rôle spécifique"""
    
    if not role.members:
        return await ctx.send(f"❌ Aucun membre trouvé avec le rôle **{role.name}**!")
    
    # Confirmation
    embed = discord.Embed(
        title="⚠️ Confirmation DM ROLE",
        description=f"Veux-tu envoyer ce message aux **{len(role.members)}** membres du rôle **{role.name}** ?",
        color=role.color if role.color != discord.Color.default() else discord.Color.yellow()
    )
    embed.add_field(name="📝 Message", value=f"```{message[:500]}{'...' if len(message) > 500 else ''}```", inline=False)
    
    confirm_msg = await ctx.send(embed=embed)
    await confirm_msg.add_reaction("✅")
    await confirm_msg.add_reaction("❌")
    
    def check(reaction, user):
        return (user == ctx.author and 
                str(reaction.emoji) in ["✅", "❌"] and 
                reaction.message.id == confirm_msg.id)
    
    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
        
        if str(reaction.emoji) == "❌":
            await confirm_msg.edit(content="❌ Envoi annulé.", embed=None)
            return
            
        if str(reaction.emoji) == "✅":
            await confirm_msg.delete()
            
            sent_count = 0
            failed_count = 0
            
            dm_embed = discord.Embed(
                title=f"📢 Message pour le rôle {role.name}",
                description=message,
                color=role.color if role.color != discord.Color.default() else discord.Color.green(),
                timestamp=datetime.now()
            )
            dm_embed.add_field(name="👤 Envoyé par", value=ctx.author.display_name, inline=True)
            dm_embed.add_field(name="🎭 Rôle ciblé", value=role.name, inline=True)
            dm_embed.set_footer(text=f"Message du serveur {ctx.guild.name}")
            
            progress_msg = await ctx.send("📤 Envoi en cours...")
            
            for member in role.members:
                if member.bot or member == ctx.author:
                    continue
                    
                try:
                    await member.send(embed=dm_embed)
                    sent_count += 1
                    await asyncio.sleep(1.5)
                except:
                    failed_count += 1
            
            result_embed = discord.Embed(
                title=f"📊 Résultats DM {role.name}",
                color=discord.Color.green()
            )
            result_embed.add_field(name="✅ Envoyés", value=sent_count, inline=True)
            result_embed.add_field(name="❌ Échecs", value=failed_count, inline=True)
            
            await progress_msg.edit(content="", embed=result_embed)
            
    except asyncio.TimeoutError:
        await confirm_msg.edit(content="⏰ Temps écoulé. Envoi annulé.", embed=None)

# ===== COMMANDES DE MODÉRATION =====

# Commande BAN
@bot.command(name='ban', aliases=['bannir'])
@commands.has_permissions(ban_members=True)
async def ban_member(ctx, member: discord.Member, *, raison="Aucune raison fournie"):
    """🔨 Ban un membre du serveur"""
    if member == ctx.author:
        return await ctx.send("❌ Tu ne peux pas te bannir toi-même!")

    if member.top_role >= ctx.author.top_role:
        return await ctx.send("❌ Tu ne peux pas bannir quelqu'un avec un rôle supérieur!")

    if member == ctx.guild.owner:
        return await ctx.send("❌ Tu ne peux pas bannir le propriétaire du serveur!")

    try:
        # MP au membre
        try:
            dm_embed = discord.Embed(
                title="🔨 Bannissement",
                description=f"Tu as été banni de **{ctx.guild.name}**",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            dm_embed.add_field(name="📝 Raison", value=raison, inline=False)
            dm_embed.add_field(name="👮 Par", value=ctx.author.display_name, inline=False)
            await member.send(embed=dm_embed)
        except:
            pass

        await member.ban(reason=f"Par {ctx.author} - {raison}")

        embed = discord.Embed(
            title="✅ Membre banni",
            description=f"**{member.display_name}** a été banni",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="📝 Raison", value=raison, inline=False)
        embed.add_field(name="👮 Par", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions pour bannir ce membre!")
    except Exception as e:
        await ctx.send(f"❌ Erreur: {e}")

# Commande MUTE avec TIMEOUT
@bot.command(name='mute', aliases=['silence'])
@commands.has_permissions(manage_roles=True)
async def mute_member(ctx, member: discord.Member, duration: int = 10, *, raison="Aucune raison fournie"):
    """🔇 Timeout un membre (durée en minutes)"""
    if member == ctx.author:
        return await ctx.send("❌ Tu ne peux pas te mute toi-même!")

    if member.top_role >= ctx.author.top_role:
        return await ctx.send("❌ Tu ne peux pas mute quelqu'un avec un rôle supérieur!")

    try:
        # Utilise le timeout Discord natif
        timeout_duration = timedelta(minutes=duration)
        await member.timeout(timeout_duration, reason=f"Par {ctx.author} - {raison}")

        embed = discord.Embed(
            title="🔇 Membre timeout",
            description=f"**{member.display_name}** a été mis en timeout",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.add_field(name="⏰ Durée", value=f"{duration} minutes", inline=True)
        embed.add_field(name="📝 Raison", value=raison, inline=False)
        embed.add_field(name="👮 Par", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions pour timeout ce membre!")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du timeout: {e}")

# Commande UNMUTE avec TIMEOUT
@bot.command(name='unmute', aliases=['demute'])
@commands.has_permissions(manage_roles=True)
async def unmute_member(ctx, member: discord.Member):
    """🔊 Retire le timeout d'un membre"""
    
    # Vérifie si le membre est timeout
    if member.timed_out_until is None:
        return await ctx.send("❌ Ce membre n'est pas en timeout!")

    try:
        # Retire le timeout (None = pas de timeout)
        await member.timeout(None, reason=f"Démuté par {ctx.author}")

        embed = discord.Embed(
            title="🔊 Membre démuté",
            description=f"**{member.display_name}** a été démuté",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="👮 Par", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Erreur lors du démute: {e}")

# Commande DELETE ALL
@bot.command(name='delall', aliases=['clearall', 'purge'])
@commands.has_permissions(manage_messages=True)
async def delete_all(ctx, limite: int = 100):
    """🗑️ Supprime tous les messages d'un canal"""
    if limite > 1000:
        return await ctx.send("❌ Limite maximale: 1000 messages!")

    if limite < 1:
        return await ctx.send("❌ Le nombre doit être positif!")

    # Confirmation
    embed = discord.Embed(
        title="⚠️ Confirmation requise",
        description=f"Veux-tu vraiment supprimer **{limite}** messages?",
        color=discord.Color.yellow()
    )
    embed.add_field(name="⏰ Temps limite", value="30 secondes", inline=False)

    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

    def check(reaction, user):
        return (user == ctx.author and 
                str(reaction.emoji) in ["✅", "❌"] and 
                reaction.message.id == msg.id)

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)

        if str(reaction.emoji) == "✅":
            await msg.delete()
            deleted = await ctx.channel.purge(limit=limite)

            confirm_embed = discord.Embed(
                title="✅ Messages supprimés",
                description=f"**{len(deleted)}** messages supprimés!",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            temp_msg = await ctx.send(embed=confirm_embed)
            await asyncio.sleep(5)
            await temp_msg.delete()
        else:
            await msg.clear_reactions()
            await msg.edit(content="❌ Suppression annulée.", embed=None)

    except asyncio.TimeoutError:
        await msg.clear_reactions()
        await msg.edit(content="⏰ Temps écoulé. Suppression annulée.", embed=None)

# ===== COMMANDES D'AIDE =====

@bot.command(name='help_mod', aliases=['aide'])
async def help_moderation(ctx):
    """📋 Affiche les commandes de modération"""
    embed = discord.Embed(
        title="🛡️ Commandes de Modération",
        description="Liste des commandes disponibles",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    commands_list = [
        ("🔨 `+ban @membre [raison]`", "Bannit un membre du serveur"),
        ("🔇 `+mute @membre [minutes] [raison]`", "Mute temporairement un membre"),
        ("🔊 `+unmute @membre`", "Démute un membre"),
        ("🗑️ `+delall [nombre]`", "Supprime tous les messages (max 1000)"),
        ("🏓 `+ping`", "Teste la latence du bot"),
        ("⚙️ **Configuration des salons:**", ""),
        ("🏠 `+set_welcome #salon`", "Configure le salon de bienvenue"),
        ("👋 `+set_leave #salon`", "Configure le salon des départs"),
        ("📋 `+channels_config`", "Affiche la configuration actuelle"),
        ("📩 **Messages privés:**", ""),
        ("📤 `+dmall <message>`", "Envoie un MP à tous les membres"),
        ("🎭 `+dmrole @role <message>`", "Envoie un MP aux membres d'un rôle")
    ]

    for cmd, desc in commands_list:
        if desc:  # Skip empty descriptions
            embed.add_field(name=cmd, value=desc, inline=False)
        else:
            embed.add_field(name=cmd, value="\u200b", inline=False)  # Invisible character for spacing

    embed.set_footer(text="Permissions administrateur requises", 
                     icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

# Commande ping
@bot.command(name='ping')
async def ping(ctx):
    """🏓 Affiche la latence du bot"""
    latency = round(bot.latency * 1000)

    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latence: **{latency}ms**",
        color=discord.Color.green() if latency < 100 else discord.Color.orange()
    )

    await ctx.send(embed=embed)

# Gestion des erreurs
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Permissions insuffisantes",
            description="Tu n'as pas les permissions nécessaires!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Membre introuvable!")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Arguments invalides! Utilise `+help_mod`")
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        print(f"Erreur: {error}")

# Lancement du bot
if __name__ == "__main__":
    keep_alive()  # Démarre le serveur web
    bot.run(os.environ['BOT_TOKEN'])
