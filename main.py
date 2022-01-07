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
from discord_slash.error import *
from colorthief import ColorThief
import os
from dotenv import load_dotenv
import pymongo

load_dotenv()
TOKEN = os.getenv('TOKEN')
APPID = os.getenv('APPID')
TYPE = os.getenv('TYPE')

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="*", intents=intents)
if TYPE == "BETA":
    slash = SlashCommand(bot, override_type=True, sync_commands=True, sync_on_cog_reload=True, application_id=APPID, debug_guild=config.DEBUGSERVER)
else:
    slash = SlashCommand(bot, override_type=True, sync_commands=True, sync_on_cog_reload=True, application_id=APPID)

# cogTypes = ["commands", "handlers", "listeners"]

# for cogType in cogTypes:
#     for filename in os.listdir(f'./cogs/{cogType}'):
#         if filename.endswith('.py'):
#             bot.load_extension(f'cogs.{cogType}.{filename[:-3]}')

database = pymongo.MongoClient(config.CONNURL, serverSelectionTimeoutMS=5000)

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

@bot.event
async def on_ready():
    print("Bot is ready!")
    print(f"\n\nLogged in as {bot.user.name}")
    print(f"ID: {bot.user.id}")
    print(f"\n\nDiscord.py version: {discord.__version__}")

    await bot.change_presence(activity=discord.Game(name="with colors!!!!!"))

    bot.remove_command('help')

    print("\n\nServers:")
    for server in bot.guilds:
        print(f"{server.name}")

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
            db = database.servers
            collection = db.configs
            position = collection.find_one({"guild_id": guild.id})["position"]
            if position < len(guild.roles):
                try:
                    role = await guild.create_role(name=f"#{dominantColor}", colour=discord.Colour(int(dominantColor, base=16)))
                    await role.edit(position=position)
                except discord.errors.Forbidden:
                    error = discord.Embed(title="Error", description="I don't have permission to move this role to the set position.", color=discord.Colour.red())
                    await guild.owner.send(embed=error)
            else:
                error = discord.Embed(title="Invalid Position", description=f"The position your server ({guild.name}) has set is invalid. Please enter a number between 0 and the number of roles in your server and reset with /config position. Defaulting to 0", color=discord.Colour(0xff0000))
                await guild.owner.send(embed=error)
            await member.add_roles(discord.utils.get(guild.roles, name=f"#{dominantColor}"))

@bot.event
async def on_guild_join(guild):
    print(f"Joined {guild.name}")
    for channel in guild.channels:
        if channel.name == "general":
            if channel.permissions_for(guild.me).send_messages:
                em = discord.Embed(title="Thanks for adding me!", description="Make sure to move me to the top of the role list in order for everything to work correctly! Also, do /config position to set the position of where roles will go.", colour=discord.Colour(0x00ff00))
                em.set_thumbnail(url=f"{bot.user.avatar_url}")
                await channel.send(embed=em)
            else:
                noPerms = discord.Embed(title="I do not have permission to send messages!", description="Please make sure I have the permission to send messages in all channels.", colour=discord.Colour(0xff0000))
                em = discord.Embed(title="Thanks for adding me!", description="Make sure to move me to the top of the role list in order for everything to work correctly! Also, do /config position to set the position of where roles will go.", colour=discord.Colour(0x00ff00))
                em.set_thumbnail(url=f"{bot.user.avatar_url}")
                await guild.server.owner.send(embed=noPerms)
                await guild.server.owner.send(embed=em)
    db = database.servers
    post = {
        "guild_id": guild.id,
        "position": 0
    }

    collection = db.configs
    posts = db.configs
    if posts.findone({"guild_id": guild.id}):
        pass
    else:
        posts.insert_one(post)

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
        color_thief.get_color(quality=1)
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
            db = database.servers
            collection = db.configs
            position = collection.find_one({"guild_id": guild.id})["position"]
            if position < len(guild.roles):
                role = await guild.create_role(name=f"#{dominant_color}", colour=discord.Colour(int(dominant_color, base=16)))
                await role.edit(position=position)
            else:
                error = discord.Embed(title="Invalid Position", description="The position your server has set is invalid. Please enter a number between 0 and the number of roles in your server and reset with /config position. Defaulting to 0", color=discord.Colour(0xff0000))
                await ctx.send(embed=error, delete_after=5)
            await ctx.author.add_roles(role)
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
        db = database.servers
        collection = db.configs
        position = collection.find_one({"guild_id": guild.id})["position"]
        if position < len(guild.roles):
            role = await guild.create_role(name=f"#{hexCode}", colour=discord.Colour(int(hexCode, base=16)))
            await role.edit(position=position)
        else:
            error = discord.Embed(title="Invalid Position", description="The position your server has set is invalid. Please enter a number between 0 and the number of roles in your server and reset with /config position. Defaulting to 0", color=discord.Colour(0xff0000))
            await ctx.send(embed=error, delete_after=5)
        await ctx.author.add_roles(role)
        em = discord.Embed(title="Role Created & Added", description=f"{ctx.author.mention} has been given the role #{hexCode}.", color=discord.Colour(int(hexCode, base=16)))
        await ctx.send(embed=em, delete_after=5)

@slash.subcommand(base="roles", name="remove", description="Removes any color roles you have.")
async def roles_remove(ctx):
    for role in ctx.author.roles:
        if role.name.startswith("#"):
            await ctx.author.remove_roles(role)
    em = discord.Embed(title="Roles Removed", description=f"{ctx.author.mention} has had all of their color roles removed.", color=discord.Colour(0x00ff00))
    await ctx.send(embed=em, delete_after=5)

@slash.subcommand(base="roles", name="syncall", description="Runs /roles sync on all users in the server.")
async def roles_syncall(ctx):
    finishedUsers = 0
    waitingMsg = await ctx.send(f"<:buffering:928709341568180254> Syncing...\nThis may take a while.\n{finishedUsers}/{len(ctx.guild.members)}")
    guild = ctx.guild
    errors = []
    for member in guild.members:
        try:
            pfpUrl = str(member.avatar_url)
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
                    for role in member.roles:
                        if role.name.startswith("#") and role.name != f"#{dominant_color}":
                            await member.remove_roles(role)
                    await member.add_roles(discord.utils.get(guild.roles, name=f"#{dominant_color}"))
                else:
                    for role in member.roles:
                        if role.name.startswith("#") and role.name != f"#{dominant_color}":
                            await member.remove_roles(role)
                    db = database.servers
                    collection = db.configs
                    position = collection.find_one({"guild_id": guild.id})["position"]
                    if position < len(guild.roles):
                        role = await guild.create_role(name=f"#{dominant_color}", colour=discord.Colour(int(dominant_color, base=16)))
                        await role.edit(position=position)
                    else:
                        error = discord.Embed(title="Invalid Position", description="The position your server has set is invalid. Please enter a number between 0 and the number of roles in your server and reset with /config position. Defaulting to 0", color=discord.Colour(0xff0000))
                        await ctx.send(embed=error, delete_after=5)
                    await member.add_roles(role)
                finishedUsers += 1
                await waitingMsg.edit(content=f"<:buffering:928709341568180254> Syncing...\nThis may take a while.\n{finishedUsers}/{len(ctx.guild.members)}")
        except:
            errors.append(member)
    if len(errors) > 0 and len(errors) < 10:
        em = discord.Embed(title="Errors", description=f"The following users had errors: {', '.join(str(x) for x in errors)}", color=discord.Colour(0xff0000))
        await ctx.send(embed=em, delete_after=5)
    elif len(errors) > 10:
        em = discord.Embed(title="Errors", description=f"The following users had errors: {', '.join(str(x) for x in errors[:10])} and {len(errors) -10}", color=discord.Colour(0xff0000))
        await ctx.send(embed=em, delete_after=5)
    else:
        em = discord.Embed(title="Success", description="All users have been synced.", color=discord.Colour(0x00ff00))
        await ctx.send(embed=em, delete_after=5)
    await waitingMsg.delete()

@slash.subcommand(base="roles", name="hexall", description="Runs /roles color on all users in the server.", options=[create_option(name="hex", description="The hex code of the color you want to make a role for.", option_type=3, required=True)])
async def roles_hexall(ctx, hex):
    finishedUsers = 0
    waitingMsg = await ctx.send(f"<:buffering:928709341568180254> Syncing...\nThis may take a while.\n{finishedUsers}/{len(ctx.guild.members)}")
    guild = ctx.guild
    errors = []
    hexCode = hex.replace("#", "")
    for member in guild.members:
        try:
            if discord.utils.get(guild.roles, name=f"#{hexCode}"):
                for role in member.roles:
                    if role.name.startswith("#") and role.name != f"#{hexCode}":
                        await member.remove_roles(role)
                await member.add_roles(discord.utils.get(guild.roles, name=f"#{hexCode}"))
            else:
                for role in member.roles:
                    if role.name.startswith("#") and role.name != f"#{hexCode}":
                        await member.remove_roles(role)
                db = database.servers
                collection = db.configs
                position = collection.find_one({"guild_id": guild.id})["position"]
                if position < len(guild.roles):
                    role = await guild.create_role(name=f"#{hexCode}", colour=discord.Colour(int(hexCode, base=16)))
                    await role.edit(position=position)
                else:
                    error = discord.Embed(title="Invalid Position", description="The position your server has set is invalid. Please enter a number between 0 and the number of roles in your server and reset with /config position. Defaulting to 0", color=discord.Colour(0xff0000))
                    await ctx.send(embed=error, delete_after=5)
                await member.add_roles(role)
            finishedUsers += 1
            await waitingMsg.edit(content=f"<:buffering:928709341568180254> Syncing...\nThis may take a while.\n{finishedUsers}/{len(ctx.guild.members)}")
        except:
            errors.append(member)
    if len(errors) > 0 and len(errors) < 10:
        em = discord.Embed(title="Errors", description=f"The following users were unable to recieve roles.: {', '.join(str(x) for x in errors)}", color=discord.Colour(0xff0000))
        await ctx.send(embed=em, delete_after=5)
    elif len(errors) > 10:
        em = discord.Embed(title="Errors", description=f"The following users were unable to recieve roles: {', '.join(str(x) for x in errors)[:10]} and {len(errors) - 10} more.", color=discord.Colour(0xff0000))
        await ctx.send(embed=em, delete_after=5)
    else:
        em = discord.Embed(title="Success", description=f"All users have been the color role #{hexCode}.", color=discord.Colour(0x00ff00))
        await ctx.send(embed=em, delete_after=5)
    await waitingMsg.delete()


# Management Commands

@slash.subcommand(base="manage", name="help", description="Shows the help menu for the manage commands.")
async def manage_help(ctx):
    if ctx.author.guild_permissions.administrator or ctx.author.id in config.OWNERS:
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
    if ctx.author.guild_permissions.administrator or ctx.author.id in config.OWNERS:
        if len(ctx.guild.roles) > 1:
            for role in ctx.guild.roles:
                if role.name.startswith("#") and len(role.name) == 7:
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
    if ctx.author.guild_permissions.administrator or ctx.author.id in config.OWNERS:
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

@slash.subcommand(base="manage", name="deleteuseless", description="Deletes all roles with no members using it.")
async def manage_deleteuseless(ctx):
    if ctx.author.guild_permissions.administrator or ctx.author.id in config.OWNERS:
        guild = ctx.guild
        for role in guild.roles:
            if role.name.startswith("#") and len(role.name) == 7 and len(role.members) == 0:
                await role.delete()
        em = discord.Embed(title="Roles Deleted", description=f"All of the roles with no members using them have been deleted.", color=discord.Colour(0x00ff00))
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title="No Permission", description="You do not have permission to use this command.", color=discord.Colour(0xff0000))
        await ctx.send(embed=em)

@slash.subcommand(base="manage", name="listroles", description="Lists all of the color roles on the server.")
async def manage_listroles(ctx):
    if ctx.author.guild_permissions.administrator or ctx.author.id in config.OWNERS:
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

# Server Config Commands

@slash.subcommand(base="config", name="help", description="Shows the help menu for the config commands.")
async def config_help(ctx):
    if ctx.author.guild_permissions.administrator or ctx.author.id in config.OWNERS:
        em = discord.Embed(title="Config Help", description="The config commands are used to configure the server.", color=discord.Colour(0x00ff00))
        em.add_field(name="position", value="Changes the position (from the bottom of the role list) of where new color roles will be placed.", inline=False)
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title="No Permission", description="You do not have permission to use this command.", color=discord.Colour(0xff0000))
        await ctx.send(embed=em, delete_after=5)

@slash.subcommand(base="config", name="position", description="Changes the position (from the bottom of the role list) of where new color roles will be placed.", options=[create_option(name="position", description="The position you want to change the new color roles to.", option_type=4, required=True)])
async def config_position(ctx, position):
    if ctx.author.guild_permissions.administrator or ctx.author.id in config.OWNERS:
        if position < 0 or position > len(ctx.guild.roles):
            em = discord.Embed(title="Invalid Position", description="The position you entered is invalid. Make sure it is greater or equal to 0 and is less than the amount of roles you have in your server.", color=discord.Colour(0xff0000))
            await ctx.send(embed=em, delete_after=5)
        else:
            guild = ctx.guild
            db = database.servers
            post = {
                "guild_id": guild.id,
                "position": position
            }
            posts = db.configs
            if posts.find_one({"guild_id": guild.id}):
                posts.update_one({"guild_id": guild.id}, {"$set": post})
            else:
                posts.insert_one(post)
            em = discord.Embed(title="Position Changed", description=f"The position of new color roles has been changed to {position}.", color=discord.Colour(0x00ff00))
            await ctx.send(embed=em, delete_after=5)
    else:
        em = discord.Embed(title="No Permission", description="You do not have permission to use this command.", color=discord.Colour(0xff0000))
        await ctx.send(embed=em, delete_after=5)

# Debug Commands

@slash.subcommand(base="debug", name="forceerror", description="Forces an error to be thrown.", options=[create_option(name="error", description="The error you want to throw.", option_type=3, required=False)])
async def debug_forceerror(ctx, error=None):
    if ctx.author.id in config.DEBUGPERMS:
        if error == None:
            raise SlashCommandError("This is a forced error.")
        else:
            raise SlashCommandError(f"{error} (Forced)")
    else:
        em = discord.Embed(title="No Permission", description="You do not have permission to use this command.", color=discord.Colour(0xff0000))
        await ctx.send(embed=em, delete_after=5)

@slash.subcommand(base="debug", name="status", description="Shows the status of the bot.", options=[create_option(name="dm",description="Would you like the info to be sent to you? This will uncencor any cencored information", option_type=5, required=False)])
async def debug_status(ctx, dm=False):
    if ctx.author.id in config.DEBUGPERMS:
        if dm == True:
            em = discord.Embed(title="Status", description=f"Status of all features.\n:green_circle: - Working as intended.\n:yellow_circle: - Lagging, not fully working as intended but main features still work. (Maybe restart?)\n:red_circle: - Fatal errors, unusable, crashed.", color=discord.Colour(0x00ff00))
            if round(bot.latency * 1000) <= 100:
                em.add_field(name="Bot", value=f":green_circle: ({round(bot.latency*1000)} ms delay)", inline=False)
            elif round(bot.latency * 1000) <= 101 and round(bot.latency * 1000) >= 499:
                em.add_field(name="Bot", value=f":yellow_circle: ({round(bot.latency*1000)} ms delay)", inline=False)
            else:
                em.add_field(name="Bot", value=f":red_circle: ({round(bot.latency*1000)} ms delay)", inline=False)

            try:
                info = database.server_info()
            except:
                em.add_field(name="Database", value=f":red_circle:", inline=False)
            else:
                em.add_field(name="Database", value=f":green_circle:", inline=False)

            await ctx.author.send(embed=em)
        else:
            em = discord.Embed(title="Status", description=f"Status of all features.\n:green_circle: - Working as intended.\n:yellow_circle: - Lagging, not fully working as intended but main features still work. (Maybe restart?)\n:red_circle: - Fatal errors, unusable, crashed.", color=discord.Colour(0x00ff00))
            if round(bot.latency * 1000) <= 100:
                em.add_field(name="Bot", value=f":green_circle: ({round(bot.latency*1000)} ms delay)", inline=False)
            elif round(bot.latency * 1000) <= 101 and round(bot.latency * 1000) >= 499:
                em.add_field(name="Bot", value=f":yellow_circle: ({round(bot.latency*1000)} ms delay)", inline=False)
            else:
                em.add_field(name="Bot", value=f":red_circle: ({round(bot.latency*1000)} ms delay)", inline=False)

            try:
                info = database.server_info()
            except:
                em.add_field(name="Database", value=f":red_circle:", inline=False)
            else:
                em.add_field(name="Database", value=f":green_circle:", inline=False)

            await ctx.send(embed=em)
    else:
        em = discord.Embed(title="No Permission", description="You do not have permission to use this command.", color=discord.Colour(0xff0000))
        await ctx.send(embed=em, delete_after=5)

@bot.event
async def on_slash_command_error(ctx, ex):
    em = discord.Embed(title="Error", colour=0xaa0000)
    em.add_field(name="Traceback", value=ex)
    em.add_field(name="Support", value=f"[Support Server](https://discord.gg/TZpHkkNUmh)")
    await ctx.send(embed=em)
    print(f"\n\n\n\n\nError!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nLMFAO U SUCK AT CODING!!!!!!!!!!!!!!!!!!!!!!!\n\nDEBUG: {ctx.guild.name} - {ctx.channel} - {ctx.author}\n\nDEBUG: {ex}")

bot.run(TOKEN)
