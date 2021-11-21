import os
import discord
from discord import colour
import discord_slash
import config
import datetime
import time
import requests
import shutil
from datetime import timezone, tzinfo
from discord import Intents
from discord.ext import commands
from discord_slash import *
from discord_slash.utils.manage_commands import *
from discord_slash.utils.manage_components import *
from discord_slash.model import *
from discord_slash.context import *
from colorthief import ColorThief
import os

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="*", intents=intents)
slash = SlashCommand(bot, override_type=True, sync_commands=True, sync_on_cog_reload=True, debug_guild=config.SERVERID, application_id=config.APPLICATIONID)

# cogTypes = ["commands", "handlers", "listeners"]

# for cogType in cogTypes:
#     for filename in os.listdir(f'./cogs/{cogType}'):
#         if filename.endswith('.py'):
#             bot.load_extension(f'cogs.{cogType}.{filename[:-3]}')


def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

@bot.event
async def on_ready():
    print("Bot is ready!")
    print(f"Logged in as {bot.user.name}")
    print(f"ID: {bot.user.id}")
    print(f"Discord.py version: {discord.__version__}")
    print(f"Discord.py version: {discord.version_info}")
    print(f"Discord.py version: {discord.version_info.major}")
    print(f"Discord.py version: {discord.version_info.minor}")
    print(f"Discord.py version: {discord.version_info.micro}")
    print(f"Discord.py version: {discord.version_info.releaselevel}")
    print(f"Discord.py version: {discord.version_info.serial}")
    
    await bot.change_presence(activity=discord.Game(name="with colors!!!!!"))

    bot.remove_command('help')

@bot.event
async def on_member_join(member):
    guild = member.guild
    pfpUrl = member.avatar_url
    fileName = pfpUrl.split("/")[-1]
    fileName = fileName.split("?")[0]
    r = requests.get(pfpUrl, stream=True)
    if r.status_code == 200:
        with open(fileName, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
        colorThief = ColorThief(f'{fileName}')
        dominantColor = colorThief.get_color(quality=1)
        dominantColor = rgb2hex(dominantColor[0], dominantColor[1], dominantColor[2])
        os.remove(f'{fileName}')
        if discord.utils.get(guild.roles, name=f"#{dominantColor}"):
            await member.add_roles(discord.utils.get(guild.roles, name=f"#{dominantColor}"))
        else:
            await guild.create_role(name=f"#{dominantColor}", colour=discord.Colour(int(dominantColor, base=16)))
            await member.add_roles(discord.utils.get(guild.roles, name=f"#{dominantColor}"))

# Roles Commands

@slash.subcommand(base="roles", name="sync", description="Syncs your color roles to your current profile picture.")
async def roles_sync(ctx):
    guild = ctx.guild
    pfpUrl = str(ctx.author.avatar_url)
    fileName = pfpUrl.split("/")[-1]
    fileName = fileName.split("?")[0]
    r = requests.get(pfpUrl, stream=True)
    if r.status_code == 200:
        with open(fileName, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
        color_thief = ColorThief(f'{fileName}')
        dominant_color = color_thief.get_color(quality=1)
        dominant_color = rgb2hex(dominant_color[0], dominant_color[1], dominant_color[2])
        dominant_color = dominant_color.replace("#", "")
        os.remove(fileName)
        if discord.utils.get(guild.roles, name=f"#{dominant_color}"):
            for role in ctx.author.roles:
                if role.name.startswith("#") and role.name != f"#{dominant_color}":
                    await ctx.author.remove_roles(role)
            await ctx.author.add_roles(discord.utils.get(guild.roles, name=f"#{dominant_color}"))
            em = discord.Embed(title="Role Added", description=f"{ctx.author.mention} has been given the role #{dominant_color}.", color=discord.Colour(int(dominant_color, base=16)))
            await ctx.send(embed=em, delete_after=5)
        else:
            for role in ctx.author.roles:
                if role.name.startswith("#") and role.name != f"#{dominant_color}":
                    await ctx.author.remove_roles(role)
            await guild.create_role(name=f"#{dominant_color}", colour=discord.Colour(int(dominant_color, base=16)))
            await ctx.author.add_roles(discord.utils.get(guild.roles, name=f"#{dominant_color}"))
            em = discord.Embed(title="Role Created & Added", description=f"{ctx.author.mention} has been given the role #{dominant_color}.", color=discord.Colour(int(dominant_color, base=16)))
            await ctx.send(embed=em, delete_after=5)
    else:
        raise discord_slash.exceptions.SlashError(f"{ctx.author.name}'s profile picture is not available.")

@slash.subcommand(base="roles", name="hex", description="Makes and gives you a role based on a HEX code.", options=[create_option(name="hex", description="The hex code of the color you want to make a role for.", option_type=3, required=True)])
async def roles_hex(ctx, hex):
    guild = ctx.guild
    hexCode = hex.replace("#", "")
    if discord.utils.get(guild.roles, name=f"#{hexCode}"):
        for role in ctx.author.roles:
            if role.name.startswith("#") and role.name != f"#{hexCode}":
                await ctx.author.remove_roles(role)
        await ctx.author.add_roles(discord.utils.get(guild.roles, name=f"#{hexCode}"))
        em = discord.Embed(title="Role Added", description=f"{ctx.author.mention} has been given the role #{hexCode}.", color=discord.Colour(int(hexCode, base=16)))
        await ctx.send(embed=em, delete_after=5)
    else:
        for role in ctx.author.roles:
            if role.name.startswith("#") and role.name != f"#{hexCode}":
                await ctx.author.remove_roles(role)
        await guild.create_role(name=f"#{hexCode}", colour=discord.Colour(int(hexCode, base=16)))
        await ctx.author.add_roles(discord.utils.get(guild.roles, name=f"#{hexCode}"))
        em = discord.Embed(title="Role Created & Added", description=f"{ctx.author.mention} has been given the role #{hexCode}.", color=discord.Colour(int(hexCode, base=16)))
        await ctx.send(embed=em, delete_after=5)

@slash.subcommand(base="roles", name="remove", description="Removes any color roles you have.")
async def roles_remove(ctx):
    for role in ctx.author.roles:
        if role.name.startswith("#"):
            await ctx.author.remove_roles(role)
    em = discord.Embed(title="Roles Removed", description=f"{ctx.author.mention} has had all of their color roles removed.", color=discord.Colour(0x00ff00))
    await ctx.send(embed=em, delete_after=5)




# Management Commands



@slash.subcommand(base="manage", name="help", description="Shows the help menu for the manage commands.")
async def manage_help(ctx):
    if discord.utils.get(ctx.guild.roles, id=config.ADMINROLE) in ctx.author.roles:
        em = discord.Embed(title="Help Menu", description="The following commands are available for the manage command.", color=discord.Colour(0x00ff00))
        em.add_field(name="help", value="Shows the help menu for the manage command.", inline=False)
        em.add_field(name="deleteall", value="Deletes all color roles from the server.", inline=False)
        em.add_field(name="delete", value="Deletes a color role from the server.", inline=False)
        em.add_field(name="list", value="Lists all of the color roles in the server.", inline=False)
        await ctx.send(embed=em, delete_after=5)
    else:
        em = discord.Embed(title="No Permission", description="You do not have permission to use this command.", color=discord.Colour(0xff0000))
        await ctx.send(embed=em, delete_after=5)

@slash.subcommand(base="manage", name="deleteall", description="Deletes all color roles from the server.")
async def manage_deleteall(ctx):
    if discord.utils.get(ctx.guild.roles, id=config.ADMINROLE) in ctx.author.roles:
        if len(ctx.guild.roles) > 1:
            for role in ctx.guild.roles:
                if role.name.startswith("#"):
                    await role.delete()
            em = discord.Embed(title="Roles Deleted", description=f"All of the color roles have been deleted from the server.", color=discord.Colour(0x00ff00))
            await ctx.send(embed=em)
        else:
            em = discord.Embed(title="No Roles", description=f"There are no color roles on the server.", color=discord.Colour(0x00ff00))
            await ctx.send(embed=em)
    else:
        em = discord.Embed(title="No Permission", description="You do not have permission to use this command.", color=discord.Colour(0xff0000))
        await ctx.send(embed=em)

@slash.subcommand(base="manage", name="delete", description="Deletes a color role from the server.", options=[create_option(name="hex", description="The hex code of the color role you want to delete.", option_type=3, required=True)])
async def manage_delete(ctx, hex):
    if discord.utils.get(ctx.guild.roles, id=config.ADMINROLE) in ctx.author.roles:
        guild = ctx.guild
        hexCode = hex.replace("#", "")
        if discord.utils.get(guild.roles, name=f"#{hexCode}"):
            await discord.utils.get(guild.roles, name=f"#{hexCode}").delete()
            em = discord.Embed(title="Role Deleted", description=f"The role #{hexCode} has been deleted.", color=discord.Colour(0x00ff00))
            await ctx.send(embed=em)
        else:
            em = discord.Embed(title="No Role", description=f"There is no role with the hex code #{hexCode}. Did you type it right?", color=discord.Colour(0xff0000))
            await ctx.send(embed=em)
    else:
        em = discord.Embed(title="No Permission", description="You do not have permission to use this command.", color=discord.Colour(0xff0000))
        await ctx.send(embed=em)

@slash.subcommand(base="manage", name="listroles", description="Lists all of the color roles on the server.")
async def manage_listroles(ctx):
    if discord.utils.get(ctx.guild.roles, id=config.ADMINROLE) in ctx.author.roles:
        guild = ctx.guild
        roles = []
        for role in guild.roles:
            if role.name.startswith("#"):
                roles.append(role)
        if len(roles) == 0:
            em = discord.Embed(title="No Roles", description="There are no color roles on this server.", color=discord.Colour(0x00ff00))
            await ctx.send(embed=em, delete_after=5)
        else:
            try:
                em = discord.Embed(title="Color Roles", description="Here are all of the color roles on this server.", color=discord.Colour(0x00ff00))
                for role in roles:
                    em.add_field(name=role.name, value=f"{role.mention}")
                await ctx.send(embed=em, delete_after=5)
            except discord.errors.HTTPException:
                em = discord.Embed(title="Too Many Roles", description=f"There are too many color roles on this server to list them all. You have {len(roles)} color roles.", color=discord.Colour(0x00ff00))
                await ctx.send(embed=em, delete_after=5)
    else:
        em = discord.Embed(title="No Permission", description="You do not have permission to use this command.", color=discord.Colour(0xff0000))
        await ctx.send(embed=em, delete_after=5)

@bot.event
async def on_slash_command_error(ctx, ex):
    em = discord.Embed(title="An error has occurred.", colour=0xaa0000)
    em.add_field(name="Traceback", value=ex)
    em.add_field(name="Support", value=f"wip")
    await ctx.send(embed=em, delete_after=10)
    print(f"\n\n\n\n\nError!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nLMFAO U SUCK AT CODING!!!!!!!!!!!!!!!!!!!!!!!\n\nDEBUG: {ctx.guild.name} - {ctx.channel} - {ctx.author}\n\nDEBUG: {ex}")

bot.run(config.TOKEN)