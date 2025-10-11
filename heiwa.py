import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import os
from keep_alive import keep_alive
from PIL import Image, ImageDraw, ImageFont
import aiohttp
from io import BytesIO
import random

# ===== CONFIGURATION =====
WELCOME_CHANNEL_ID = 1384523345705570487
LEAVE_CHANNEL_ID = 9876543210987654321

# Configuration des intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='+', intents=intents, help_command=None)

# ===== ÉVÉNEMENTS =====

@bot.event
async def on_ready():
    print('=' * 60)
    print(f'🤖 Bot connecté: {bot.user.name}')
    print(f'🆔 ID: {bot.user.id}')
    print(f'📊 Serveurs: {len(bot.guilds)}')
    print(f'👥 Utilisateurs: {len(set(bot.get_all_members()))}')
    print('=' * 60)

    await bot.change_presence(
        activity=discord.Game(name="HK je t'aime 💖"),
        status=discord.Status.dnd
    )

@bot.event
async def on_member_join(member):
    """Message de bienvenue élégant"""
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    
    if not welcome_channel:
        for channel_name in ['bienvenue', 'général', 'welcome', 'general']:
            welcome_channel = discord.utils.get(member.guild.channels, name=channel_name)
            if welcome_channel:
                break
        if not welcome_channel:
            welcome_channel = member.guild.system_channel

    if welcome_channel:
        member_count = len(member.guild.members)
        
        message = f"<a:whitearrow:1426212535262248960> Bienvenue {member.mention} !\n<a:whitearrow:1426212535262248960> Tu es notre **{member_count}ème** membre !"
        
        await welcome_channel.send(message)

    # MP de bienvenue
    try:
        dm_embed = discord.Embed(
            title=f"🎉 Bienvenue sur {member.guild.name} !",
            description=f"Salut **{member.display_name}** ! 👋\n\n"
                       f"Nous sommes ravis de t'accueillir dans notre communauté ! 🔥",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        dm_embed.add_field(
            name="📝 Pour bien commencer",
            value="• Présente-toi dans le salon approprié\n"
                  "• Explore les différents salons\n"
                  "• Respecte les règles et les membres\n"
                  "• Amuse-toi bien !",
            inline=False
        )
        
        dm_embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)
        dm_embed.set_footer(text=f"Équipe {member.guild.name}")
        
        await member.send(embed=dm_embed)
        
    except discord.Forbidden:
        pass

# ===== CONFIGURATION DES SALONS =====

@bot.command(name='set_welcome')
@commands.has_permissions(administrator=True)
async def set_welcome_channel(ctx, channel: discord.TextChannel):
    """Configure le salon de bienvenue"""
    global WELCOME_CHANNEL_ID
    WELCOME_CHANNEL_ID = channel.id
    
    embed = discord.Embed(
        description=f"✅ Les messages de bienvenue seront envoyés dans {channel.mention}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='set_leave')
@commands.has_permissions(administrator=True)  
async def set_leave_channel(ctx, channel: discord.TextChannel):
    """Configure le salon des départs"""
    global LEAVE_CHANNEL_ID
    LEAVE_CHANNEL_ID = channel.id
    
    embed = discord.Embed(
        description=f"✅ Les messages de départ seront envoyés dans {channel.mention}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='config')
@commands.has_permissions(administrator=True)
async def show_config(ctx):
    """Affiche la configuration des salons"""
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    leave_channel = bot.get_channel(LEAVE_CHANNEL_ID)
    
    embed = discord.Embed(
        title="⚙️ Configuration du Bot",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="🏠 Salon de bienvenue", 
        value=welcome_channel.mention if welcome_channel else "❌ Non configuré",
        inline=False
    )
    
    embed.add_field(
        name="👋 Salon des départs",
        value=leave_channel.mention if leave_channel else "❌ Non configuré", 
        inline=False
    )
    
    embed.set_footer(text=f"Demandé par {ctx.author.display_name}")
    await ctx.send(embed=embed)

# ===== MODÉRATION =====

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban_member(ctx, member: discord.Member, *, raison="Aucune raison fournie"):
    """Bannit un membre du serveur"""
    if member == ctx.author:
        return await ctx.send("❌ Tu ne peux pas te bannir toi-même !")

    if member.top_role >= ctx.author.top_role:
        return await ctx.send("❌ Ce membre a un rôle supérieur ou égal au tien !")

    try:
        try:
            dm_embed = discord.Embed(
                title="🔨 Bannissement",
                description=f"Tu as été banni de **{ctx.guild.name}**",
                color=discord.Color.red()
            )
            dm_embed.add_field(name="📝 Raison", value=raison, inline=False)
            dm_embed.add_field(name="👮 Modérateur", value=ctx.author.display_name, inline=False)
            await member.send(embed=dm_embed)
        except:
            pass

        await member.ban(reason=f"Par {ctx.author} - {raison}")

        embed = discord.Embed(
            title="🔨 Membre banni",
            description=f"**{member.display_name}** a été banni du serveur",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="📝 Raison", value=raison, inline=False)
        embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions pour bannir ce membre !")
    except Exception as e:
        await ctx.send(f"❌ Erreur : {e}")

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick_member(ctx, member: discord.Member, *, raison="Aucune raison fournie"):
    """Expulse un membre du serveur"""
    if member == ctx.author:
        return await ctx.send("❌ Tu ne peux pas t'expulser toi-même !")

    if member.top_role >= ctx.author.top_role:
        return await ctx.send("❌ Ce membre a un rôle supérieur ou égal au tien !")

    try:
        try:
            dm_embed = discord.Embed(
                title="👢 Expulsion",
                description=f"Tu as été expulsé de **{ctx.guild.name}**",
                color=discord.Color.orange()
            )
            dm_embed.add_field(name="📝 Raison", value=raison, inline=False)
            dm_embed.add_field(name="👮 Modérateur", value=ctx.author.display_name, inline=False)
            await member.send(embed=dm_embed)
        except:
            pass

        await member.kick(reason=f"Par {ctx.author} - {raison}")

        embed = discord.Embed(
            title="👢 Membre expulsé",
            description=f"**{member.display_name}** a été expulsé du serveur",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.add_field(name="📝 Raison", value=raison, inline=False)
        embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions pour expulser ce membre !")
    except Exception as e:
        await ctx.send(f"❌ Erreur : {e}")

@bot.command(name='mute')
@commands.has_permissions(moderate_members=True)
async def mute_member(ctx, member: discord.Member, duration: int = 10, *, raison="Aucune raison fournie"):
    """Timeout un membre (durée en minutes)"""
    if member == ctx.author:
        return await ctx.send("❌ Tu ne peux pas te mute toi-même !")

    if member.top_role >= ctx.author.top_role:
        return await ctx.send("❌ Ce membre a un rôle supérieur ou égal au tien !")

    if duration > 40320:
        return await ctx.send("❌ Durée maximale : 40320 minutes (28 jours) !")

    try:
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
        embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions pour timeout ce membre !")
    except Exception as e:
        await ctx.send(f"❌ Erreur : {e}")

@bot.command(name='unmute')
@commands.has_permissions(moderate_members=True)
async def unmute_member(ctx, member: discord.Member):
    """Retire le timeout d'un membre"""
    if member.timed_out_until is None:
        return await ctx.send("❌ Ce membre n'est pas en timeout !")

    try:
        await member.timeout(None, reason=f"Démuté par {ctx.author}")

        embed = discord.Embed(
            title="🔊 Membre démuté",
            description=f"**{member.display_name}** peut de nouveau parler",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Erreur : {e}")

@bot.command(name='clear', aliases=['purge', 'clean'])
@commands.has_permissions(manage_messages=True)
async def clear_messages(ctx, amount: int = 10):
    """Supprime un nombre de messages"""
    if amount > 100:
        return await ctx.send("❌ Maximum 100 messages à la fois !")

    if amount < 1:
        return await ctx.send("❌ Le nombre doit être positif !")

    try:
        deleted = await ctx.channel.purge(limit=amount + 1)
        
        embed = discord.Embed(
            description=f"✅ **{len(deleted) - 1}** messages supprimés !",
            color=discord.Color.green()
        )
        
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(3)
        await msg.delete()

    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions pour supprimer des messages !")
    except Exception as e:
        await ctx.send(f"❌ Erreur : {e}")

# ===== MESSAGES PRIVÉS =====

@bot.command(name='dmall')
@commands.has_permissions(administrator=True)
async def dm_all_members(ctx, *, message):
    """Envoie un message privé à tous les membres"""
    
    non_bot_members = [m for m in ctx.guild.members if not m.bot and m != ctx.author]
    
    embed = discord.Embed(
        title="⚠️ Confirmation DM ALL",
        description=f"Envoyer ce message à **{len(non_bot_members)}** membres ?",
        color=discord.Color.yellow()
    )
    embed.add_field(name="📝 Message", value=f"```{message[:300]}{'...' if len(message) > 300 else ''}```", inline=False)
    embed.add_field(name="⏰ Temps", value="30 secondes", inline=True)
    
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
            
        await confirm_msg.delete()
        
        progress_embed = discord.Embed(
            title="📤 Envoi en cours...",
            description="Envoi des messages privés",
            color=discord.Color.blue()
        )
        progress_msg = await ctx.send(embed=progress_embed)
        
        sent_count = 0
        failed_count = 0
        
        dm_embed = discord.Embed(
            title=f"📢 Message de {ctx.guild.name}",
            description=message,
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        dm_embed.set_footer(text=f"Envoyé par {ctx.author.display_name}")
        if ctx.guild.icon:
            dm_embed.set_thumbnail(url=ctx.guild.icon.url)
        
        for member in non_bot_members:
            try:
                await member.send(embed=dm_embed)
                sent_count += 1
                await asyncio.sleep(1.5)
            except:
                failed_count += 1
        
        final_embed = discord.Embed(
            title="📊 Résultats",
            color=discord.Color.green()
        )
        final_embed.add_field(name="✅ Envoyés", value=sent_count, inline=True)
        final_embed.add_field(name="❌ Échecs", value=failed_count, inline=True)
        final_embed.add_field(name="📈 Taux", 
                            value=f"{round((sent_count / len(non_bot_members)) * 100)}%", 
                            inline=True)
        
        await progress_msg.edit(embed=final_embed)
        
    except asyncio.TimeoutError:
        await confirm_msg.edit(content="⏰ Temps écoulé.", embed=None)

@bot.command(name='dmrole')
@commands.has_permissions(administrator=True)
async def dm_role_members(ctx, role: discord.Role, *, message):
    """Envoie un MP aux membres d'un rôle"""
    
    non_bot_members = [m for m in role.members if not m.bot and m != ctx.author]
    
    if not non_bot_members:
        return await ctx.send(f"❌ Aucun membre trouvé avec le rôle **{role.name}** !")
    
    embed = discord.Embed(
        title="⚠️ Confirmation DM ROLE",
        description=f"Envoyer ce message aux **{len(non_bot_members)}** membres du rôle **{role.name}** ?",
        color=role.color if role.color != discord.Color.default() else discord.Color.yellow()
    )
    embed.add_field(name="📝 Message", value=f"```{message[:300]}{'...' if len(message) > 300 else ''}```", inline=False)
    
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
            
        await confirm_msg.delete()
        
        sent_count = 0
        failed_count = 0
        
        dm_embed = discord.Embed(
            title=f"📢 Message pour {role.name}",
            description=message,
            color=role.color if role.color != discord.Color.default() else discord.Color.blue(),
            timestamp=datetime.now()
        )
        dm_embed.set_footer(text=f"Envoyé par {ctx.author.display_name}")
        
        progress_msg = await ctx.send("📤 Envoi en cours...")
        
        for member in non_bot_members:
            try:
                await member.send(embed=dm_embed)
                sent_count += 1
                await asyncio.sleep(1.5)
            except:
                failed_count += 1
        
        result_embed = discord.Embed(
            title=f"📊 Résultats pour {role.name}",
            color=discord.Color.green()
        )
        result_embed.add_field(name="✅ Envoyés", value=sent_count, inline=True)
        result_embed.add_field(name="❌ Échecs", value=failed_count, inline=True)
        
        await progress_msg.edit(content="", embed=result_embed)
        
    except asyncio.TimeoutError:
        await confirm_msg.edit(content="⏰ Temps écoulé.", embed=None)

# ===== UTILITAIRES =====

@bot.command(name='ping')
async def ping(ctx):
    """Affiche la latence du bot"""
    latency = round(bot.latency * 1000)

    embed = discord.Embed(
        title="🏓 Pong !",
        description=f"**Latence :** {latency}ms",
        color=discord.Color.green() if latency < 100 else discord.Color.orange()
    )
    await ctx.send(embed=embed)

@bot.command(name='avatar', aliases=['pdp', 'pp'])
async def show_avatar(ctx, membre: discord.Member = None):
    """Affiche la photo de profil d'un membre"""
    membre = membre or ctx.author
    
    embed = discord.Embed(
        title=f"📸 Avatar de {membre.display_name}",
        color=membre.color if membre.color != discord.Color.default() else discord.Color.blue()
    )
    
    embed.set_image(url=membre.display_avatar.url)
    embed.add_field(
        name="🔗 Liens",
        value=f"[PNG]({membre.display_avatar.with_format('png').url}) • "
              f"[JPG]({membre.display_avatar.with_format('jpg').url}) • "
              f"[WEBP]({membre.display_avatar.with_format('webp').url})",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='banner')
async def show_banner(ctx, membre: discord.Member = None):
    """Affiche la bannière d'un membre"""
    membre = membre or ctx.author
    user = await bot.fetch_user(membre.id)
    
    if user.banner:
        embed = discord.Embed(
            title=f"🎨 Bannière de {membre.display_name}",
            color=membre.color if membre.color != discord.Color.default() else discord.Color.purple()
        )
        
        embed.set_image(url=user.banner.url)
        embed.add_field(
            name="🔗 Liens",
            value=f"[PNG]({user.banner.with_format('png').url}) • "
                  f"[JPG]({user.banner.with_format('jpg').url}) • "
                  f"[WEBP]({user.banner.with_format('webp').url})",
            inline=False
        )
        
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ **{membre.display_name}** n'a pas de bannière !")

@bot.command(name='serverinfo', aliases=['si'])
async def server_info(ctx):
    """Affiche les informations du serveur"""
    guild = ctx.guild
    
    embed = discord.Embed(
        title=f"📊 Informations sur {guild.name}",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.add_field(name="🆔 ID", value=guild.id, inline=True)
    embed.add_field(name="👑 Propriétaire", value=guild.owner.mention, inline=True)
    embed.add_field(name="📅 Créé le", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    
    embed.add_field(name="👥 Membres", value=len(guild.members), inline=True)
    embed.add_field(name="💬 Salons", value=len(guild.channels), inline=True)
    embed.add_field(name="🎭 Rôles", value=len(guild.roles), inline=True)
    
    embed.set_footer(text=f"Demandé par {ctx.author.display_name}")
    
    await ctx.send(embed=embed)

@bot.command(name='userinfo', aliases=['ui'])
async def user_info(ctx, membre: discord.Member = None):
    """Affiche les informations d'un membre"""
    membre = membre or ctx.author
    
    embed = discord.Embed(
        title=f"👤 Informations sur {membre.display_name}",
        color=membre.color if membre.color != discord.Color.default() else discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    embed.set_thumbnail(url=membre.display_avatar.url)
    
    embed.add_field(name="🆔 ID", value=membre.id, inline=True)
    embed.add_field(name="📅 Compte créé", value=membre.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="📅 A rejoint", value=membre.joined_at.strftime("%d/%m/%Y"), inline=True)
    
    roles = [role.mention for role in membre.roles[1:]][:10]
    embed.add_field(
        name=f"🎭 Rôles ({len(membre.roles) - 1})",
        value=" ".join(roles) if roles else "Aucun",
        inline=False
    )
    
    await ctx.send(embed=embed)

# ===== LOVE CALCULATOR =====

@bot.command(name='lc')
async def love_calculator(ctx, *, args: str = None):
    """Calcule le taux d'amour entre toi et quelqu'un"""
    
    if args is None:
        menu_message = "💕 **Love Calculator**\nCalcule le taux d'amour entre deux personnes !\n\n📋 **Commandes disponibles :**\n• `+lc random` - Avec une personne au hasard\n• `+lc @membre` - Avec un membre spécifique"
        return await ctx.send(menu_message)
    
    personne1 = ctx.author
    
    if args.lower() == "random":
        members = [m for m in ctx.guild.members if not m.bot and m != ctx.author]
        if len(members) < 1:
            return await ctx.send("❌ Pas assez de membres !")
        personne2 = random.choice(members)
    else:
        try:
            personne2 = await commands.MemberConverter().convert(ctx, args.strip('<@!> '))
        except:
            return await ctx.send("❌ Membre introuvable ! Utilise `+lc` pour voir les commandes.")
    
    seed = int(str(personne1.id) + str(personne2.id))
    random.seed(seed)
    love_percentage = random.randint(0, 100)
    
    if love_percentage >= 90:
        message = "Amour fou ! 💘"
        emoji = "💘"
    elif love_percentage >= 80:
        message = "Couple parfait ! 💖"
        emoji = "💖"
    elif love_percentage >= 70:
        message = "Très forte attirance ! 💕"
        emoji = "💕"
    elif love_percentage >= 60:
        message = "Belle complicité ! 💗"
        emoji = "💗"
    elif love_percentage >= 50:
        message = "Bonne entente ! 💓"
        emoji = "💓"
    elif love_percentage >= 40:
        message = "Amitié possible ! 💙"
        emoji = "💙"
    elif love_percentage >= 30:
        message = "Relation cordiale ! 🤝"
        emoji = "🤝"
    elif love_percentage >= 20:
        message = "Connaissance ! 👋"
        emoji = "👋"
    elif love_percentage >= 10:
        message = "Pas vraiment de feeling... 😐"
        emoji = "😐"
    else:
        message = "Totalement incompatible ! 💔"
        emoji = "💔"
    
    result_message = f"{personne1.mention} + {personne2.mention} = **{love_percentage}%** of Love {emoji}\n**{personne1.display_name}** + **{personne2.display_name}** ? {message}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(str(personne1.display_avatar.url)) as resp:
                avatar1_data = await resp.read()
            async with session.get(str(personne2.display_avatar.url)) as resp:
                avatar2_data = await resp.read()
        
        avatar1 = Image.open(BytesIO(avatar1_data)).convert("RGBA").resize((200, 200))
        avatar2 = Image.open(BytesIO(avatar2_data)).convert("RGBA").resize((200, 200))
        
        width = 600
        height = 250
        img = Image.new('RGB', (width, height), color=(47, 49, 54))
        
        def make_circle(img):
            mask = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + img.size, fill=255)
            result = Image.new('RGBA', img.size)
            result.paste(img, (0, 0))
            result.putalpha(mask)
            return result
        
        avatar1_circle = make_circle(avatar1)
        avatar2_circle = make_circle(avatar2)
        
        img.paste(avatar1_circle, (50, 25), avatar1_circle)
        img.paste(avatar2_circle, (350, 25), avatar2_circle)
        
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        except:
            font = ImageFont.load_default()
        
        text = f"{love_percentage}%"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        
        draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        file = discord.File(buffer, filename='love.png')
        await ctx.send(result_message, file=file)
        
    except Exception as e:
        print(f"Erreur image: {e}")
        await ctx.send(result_message)

# ===== AIDE =====

@bot.command(name='help', aliases=['aide', 'h'])
async def help_command(ctx):
    """Affiche toutes les commandes"""
    embed = discord.Embed(
