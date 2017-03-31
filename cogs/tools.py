import asyncio
import datetime
import discord
import os
import platform
import psutil

from .utils.checks import me, send, getwithoutInvoke, getTimeDiff
from .utils import config
from discord.ext import commands


class Tools:

    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('config.json')

    # Command usage stats
    @commands.command()
    async def cmdstats(self, ctx):
        await ctx.message.delete()
        p = commands.Paginator()
        counter = self.bot.commands_triggered
        width = len(max(counter, key=len))
        total = sum(counter.values())
        fmt = '{0:<{width}}: {1}'
        p.add_line(fmt.format('Total', total, width=width))
        for key, count in counter.most_common():
            p.add_line(fmt.format(key, count, width=width))
        for page in p.pages:
            await ctx.send(page, delete_after=20)

    @commands.command()
    async def socketstats(self, ctx):
        delta = datetime.datetime.now() - self.bot.uptime
        minutes = delta.total_seconds() / 60
        total = sum(self.bot.socket_stats.values())
        cpm = total / minutes

        fmt = '%s socket events observed (%.2f/minute):\n%s'
        await send(ctx, content=fmt % (total, cpm, self.bot.socket_stats))

    # Ping Time
    @commands.command()
    async def ping(self, ctx):
        before = datetime.datetime.now()
        await (await self.bot.ws.ping())
        ping = (datetime.datetime.now() - before) * 1000
        pong = discord.Embed(title='Pong!', colour=0x9b59b6)
        pong.add_field(name="Response Time:", value='{:.2f}ms'.format(ping.total_seconds()))
        pong.set_thumbnail(url='http://i.imgur.com/SKEmkvf.png')
        await send(ctx, embed=pong, ttl=5)

    # Time Since Bot is running
    @commands.command()
    async def uptime(self, ctx):
        embed = discord.Embed(title='\N{CLOCK FACE THREE OCLOCK} UPTIME', colour=0x9b59b6)
        embed.add_field(name='﻿ ', value=getTimeDiff(self.bot.uptime), inline=False)
        embed.set_thumbnail(url='http://i.imgur.com/mfxd06f.gif')
        await send(ctx, embed=embed, ttl=20)

    # Various stat about the bot since startup
    @commands.command()
    async def stats(self, ctx):
        unique_online = len(dict((m.id, m) for m in self.bot.get_all_members() if m.status != discord.Status.offline))
        voice = sum(len(g.voice_channels) for g in self.bot.guilds)
        text = sum(len(g.text_channels) for g in self.bot.guilds)
        embed = discord.Embed(title='\N{ELECTRIC LIGHT BULB} Bot Info', colour=0x9b59b6)
        embed.add_field(name='\N{CLOCK FACE THREE OCLOCK} UPTIME',
                        value=getTimeDiff(self.bot.uptime), inline=True)
        embed.add_field(name='\N{INBOX TRAY} Messages Received',
                        value=(self.bot.message_count - self.bot.icount), inline=True)
        embed.add_field(name='\N{OUTBOX TRAY} Messages Sent',
                        value=self.bot.icount, inline=True)
        embed.add_field(name='\N{SPEAKING HEAD IN SILHOUETTE} Members [%s]' % len(self.bot.users),
                        value='%s Online' % unique_online, inline=True)
        embed.add_field(name='\N{SPIRAL NOTE PAD} Channels [%s]' % (text+voice),
                        value='%s Text | %s Voice' % (text, voice), inline=True)
        embed.add_field(name='\N{TICKET} Guilds',
                        value=len(self.bot.guilds))
        embed.add_field(name='\N{BELL} Mentions [%s]' % (self.bot.mention_count + self.bot.mention_count_name),
                        value='%s Pings | %s Names' % (self.bot.mention_count, self.bot.mention_count_name), inline=True)
        embed.add_field(name='\N{SPEECH BALLOON} Commands Used',
                        value=sum(self.bot.commands_triggered.values()), inline=True)
        try:
            embed.add_field(name='\N{ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS} Most Used',
                            value='%s [%s]' % (self.bot.commands_triggered.most_common()[0][0], self.bot.commands_triggered.most_common()[0][1]))
        except:
            embed.add_field(name='\N{ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS} Most Used',
                            value='﻿None')
        await send(ctx, embed=embed, ttl=20)

    # Host System Infos
    @commands.command()
    async def sysinfo(self, ctx):
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_full_info().uss / 1024**2
        avai = psutil.virtual_memory().total / 1024**2
        mepro = process.memory_percent()
        prosys = psutil.cpu_percent()
        sys = '%s %s' % (platform.linux_distribution(full_distribution_name=1)[0].title(), platform.linux_distribution(full_distribution_name=1)[1])
        embed = discord.Embed(title='\N{ELECTRIC LIGHT BULB} Host Info', colour=0x9b59b6)
        embed.add_field(name='\N{CLOCK FACE THREE OCLOCK} UPTIME',
                        value=getTimeDiff(datetime.datetime.fromtimestamp(int(process.create_time()))))
        embed.add_field(name='\N{DESKTOP COMPUTER} SYSTEM',
                        value='{0}, {1}'.format(platform.system(), sys, platform.release()))
        embed.add_field(name='\N{FLOPPY DISK} MEMORY',
                        value='{:.2f} MiB / {:.2f} MiB\nBot uses: {:.2f}%'.format(memory_usage, avai, mepro))
        embed.add_field(name='\N{DVD} CPU',
                        value='{:.2f}%'.format(prosys))
        await send(ctx, embed=embed, ttl=20)

    # Change Gamestatus - blank is no game
    @commands.command()
    async def game(self, ctx):
        await self.config.put('gamestatus', getwithoutInvoke(ctx))
        await send(ctx, 'Now playing: ``%s``' % self.config.get('gamestatus', []),  ttl=5)

    # Find message with specific Text in Channel History...    Search Term(s) | Text
    @commands.command()
    async def quote(self, ctx):
        search = getwithoutInvoke(ctx)
        content = '\U0000200d'
        if '|' in search:
            msg = search.split(" | ")
            search = msg[0]
            content = msg[1]
        async for message in ctx.message.channel.history(limit=500):
            if message.id != ctx.message.id and search in message.content:
                em = discord.Embed(description=message.clean_content, timestamp=message.created_at, colour=0x33CC66)
                em.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
                await send(ctx, content=content, embed=em)
                return
        await send(ctx, 'Message not found!', ttl=3)

    # Deletes messages from Channel History - only number for own, number and "all" to delete every message and not only the own
    @commands.command()
    async def clean(self, ctx, limit: int=25):
        msg_amt = 0
        async for message in ctx.message.channel.history(limit=limit):
                if me(message):
                    try:
                        await message.delete()
                    except:
                        pass
                    await asyncio.sleep(0.25)
                    msg_amt += 1
                elif ctx.message.content.endswith('all') and ctx.message.author.permissions_in(ctx.message.channel).manage_messages:
                    try:
                        await message.delete()
                    except:
                        pass
                    await asyncio.sleep(0.25)
                    msg_amt += 1
        await send(ctx, f'Cleaned `{msg_amt}` messages out of `{limit}` that were checked.', ttl=3, delete=False)


def setup(bot):
    bot.add_cog(Tools(bot))
