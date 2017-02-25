import json
import time

from discord import utils


with open('cogs/utils/config.json', 'r') as f:
    config = json.load(f)


def me(message):
    return message.author.id == config['me']


def perms(message):
    return message.author.permissions_in(message.channel).attach_files and message.author.permissions_in(message.channel).embed_links


def hasPassed(bot, oldtime):
    if time.time() - 60 < oldtime:
        return False
    bot.refresh_time = time.time()
    return True


def getAvi(user):
    if user.avatar_url is '':
        return user.default_avatar_url
    else:
        return user.avatar_url


def getUser(message, msg):
    if '' is msg:
        return message.author
    elif 1 == len(message.mentions):
        return message.mentions[0]
    elif message.guild.get_member_named(msg) is not None:
        return message.guild.get_member_named(msg)
    elif utils.find(lambda m: msg.lower() in m.name.lower(), message.guild.members) is not None:
        return utils.find(lambda m: msg.lower() in m.name.lower(), message.guild.members)
    else:
        for member in message.guild.members:
            if member.nick is not None:
                if msg.lower() in member.nick.lower():
                    return member
                    break
    return None
