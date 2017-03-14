import json
import time

from discord import utils


with open('config/config.json', 'r') as f:
    config = json.load(f)


# Check if me
def me(message):
    return message.author.id == config['me']


# Check for perms of links and attached files
def perms(message):
    return message.author.permissions_in(message.channel).attach_files and message.author.permissions_in(message.channel).embed_links


# Time for Gamestatus upate
def hasPassed(bot, oldtime):
    if time.time() - 60 < oldtime:
        return False
    bot.refresh_time = time.time()
    return True


def getInvoke(ctx):
    return len(ctx.prefix + ctx.command.qualified_name + ' ')


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
