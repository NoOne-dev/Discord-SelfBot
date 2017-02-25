import discord
import datetime
import logging
import unicodedata

from discord import utils
from discord.ext import commands
from .utils.checks import getUser, getAvi, perms

log = logging.getLogger('LOG')


class Userinfo:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(no_pm=True)
    async def info(self, ctx):
        mem = getUser(ctx.message, ctx.message.content[6:])
        if mem is not None:
            rolelist = ''
            for roles in mem.roles:
                rolelist += ', %s' % roles.name
            guildlist = '﻿'
            guildcount = 0
            for guild in self.bot.guilds:
                if guild is not ctx.message.guild:
                    if guild.get_member(mem.id):
                        guildlist += ', %s' % guild.name
                        guildcount += 1
            rel = str(mem.relationship.type)[17:].title() if mem.relationship is not None else None
            pro = await mem.profile()
            nitro = pro.premium_since.__format__('Since: %d/%m/%Y') if pro.premium is True else None
            em = discord.Embed(timestamp=ctx.message.created_at, colour=mem.colour)
            if mem.game is not None:
                em = discord.Embed(description='Playing **%s**' % mem.game, timestamp=ctx.message.created_at, colour=mem.colour)
            em.add_field(name='User ID', value=mem.id, inline=True)
            em.add_field(name='Status', value=mem.status, inline=True)
            em.add_field(name='Nick', value=mem.nick, inline=True)
            em.add_field(name='In Voice', value=mem.voice,  inline=True)
            em.add_field(name='Partnership', value=rel,  inline=True)
            em.add_field(name='Nitro', value=nitro,  inline=True)
            em.add_field(name='Account Created', value='%s, %s Days' % (mem.created_at.__format__('%d/%m/%Y'), int((datetime.datetime.now() - mem.created_at).total_seconds() // (60 * 60 * 24))), inline=True)
            em.add_field(name='Join Date', value='%s, %s Days' % (mem.joined_at.__format__('%d/%m/%Y'), int((datetime.datetime.now() - mem.joined_at).total_seconds() // (60 * 60 * 24))), inline=True)
            if rolelist[13:] is not '':
                em.add_field(name='Roles [%s]' % (len(mem.roles)-1), value=rolelist[13:], inline=True)
            if (mem.id is not ctx.message.author.id) and guildlist[2:] is not '':
                em.add_field(name='Shared Guilds [%s]' % guildcount, value='%s' % guildlist[2:], inline=True)
            em.set_thumbnail(url=getAvi(mem))
            em.set_author(name=mem, icon_url='https://i.imgur.com/RHagTDg.png')
            await ctx.message.delete()
            if perms(ctx.message):
                await ctx.send(embed=em, delete_after=20)
            else:
                await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} No Perms for Embeds, move to a better Guild!', delete_after=5)
        else:
            await ctx.message.delete()
            await ctx.send("\N{HEAVY EXCLAMATION MARK SYMBOL} User not found",  delete_after=20)

    @commands.command(no_pm=True)
    async def role(self, ctx):
        role = None
        if 1 == len(ctx.message.role_mentions):
            role = ctx.message.role_mentions[0]
        else:
            role = utils.find(lambda r: ctx.message.content[5:].strip().lower() in r.name.lower(), ctx.message.guild.roles)
        if role is not None:
            onlineuser = 0
            roleuser = 0
            for x in ctx.message.guild.members:
                if role in x.roles:
                    if str(x.status) != 'offline':
                        onlineuser += 1
                        roleuser += 1
                    else:
                        roleuser += 1
            em = discord.Embed(timestamp=ctx.message.created_at, colour=role.colour)
            em.add_field(name='Name', value=role.name, inline=True)
            em.add_field(name='ID', value=role.id, inline=True)
            em.add_field(name='Created On', value=role.created_at.__format__('%d/%m/%Y %H:%M:%S'), inline=True)
            em.add_field(name='Mentionable', value=role.mentionable,  inline=True)
            em.add_field(name='Color', value=str(role.colour).upper(), inline=True)
            em.add_field(name='Members [%s]' % roleuser, value='%s Online' % onlineuser, inline=True)
            em.set_thumbnail(url='http://www.colorhexa.com/%s.png' % str(role.colour).replace("#", ""))
            await ctx.message.delete()
            if perms(ctx.message):
                await ctx.send(embed=em, delete_after=20)
            else:
                await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} No Perms for Embeds, move to a better Guild!', delete_after=5)
        else:
            await ctx.message.delete()
            await ctx.send("\N{HEAVY EXCLAMATION MARK SYMBOL} Role not found",  delete_after=20)

    @commands.command(no_pm=True)
    async def guild(self, ctx):
        serv = ctx.message.guild
        rolelist = ''
        onlineuser = 0
        for roles in serv.role_hierarchy:
            if not roles.is_default():
                rolelist += ', %s' % roles.name
        for x in serv.members:
            if str(x.status) != 'offline':
                onlineuser += 1
        em = discord.Embed(timestamp=ctx.message.created_at, colour=ctx.message.author.colour)
        em.set_author(name=serv.name, icon_url='https://i.imgur.com/RHagTDg.png')
        em.set_thumbnail(url=serv.icon_url)
        em.add_field(name='ID', value=serv.id, inline=True)
        em.add_field(name='Region', value=serv.region, inline=True)
        em.add_field(name='Created On', value=serv.created_at.__format__('%d/%m/%Y %H:%M:%S'), inline=True)
        em.add_field(name='Owner', value='%s' % serv.owner,  inline=True)
        em.add_field(name='Members [%s]' % serv.member_count, value='%s Online' % onlineuser, inline=True)
        em.add_field(name='Channels [%s]' % len(serv.channels), value='%s Text | %s Voice' % (len(serv.text_channels), len(serv.voice_channels)), inline=True)
        em.add_field(name='Roles [%s]' % (len(serv.roles)-1), value=rolelist[2:], inline=False)
        await ctx.message.delete()
        if perms(ctx.message):
            await ctx.send(embed=em, delete_after=20)
        else:
            await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} No Perms for Embeds, move to a better Guild!', delete_after=5)

    @commands.command(no_pm=True)
    async def emotes(self, ctx):
        unique_emojis = set(ctx.message.guild.emojis)
        em = discord.Embed(timestamp=ctx.message.created_at, title='Emotes [%s]' % len(unique_emojis), colour=ctx.message.author.colour)
        allWords = []
        splitmsg = ''
        count = 0
        for blocks in unique_emojis:
            if (len(splitmsg + str(blocks) + ' ')) <= 1024:
                splitmsg += str(blocks) + ' '
                count += 1
                if count == len(unique_emojis):
                    allWords.append(splitmsg)
            else:
                allWords.append(splitmsg)
                splitmsg = ''
                splitmsg += str(blocks) + ' '
                count += 1
        for i in allWords:
            em.add_field(name='﻿', value=i, inline=False)
        if unique_emojis is None:
            em.add_field(name='Emotes', value='Not Found \N{HEAVY EXCLAMATION MARK SYMBOL}', inline=False)
        await ctx.message.delete()
        if perms(ctx.message):
            await ctx.send(embed=em, delete_after=20)
        else:
            await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} No Perms for Embeds, move to a better Guild!', delete_after=5)

    @commands.command(no_pm=True)
    async def avi(self, ctx):
        mem = getUser(ctx.message, ctx.message.content[5:])
        if mem is not None:
            em = discord.Embed(timestamp=ctx.message.created_at, colour=mem.colour)
            em.set_image(url=getAvi(mem))
            em.set_author(name=mem, icon_url='https://i.imgur.com/RHagTDg.png')
            await ctx.message.delete()
            if perms(ctx.message):
                await ctx.send(embed=em, delete_after=20)
            else:
                await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} No Perms for Embeds, move to a better Guild!', delete_after=5)
        else:
            await ctx.message.delete()
            await ctx.send("\N{HEAVY EXCLAMATION MARK SYMBOL} User not found",  delete_after=5)

    @commands.command()
    async def emote(self, ctx, emote: str):
        success = False
        # if len(emote) > 1:
        #     em = emote.split(':')
        #     emo = None
        #     for i in self.bot.guilds:
        #         try:
        #             emo = utils.get(i.emojis, id=em[1])
        #             if emo:
        #                 success = True
        #                 await ctx.send(emo.url)
        #                 break
        #         except:
        #             pass
        if len(emote) is 1:
            success = True
            uni = format(ord(emote), 'x')
            name = unicodedata.name(emote)
            e = discord.Embed(title=name, description='`\\U{0:>08}`\nhttp://twemoji.maxcdn.com/svg/{0}.svg'.format(uni), colour=0x9b59b6)
            e.set_thumbnail(url='http://twemoji.maxcdn.com/72x72/{}.png'.format(uni))
            await ctx.send(embed=e)
        if not success:
            await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} Either Custom Emote or a unicode symbol!', delete_after=3)


def setup(bot):
    bot.add_cog(Userinfo(bot))
