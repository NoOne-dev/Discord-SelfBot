import datetime
import json
import time

from discord import utils


with open('config/config.json', 'r') as f:
    config = json.load(f)


# Send made easier
async def send(ctx, content=None, embed=None, delete=True, ttl=None, file=None):
    perms = ctx.channel.permissions_for(ctx.me).embed_links
    if delete is True and perms is True:
        await ctx.message.delete()
        await ctx.send(content=content, embed=embed, file=file, delete_after=ttl)
    elif delete is False and perms is True:
        await ctx.send(content=content, embed=embed, file=file, delete_after=ttl)
    elif perms is False:
        await ctx.send(content='\N{HEAVY EXCLAMATION MARK SYMBOL} No Perms for Embeds', delete_after=5)


# Check if me
def me(message):
    return message.author.id == config['me']


# Check for perms of links and attached files
def permFile(message):
    return message.channel.permissions_for(message.author).attach_files


# Check for perms of links and attached files
def permEmbed(message):
    return message.channel.permissions_for(message.author).embed_links


# Time for Gamestatus upate
def hasPassed(bot, oldtime):
    if time.time() - 60 < oldtime:
        return False
    bot.refresh_time = time.time()
    return True


def getwithoutInvoke(ctx):
    return ctx.message.content[len(ctx.prefix + ctx.command.qualified_name + ' '):]


def getTimeDiff(t):
    delta = datetime.datetime.now() - t
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    return '{d}:{h}:{m}:{s}'.format(d=days, h=hours, m=minutes, s=seconds)


def getDays(time):
    return int((datetime.datetime.now() - time).total_seconds() // (60 * 60 * 24))


# Find User on server
def getUser(ctx, msg):
    if '' is msg:
        return ctx.message.author
    elif not ctx.guild:
        if utils.find(lambda m: msg.lower() in m.name.lower(), ctx.bot.users):
            return utils.find(lambda m: msg.lower() in m.name.lower(), ctx.bot.users)
        elif 1 == len(ctx.message.mentions):
            return ctx.message.mentions[0]
    elif 1 == len(ctx.message.mentions):
        return ctx.message.mentions[0]
    elif ctx.message.guild.get_member_named(msg):
        return ctx.message.guild.get_member_named(msg)
    elif utils.find(lambda m: msg.lower() in m.name.lower(), ctx.message.guild.members):
        return utils.find(lambda m: msg.lower() in m.name.lower(), ctx.message.guild.members)
    else:
        for member in ctx.message.guild.members:
            if member.nick:
                if msg.lower() in member.nick.lower():
                    return member
                    break
    return None
