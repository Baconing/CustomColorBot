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
    print("Ready")
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

@slash.slash(name="sync", description="Syncs your color roles to your current profile picture.")
async def sync(ctx):
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

@slash.slash(name="hex", description="Makes and gives you a role based on a HEX code.", options=[create_option(name="hex", description="The hex code of the color you want to make a role for.", option_type=3, required=True)])
async def hex(ctx, hex):
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

@slash.slash(name="removeroles", description="Removes any color roles you have.")
async def removeroles(ctx):
    for role in ctx.author.roles:
        if role.name.startswith("#"):
            await ctx.author.remove_roles(role)
    em = discord.Embed(title="Roles Removed", description=f"{ctx.author.mention} has had all of their color roles removed.", color=discord.Colour(0x00ff00))
    await ctx.send(embed=em, delete_after=5)

@slash.slash(name="manageroles", description="Manages the color roles on the server.", permissions={config.SERVERID: [create_permission(config.ADMINROLE, SlashCommandPermissionType.ROLE, True)]})
async def manageroles(ctx):
    guild = ctx.guild
    em = discord.Embed(title="Color Roles Manager", description="`Delete Roles` - Deletes all color roles from the server.\n`Delete Role` - Deletes a color role from the server.\n`List Roles` - Lists all of the color roles on the server.", color=discord.Colour(0x00ff00))
    buttons = [
        create_button(
            style=ButtonStyle.blurple,
            label="Delete Roles",
            custom_id="droles"
        ),
        create_button(
            style=ButtonStyle.blurple,
            label="Delete Role",
        ),
        create_button(
            style=ButtonStyle.blurple,
            label="List Roles",
            custom_id="lroles"
        )
    ]
    row = create_actionrow(buttons)
    await ctx.send(embed=em, componets=[row])

@slash.component_callback()
async def droles(ctx: ComponentContext):
    guild = ctx.guild
    for role in guild.roles:
        if role.name.startswith("#"):
            await role.delete()
    em = discord.Embed(title="Roles Deleted", description=f"All color roles have been deleted.", color=discord.Colour(0x00ff00))
    await ctx.send(embed=em, delete_after=5)

@slash.component_callback()
async def drole(ctx: ComponentContext):
    em = discord.Embed(title="Delete Role", description="Please enter the hex code of the color role you want to delete.", color=discord.Colour(0x00ff00))
    await ctx.send(embed=em)
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await ctx.bot.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        em = discord.Embed(title="Delete Role", description="You took too long to respond.", color=discord.Colour(0xff0000))
        await ctx.send(embed=em, delete_after=5)
        return
    hexCode = msg.content.replace("#", "")
    for role in ctx.guild.roles:
        if role.name.startswith("#") and role.name == f"#{hexCode}":
            await role.delete()
    em = discord.Embed(title="Role Deleted", description=f"The role #{hexCode} has been deleted.", color=discord.Colour(0x00ff00))
    await ctx.send(embed=em, delete_after=5)

@slash.component_callback()
async def lroles(ctx: ComponentContext):
    guild = ctx.guild
    roles = []
    for role in guild.roles:
        if role.name.startswith("#"):
            roles.append(role.name)
    em = discord.Embed(title="Color Roles", description="\n".join(roles), color=discord.Colour(0x00ff00))
    try:
        await ctx.send(embed=em, delete_after=5)
    except discord.HTTPException:
        em = discord.Embed(title="Color Roles", description=f"There are too many roles to put into a message. You have {len(roles)} color roles.", color=discord.Colour(0x00ff00))
        await ctx.send(embed=em, delete_after=5)

@bot.event
async def on_slash_command_error(ctx, ex):
    em = discord.Embed(title="An error has occurred.", colour=0xaa0000)
    em.add_field(name="Traceback", value=ex)
    em.add_field(name="Support", value=f"wip")
    await ctx.send(embed=em, delete_after=10)


bot.run(config.TOKEN)