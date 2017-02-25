import asyncio
import logging
import os
import sys

from discord.ext import commands
from .utils import config

log = logging.getLogger('LOG')


class Cogs:

    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('config.json')

    # Loads a module
    @commands.command()
    async def load(self, ctx, *, module: str):
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.message.delete()
            await ctx.send('Not Loading', delete_after=5)
            await ctx.send('``{}: {}``'.format(type(e).__name__, e), delete_after=5)
            log.error('Loading {} faild!\n{}: {}'.format(module, type(e).__name__, e))
        else:
            await ctx.message.delete()
            await ctx.send('Loaded %s' % module, delete_after=5)
            log.info('Loaded %s' % module)

    # Unloads a module
    @commands.command()
    async def unload(self, ctx, *, module: str):
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await ctx.message.delete()
            await ctx.send('Not unloading', delete_after=5)
            await ctx.send('``{}: {}``'.format(type(e).__name__, e), delete_after=5)
            log.error('Unloading {} faild!\n{}: {}'.format(module, type(e).__name__, e))
        else:
            await ctx.message.delete()
            await ctx.send('Unloaded %s' % module, delete_after=5)
            log.info('Unloaded %s' % module)

    # Reloads a module.
    @commands.command()
    async def reload(self, ctx):
        if ctx.message.content[7:] is '':
            utils = []
            for i in self.bot.extensions:
                utils.append(i)
            fail = False
            for i in utils:
                self.bot.unload_extension(i)
                try:
                    self.bot.load_extension(i)
                except Exception as e:
                    await ctx.send('Failed to reload extension ``%s``' % i, delete_after=5)
                    await ctx.send('``{}: {}``'.format(type(e).__name__, e), delete_after=5)
                    log.error('Reloading {} failed!\n{}: {}'.format(i, type(e).__name__, e))
                    fail = True
            if fail:
                await ctx.send('Reloaded remaining extensions.', delete_after=5)
            else:
                await ctx.send('Reloaded all extensions.', delete_after=5)
                log.info('Reloaded all extensions.')
            await ctx.message.delete()
        else:
            try:
                self.bot.unload_extension(ctx.message.content[7:].strip())
                self.bot.load_extension(ctx.message.content[7:].strip())
            except Exception as e:
                await ctx.message.delete()
                await ctx.send('Not reloading', delete_after=5)
                await ctx.send('``{}: {}``'.format(type(e).__name__, e), delete_after=5)
                log.error('Reloading {} failed!\n{}: {}'.format(ctx.message.content[7:].strip(), type(e).__name__, e))
            else:
                await ctx.message.delete()
                await ctx.send('Reloaded %s' % ctx.message.content[7:].strip(), delete_after=5)
                log.info('Reloaded %s' % ctx.message.content[7:].strip())

    # Shutdown Bot
    @commands.command()
    async def quit(self, ctx):
        await ctx.message.delete()
        await ctx.send('Bot has been killed.', delete_after=2)
        log.warning('Bot has been killed.')
        with open('quit.txt', 'w') as re:
            re.write('quit')
        exit()

    # Restart selfbot
    @commands.command()
    async def restart(self, ctx):
        await self.config.put('restart', 'true')
        await self.config.put('restart_channel', ctx.message.channel.id)
        log.info('Restarting....')
        await ctx.message.edit(content='Good Bye :wave:')
        await asyncio.sleep(.5)
        await ctx.message.delete()
        python = sys.executable
        os.execl(python, python, *sys.argv)


def setup(bot):
    bot.add_cog(Cogs(bot))
