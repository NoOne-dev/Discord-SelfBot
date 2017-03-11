import discord
import datetime
import logging
import unicodedata

from discord import utils
from discord.ext import commands
from .utils.checks import getUser, perms

log = logging.getLogger('LOG')


class Userinfo:

    def __init__(self, bot):
        self.bot = bot

    # User info on Server
    @commands.command()
    async def info(self, ctx):
        pre = len(ctx.prefix + ctx.command.qualified_name + ' ')
        mem = getUser(ctx, ctx.message.content[pre:])
        if mem:
            if not mem.bot:
                rel = str(mem.relationship.type)[17:].title() if mem.relationship is not None else None
                pro = await mem.profile()
                nitro = pro.premium_since.__format__('Since: %d/%m/%Y') if pro.premium is True else None
            em = discord.Embed(timestamp=ctx.message.created_at)
            em.colour = mem.colour if ctx.guild else 0x9b59b6
            em.add_field(name='User ID', value=mem.id, inline=True)
            if ctx.guild:
                if mem.game:
                    em.description = 'Playing **%s**' % mem.game
                em.add_field(name='Status', value=mem.status, inline=True)
            if ctx.guild:
                em.add_field(name='Nick', value=mem.nick, inline=True)
                em.add_field(name='In Voice', value=mem.voice,  inline=True)
            if not mem.bot:
                em.add_field(name='Partnership', value=rel,  inline=True)
                em.add_field(name='Nitro', value=nitro,  inline=True)
            em.add_field(name='Account Created', value='%s, %s Days' % (mem.created_at.__format__('%d/%m/%Y'), int((datetime.datetime.now() - mem.created_at).total_seconds() // (60 * 60 * 24))), inline=True)
            if ctx.guild:
                em.add_field(name='Join Date', value='%s, %s Days' % (mem.joined_at.__format__('%d/%m/%Y'), int((datetime.datetime.now() - mem.joined_at).total_seconds() // (60 * 60 * 24))), inline=True)
            if ctx.guild:
                rolelist = ', '.join(r.name for r in mem.roles)
                if rolelist[11:]:
                    em.add_field(name='Roles [%s]' % (len(mem.roles)-1), value=rolelist[11:], inline=True)
            guildlist = ', '.join(g.name for g in self.bot.guilds if g.get_member(mem.id))
            if (mem.id is not ctx.message.author.id) and guildlist:
                em.add_field(name='Shared Guilds [%s]' % len(guildlist.split(',')), value='%s' % guildlist, inline=True)
            em.set_thumbnail(url=mem.avatar_url)
            em.set_author(name=mem, icon_url='https://i.imgur.com/RHagTDg.png')
            await ctx.message.delete()
            if perms(ctx.message):
                await ctx.send(embed=em, delete_after=20)
            else:
                await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} No Perms for Embeds, move to a better Guild!', delete_after=5)
        else:
            await ctx.message.delete()
            await ctx.send("\N{HEAVY EXCLAMATION MARK SYMBOL} User not found",  delete_after=20)

    # User Avi on Server
    @commands.command()
    async def avi(self, ctx):
        pre = len(ctx.prefix + ctx.command.qualified_name + ' ')
        mem = getUser(ctx, ctx.message.content[pre:])
        if mem is not None:
            em = discord.Embed(timestamp=ctx.message.created_at)
            em.colour = mem.colour if ctx.guild else 0x9b59b6
            em.set_image(url=mem.avatar_url)
            em.set_author(name=mem, icon_url='https://i.imgur.com/RHagTDg.png')
            await ctx.message.delete()
            if perms(ctx.message):
                await ctx.send(embed=em, delete_after=20)
            else:
                await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} No Perms for Embeds, move to a better Guild!', delete_after=5)
        else:
            await ctx.message.delete()
            await ctx.send("\N{HEAVY EXCLAMATION MARK SYMBOL} User not found",  delete_after=5)

    # Roleinfo on Server
    @commands.command(no_pm=True)
    async def role(self, ctx):
        role = None
        pre = len(ctx.prefix + ctx.command.qualified_name + ' ')
        if 1 == len(ctx.message.role_mentions):
            role = ctx.message.role_mentions[0]
        else:
            role = utils.find(lambda r: ctx.message.content[pre:].strip().lower() in r.name.lower(), ctx.message.guild.roles)
        if role is not None:
            roleuser = len(role.members)
            onlineuser = sum(1 for m in role.members if m.status != discord.Status.offline)
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

    # Serverinfo on Server
    @commands.command(no_pm=True, aliases=["server"])
    async def guild(self, ctx):
        serv = ctx.message.guild
        rolelist = ', '.join(r.name for r in serv.role_hierarchy)
        onlineuser = sum(1 for m in serv.members if m.status != discord.Status.offline)
        em = discord.Embed(timestamp=ctx.message.created_at, colour=ctx.message.author.colour)
        em.set_author(name=serv.name, icon_url='https://i.imgur.com/RHagTDg.png')
        em.set_thumbnail(url=serv.icon_url)
        em.add_field(name='ID', value=serv.id, inline=True)
        em.add_field(name='Region', value=serv.region, inline=True)
        em.add_field(name='Created On', value=serv.created_at.__format__('%d/%m/%Y %H:%M:%S'), inline=True)
        em.add_field(name='Owner', value='%s' % serv.owner,  inline=True)
        em.add_field(name='Members [%s]' % serv.member_count, value='%s Online' % onlineuser, inline=True)
        em.add_field(name='Channels [%s]' % len(serv.channels), value='%s Text | %s Voice' % (len(serv.text_channels), len(serv.voice_channels)), inline=True)
        em.add_field(name='Roles [%s]' % (len(serv.roles)-1), value=rolelist[:-11], inline=False)
        await ctx.message.delete()
        if perms(ctx.message):
            await ctx.send(embed=em, delete_after=20)
        else:
            await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} No Perms for Embeds, move to a better Guild!', delete_after=5)

    # Emotes from Server
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

    # Info of Custom or Unicode Emotes
    @commands.command()
    async def emote(self, ctx, emote: str):
        await ctx.message.delete()
        if '>' in emote and '<:' in emote and ':' in emote:
            emote = emote.replace('<:', '').replace('>', '').split(':')[1]
            emo = utils.get(self.bot.emojis, id=int(emote))
            if emo:
                date = emo.created_at.__format__('%d/%m/%Y')
                days = int((datetime.datetime.now() - emo.created_at).total_seconds() // (60 * 60 * 24))
                e = discord.Embed(title='Custom Emote', colour=0x9b59b6)
                e.description = '**Name: **{1}\n**ID: **{2}\n**Server: **{0}\n**Created at: **{3}, {4} Days ago\n**Image: **[link]({5})'.format(emo.guild.name, emo.name, emo.id, date, days, emo.url)
                e.set_thumbnail(url=emo.url)
                await ctx.send(embed=e)
        else:
            split = '\n'.join(emote).split('\n')
            e = discord.Embed(title='Unicode Emote {}'.format(emote), colour=0x9b59b6)
            desc = ''
            if len(split) > 1:
                desc += '**Parts:**\n'
                for i in split:
                    desc += '{0} - `\\U{2:>08}` - {1}\nhttp://www.fileformat.info/info/unicode/char/{2}\n'.format(unicodedata.name(i), i, format(ord(i), 'x'))
            else:
                desc += '{0} - `\\U{1:>08}`\nhttp://www.fileformat.info/info/unicode/char/{1}\n'.format(unicodedata.name(split[0]), format(ord(split[0]), 'x'))
            e.description = desc
            if len(emote) > 20:
                await ctx.send(content='\N{HEAVY EXCLAMATION MARK SYMBOL} Come on, only 20 chars...', delete_after=3)
            else:
                await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Userinfo(bot))
