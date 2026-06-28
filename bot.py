import os
import discord
from discord.ext import commands
from discord import app_commands
from collections import defaultdict

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Storage for warns and invites
warns = defaultdict(int)
invite_counts = defaultdict(int)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_member_join(member):
    """Track invites when a member joins"""
    try:
        invites_before = invite_counts.copy()
        invites_after = {}
        for invite in await member.guild.invites():
            invites_after[invite.code] = invite.uses
        
        for code, uses in invites_after.items():
            if code not in invites_before or invites_after[code] > invites_before.get(code, 0):
                inviter = (await member.guild.fetch_invite(code)).inviter
                if inviter:
                    invite_counts[inviter.id] += 1
        
        invite_counts.update(invites_after)
    except:
        pass

@bot.tree.command(name='ping')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('Pong!')

@bot.tree.command(name='warn')
@app_commands.describe(user="User to warn", reason="Reason for warning")
async def warn(interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ You don't have permission to warn users!", ephemeral=True)
        return
    
    warns[user.id] += 1
    embed = discord.Embed(title="⚠️ User Warned", color=discord.Color.orange())
    embed.add_field(name="User", value=user.mention, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Total Warns", value=str(warns[user.id]), inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='warnings')
@app_commands.describe(user="User to check")
async def warnings(interaction: discord.Interaction, user: discord.User):
    count = warns[user.id]
    embed = discord.Embed(title="⚠️ User Warnings", color=discord.Color.orange())
    embed.add_field(name="User", value=user.mention, inline=False)
    embed.add_field(name="Total Warns", value=str(count), inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='kick')
@app_commands.describe(user="User to kick", reason="Reason for kick")
async def kick(interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ You don't have permission to kick users!", ephemeral=True)
        return
    
    try:
        await interaction.guild.kick(user, reason=reason)
        embed = discord.Embed(title="👢 User Kicked", color=discord.Color.red())
        embed.add_field(name="User", value=user.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

@bot.tree.command(name='ban')
@app_commands.describe(user="User to ban", reason="Reason for ban")
async def ban(interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ You don't have permission to ban users!", ephemeral=True)
        return
    
    try:
        await interaction.guild.ban(user, reason=reason)
        embed = discord.Embed(title="🔨 User Banned", color=discord.Color.dark_red())
        embed.add_field(name="User", value=user.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

@bot.tree.command(name='poll')
@app_commands.describe(question="Poll question", option1="First option", option2="Second option", option3="Third option", option4="Fourth option")
async def poll(interaction: discord.Interaction, question: str, option1: str, option2: str, option3: str = None, option4: str = None):
    options = [option1, option2]
    if option3:
        options.append(option3)
    if option4:
        options.append(option4)
    
    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
    
    embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.blue())
    for i, option in enumerate(options):
        embed.add_field(name=f"Option {i+1}", value=f"{emojis[i]} {option}", inline=False)
    
    msg = await interaction.response.send_message(embed=embed)
    for i in range(len(options)):
        await msg.add_reaction(emojis[i])

@bot.tree.command(name='invites')
@app_commands.describe(user="User to check")
async def invites(interaction: discord.Interaction, user: discord.User):
    count = invite_counts[user.id]
    embed = discord.Embed(title="📨 Invite Tracker", color=discord.Color.green())
    embed.add_field(name="User", value=user.mention, inline=False)
    embed.add_field(name="Invites", value=str(count), inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='userinfo')
@app_commands.describe(user="User to check")
async def userinfo(interaction: discord.Interaction, user: discord.User = None):
    user = user or interaction.user
    embed = discord.Embed(title="👤 User Info", color=discord.Color.blue())
    embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
    embed.add_field(name="Username", value=user.name, inline=False)
    embed.add_field(name="ID", value=user.id, inline=False)
    embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d"), inline=False)
    if isinstance(user, discord.Member):
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d"), inline=False)
        embed.add_field(name="Roles", value=", ".join([r.mention for r in user.roles[1:]]) or "None", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='serverinfo')
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title="🏠 Server Info", color=discord.Color.purple())
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="Server Name", value=guild.name, inline=False)
    embed.add_field(name="Members", value=str(guild.member_count), inline=False)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=False)
    embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='clear')
@app_commands.describe(amount="Number of messages to delete (1-100)")
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ You don't have permission to delete messages!", ephemeral=True)
        return
    
    if amount < 1 or amount > 100:
        await interaction.response.send_message("❌ Please specify between 1 and 100 messages!", ephemeral=True)
        return
    
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"✅ Deleted {len(deleted)} messages!", ephemeral=True)

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}!')

bot.run(os.getenv('TOKEN'))
