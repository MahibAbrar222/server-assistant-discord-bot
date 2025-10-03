"""Discord Server Assistant Bot

This bot helps manage Discord servers with features like welcome messages,
admin management, and moderation commands.

Author: Mahib Abrar
Email: mahibabrar123@gmail.com
License: MIT (Name Required for Credits)
"""

import os

from dotenv import load_dotenv
import discord
from discord.ext import commands

from guilds import Guilds
from utils import generate_welcome_image, generate_temp_file_name

# Load environment variables and setup
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

DISCORD_SERVERS = Guilds()

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
tree = bot.tree


# Event Handlers

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


@bot.event
async def on_member_join(member: discord.Member):
    """Generate and send a welcome image when a new member joins."""
    server = DISCORD_SERVERS.get_server(member.guild.id)

    if server["welcome_channel"]:
        channel = bot.get_channel(server["welcome_channel"])
    else:
        channel = bot.get_channel(server["system_channel_id"])
    
    if channel:
        avatar = member.avatar if member.avatar else member.default_avatar
        img = generate_welcome_image(member.name, member.guild.name, avatar)
        temp_file = generate_temp_file_name() + '.png'
        img.save(temp_file)
        await channel.send(file=discord.File(temp_file))
        os.remove(temp_file)


# Bot Commands
@bot.command(name="sync")
async def sync(ctx):
    """Sync bot commands with Discord."""
    DISCORD_SERVERS.refresh_servers()
    await tree.sync()
    await ctx.send("Synced!")


# Slash Commands - Server Configuration
@tree.command(name="set-welcome-channel")
async def set_welcome_channel(ctx: discord.Interaction, channel: discord.TextChannel):
    """Set the channel where welcome messages will be sent."""
    if str(ctx.user.id) not in DISCORD_SERVERS.get_admins(ctx.guild.id):
        await ctx.response.send_message("You need to be an admin to use this command", ephemeral=True)
        return
    
    DISCORD_SERVERS.set_welcome_channel(ctx.guild.id, channel.id)
    await ctx.response.send_message(f"Successfully set the welcome channel {channel.mention}", ephemeral=True)


# Slash Commands - Admin Management
@tree.command(name="add-admin")
async def add_admin(ctx: discord.Interaction, user: discord.User):
    """Add a user as a bot admin for this server."""
    if str(ctx.user.id) not in DISCORD_SERVERS.get_admins(ctx.guild.id):
        await ctx.response.send_message("You need to be an admin to use this command", ephemeral=True)
        return
    
    DISCORD_SERVERS.add_admin(ctx.guild.id, user.id)
    await ctx.response.send_message(f"Successfully added {user.mention} as an admin", ephemeral=True)


@tree.command(name="remove-admin")
async def remove_admin(ctx: discord.Interaction, user: discord.User):
    """Remove a user from bot admins for this server."""
    if str(ctx.user.id) not in DISCORD_SERVERS.get_admins(ctx.guild.id):
        await ctx.response.send_message("You need to be an admin to use this command", ephemeral=True)
        return
    
    DISCORD_SERVERS.remove_admin(ctx.guild.id, str(user.id))
    await ctx.response.send_message(f"Successfully removed {user.mention} as an admin", ephemeral=True)


@tree.command(name="get-admins")
async def get_admins(ctx: discord.Interaction):
    """List all bot admins for this server."""
    admins = DISCORD_SERVERS.get_admins(ctx.guild.id)
    if len(admins) == 0:
        await ctx.response.send_message("No admins found", ephemeral=True)
        return
    
    admin_mentions = [bot.get_user(int(admin)).mention for admin in admins]
    await ctx.response.send_message(f"Admins: {', '.join(admin_mentions)}", ephemeral=True)

# Slash Commands - Role Management
@tree.command(name="add-user-to-role")
async def add_user_to_role(ctx: discord.Interaction, role: discord.Role, user: discord.User):
    """Add a role to a user."""
    await user.add_roles(role)
    await ctx.response.send_message("Role added", ephemeral=True)


@tree.command(name="remove-user-from-role")
async def remove_user_from_role(ctx: discord.Interaction, role: discord.Role, user: discord.User):
    """Remove a role from a user."""
    await user.remove_roles(role)
    await ctx.response.send_message("Role removed", ephemeral=True)


# Slash Commands - Message Actions
@tree.command(name="delete-message")
async def delete_message(ctx: discord.Interaction, message_id: str):
    """Delete a message by its ID."""
    message = await ctx.channel.fetch_message(int(message_id))
    await message.delete()
    await ctx.response.send_message("Message deleted", ephemeral=True)


# Slash Commands - Embed
@tree.command(name="embed")
async def embed(ctx: discord.Interaction, title: str, description: str, color: str = "green", footer: str = None, image: str = None):
    """Create and send a custom embed message."""
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


# Slash Commands - Moderation
@tree.command(name="ban")
async def ban_user(ctx: discord.Interaction, user: discord.User, reason: str):
    """Ban a user from the server."""
    if str(ctx.user.id) not in DISCORD_SERVERS.get_admins(ctx.guild.id):
        await ctx.response.send_message("You need to be an admin to use this command", ephemeral=True)
        return
    
    await ctx.guild.ban(user, reason=reason)
    await ctx.response.send_message(f"Banned {user.mention} for: {reason}", ephemeral=True)


@tree.command(name="unban")
async def unban_user(ctx: discord.Interaction, user: discord.User):
    """Unban a user from the server."""
    if str(ctx.user.id) not in DISCORD_SERVERS.get_admins(ctx.guild.id):
        await ctx.response.send_message("You need to be an admin to use this command", ephemeral=True)
        return
    
    await ctx.guild.unban(user)
    await ctx.response.send_message(f"Unbanned {user.mention}", ephemeral=True)


# Slash Commands - Bot Information
@tree.command(name="copyright")
async def copyright_info(ctx: discord.Interaction):
    """Display copyright information."""
    embed = discord.Embed(
        title="Bot by @Mahib Abrar",
        description="This bot is made by Mahib Abrar and is open source. You can find the source code on [GitHub]()]",
        color=discord.Color.green()
    )
    await ctx.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="about")
async def about_bot(ctx: discord.Interaction):
    """Display information about the bot."""
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


# Slash Commands - Voice (Not Implemented)
@tree.command(name="play-sound")
async def play_sound(ctx: discord.Interaction, sound_url: str, channel: discord.VoiceChannel):
    """Play a sound in a voice channel (not yet implemented)."""
    await ctx.response.send_message("This feature is not yet implemented", ephemeral=True)


@tree.command(name="help")
async def help_command(ctx: discord.Interaction):
    """Display help information (not yet implemented)."""
    await ctx.response.send_message("This feature is not yet implemented", ephemeral=True)


# Run the bot
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
