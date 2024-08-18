# Copyright & Credits
# This bot is made by Mahib Abrar. You can use this bot for free. You can also modify the code and use it for free. (Name Required for Credits) 
# Author: Mahib Abrar
# Email: mahibabrar123@gmail.com
# GitHub:


import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from guilds import Guilds
from utils import *

# DISCORD TOKEN & SETUP
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

DISCORD_SERVERS = Guilds()

# BOT
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
tree = bot.tree

# Events
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    guilds = bot.guilds

    for guild in guilds:
        if not DISCORD_SERVERS.ifServerExists(guild.id):
            DISCORD_SERVERS.saveServers(guild.id, guild.name, guild.system_channel.id, guild.owner.id)

@bot.event
async def on_guild_join(guild):
    DISCORD_SERVERS.saveServers(guild.id, guild.name)
    
    # Send Thank You message
    channel = guild.system_channel
    if channel:
        # Beautiful Embeds
        embed = discord.Embed(
            title="Thank you for inviting me!",
            description="I am a bot that can help you with your server!",
            color=discord.Color.green()
        )
        await channel.send(embed=embed)
@bot.event
async def on_guild_remove(guild):
    DISCORD_SERVERS.removeServer(guild.id)
    print(f"Removed {guild.name} from servers.json")

    # Send server owner a message to send feedback and sorry
    owner = guild.owner
    await owner.send(f"Sorry to see you go! If you have any feedback, please let me know!")

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)


# On User Joined
@bot.event
async def on_member_join(member: discord.Member):
    # Genarate a image with welcome message
    # Send the image to the channel
    server = DISCORD_SERVERS.getServer(member.guild.id)

    if server["welcome_channel"]:
        channel = bot.get_channel(server["welcome_channel"])
    else:
        channel = bot.get_channel(server["system_channel_id"])
    if channel:
        # Genarate a image with welcome message
        # Send the image to the channel
        avatar = member.avatar
        if avatar is None:
            avatar = member.default_avatar
        img = generate_welcome_image(member.name, member.guild.name, avatar)
        temp_file = genarate_temp_file_name() + '.png'
        img.save(temp_file)
        await channel.send(file=discord.File(temp_file))
        os.remove(temp_file)

# Bot Commands
@bot.command(name="sync")
async def sync(ctx):
    DISCORD_SERVERS.refeshServers()
    await tree.sync()
    await ctx.send("Synced!")

# Bot tree commands
@tree.command(name="set-welcome-channel")
async def set_welcome_channel(ctx: discord.Interaction, channel: discord.TextChannel):
    # Check if admin
    if str(ctx.user.id) not in DISCORD_SERVERS.getAdmins(ctx.guild.id):
        await ctx.response.send_message("You need to be an admin to use this command", ephemeral=True)
        return
    DISCORD_SERVERS.setWelcomeChannel(ctx.guild.id, channel.id)
    await ctx.response.send_message("Successfully set the welcome channel " + channel.mention, ephemeral=True)

# Admin
@tree.command(name="add-admin")
async def add_admin(ctx: discord.Interaction, user: discord.User):
    # Check if admin
    if str(ctx.user.id) not in DISCORD_SERVERS.getAdmins(ctx.guild.id):
        await ctx.response.send_message("You need to be an admin to use this command", ephemeral=True)
        return
    DISCORD_SERVERS.addAdmin(ctx.guild.id, user.id)
    await ctx.response.send_message("Successfully added " + user.mention + " as an admin", ephemeral=True)
@tree.command(name="remove-admin")
async def remove_admin(ctx: discord.Interaction, user: discord.User):
    # Check if admin
    if str(ctx.user.id) not in DISCORD_SERVERS.getAdmins(ctx.guild.id):
        await ctx.response.send_message("You need to be an admin to use this command", ephemeral=True)
        return
    DISCORD_SERVERS.removeAdmin(ctx.guild.id, str(user.id))
    await ctx.response.send_message("Successfully removed " + user.mention + " as an admin", ephemeral=True)

@tree.command(name="get-admins")
async def get_admins(ctx: discord.Interaction):
    admins = DISCORD_SERVERS.getAdmins(ctx.guild.id)
    if len(admins) == 0:
        await ctx.response.send_message("No admins found", ephemeral=True)
        return
    admins = [bot.get_user(int(admin)).mention for admin in admins]
    await ctx.response.send_message("Admins: " + ', '.join(admins), ephemeral=True)

# Role Management
@tree.command(name="add-user-to-role")
async def add_user_to_role(ctx: discord.Interaction, role: discord.Role, user: discord.User):
    await user.add_roles(role)
    await ctx.response.send_message("Role added", ephemeral=True)

@tree.command(name="remove-user-from-role")
async def remove_user_from_role(ctx: discord.Interaction, role: discord.Role, user: discord.User):
    await user.remove_roles(role)
    await ctx.response.send_message("Role removed", ephemeral=True)

# Message Actions
@tree.command(name="delete-message")
async def delete_message(ctx: discord.Interaction, message_id: str):
    message = await ctx.channel.fetch_message(int(message_id))
    await message.delete()
    await ctx.response.send_message("Message deleted", ephemeral=True)

# Embed
@tree.command(name="embed")
async def embed(ctx: discord.Interaction, title: str, description: str, color: str = "green", footer: str = None, image: str = None):
    COLORS = ["red", "green", "blue", "yellow", "purple", "orange", "pink", "brown"]
    if color not in COLORS:
        await ctx.response.send_message("Invalid color", ephemeral=True)
        return
    embed_ = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.green()
    )

    embed_.set_author(name=ctx.user.name, icon_url=ctx.user.avatar or ctx.user.default_avatar)

    await ctx.response.send_message(embed=embed_)

# Ban & unban
@tree.command(name="ban")
async def schedule_ban(ctx: discord.Interaction, user: discord.User, reason: str):
    # Check if admin
    if str(ctx.user.id) not in DISCORD_SERVERS.getAdmins(ctx.guild.id):
        await ctx.response.send_message("You need to be an admin to use this command", ephemeral=True)
        return
    await ctx.guild.ban(user, reason=reason)

    await ctx.response.send_message(f"Scheduled ban for {user.mention} for {reason}", ephemeral=True)

@tree.command(name="unban")
async def unban(ctx: discord.Interaction, user: discord.User):
    # Check if admin
    if str(ctx.user.id) not in DISCORD_SERVERS.getAdmins(ctx.guild.id):
        await ctx.response.send_message("You need to be an admin to use this command", ephemeral=True)
        return
    await ctx.guild.unban(user)

    await ctx.response.send_message(f"Scheduled unban for {user.mention} for {reason} at {time}", ephemeral=True)

# Copyright Information
@tree.command(name="copyright")
async def copyright(ctx: discord.Interaction):
    embed = discord.Embed(
        title="Bot by @Mahib Abrar",
        description="This bot is made by Mahib Abrar and is open source. You can find the source code on [GitHub]()]",
        color=discord.Color.green()
    )
    await ctx.response.send_message(embed=embed, ephemeral=True)
@tree.command(name="about")
async def about(ctx: discord.Interaction):
    embed = discord.Embed(
        title="Bot by @Mahib Abrar",
        description="This bot is made by Mahib Abrar and is open source. You can find the source code on [GitHub]()]",
        color=discord.Color.green()
    )
    embed.add_field(name="Version", value="1.0.0", inline=False)
    embed.add_field(name="Language", value="Python", inline=False)
    embed.add_field(name="Library", value="Discord.py", inline=False)
    embed.add_field(name="License", value="MIT", inline=False)
    embed.add_field(name="Creator", value="Mahib Abrar", inline=False)
    embed.add_field(name="GitHub", value="[GitHub]()", inline=False)

    await ctx.response.send_message(embed=embed)
# Voice
@tree.command(name="play-sound")
async def playSound(ctx: discord.Interaction, sound_url: str, channel: discord.VoiceChannel):
    pass
# Help
@tree.command(name="help")
async def help(ctx: discord.Interaction):
    pass
# Run the bot
bot.run(DISCORD_TOKEN)

