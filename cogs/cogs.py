import asyncio
import logging
import os
import sys

from discord.ext import commands
from .utils import config
from .utils.checks import send

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
            await send(ctx, content='Not Loading', ttl=5)
            await send(ctx, content='``{}: {}``'.format(type(e).__name__, e), ttl=5)
            log.error('Loading {} faild!\n{}: {}'.format(module, type(e).__name__, e))
        else:
            await send(ctx, content='Loaded %s' % module, ttl=5)
            log.info('Loaded %s' % module)

    # Unloads a module
    @commands.command()
    async def unload(self, ctx, *, module: str):
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await send(ctx, content='Not unloading', ttl=5)
            await send(ctx, content='``{}: {}``'.format(type(e).__name__, e), ttl=5)
            log.error('Unloading {} faild!\n{}: {}'.format(module, type(e).__name__, e))
        else:
            await send(ctx, content='Unloaded %s' % module, ttl=5)
            log.info('Unloaded %s' % module)

    # Reloads a module.
    @commands.command()
    async def reload(self, ctx, module: str = None):
        if not module:
            utils = []
            for i in self.bot.extensions:
                utils.append(i)
            fail = False
            for i in utils:
                self.bot.unload_extension(i)
                try:
                    self.bot.load_extension(i)
                except Exception as e:
                    await send(ctx, content='Failed to reload extension ``%s``' % i, ttl=5, delete=False)
                    await send(ctx, content='``{}: {}``'.format(type(e).__name__, e), ttl=5, delete=False)
                    log.error('Reloading {} failed!\n{}: {}'.format(i, type(e).__name__, e))
                    fail = True
            if fail:
                await send(ctx, content='Reloaded remaining extensions.', ttl=5)
            else:
                await send(ctx, content='Reloaded all extensions.', ttl=5)
                log.info('Reloaded all extensions.')
        else:
            try:
                self.bot.unload_extension(module)
                self.bot.load_extension(module)
            except Exception as e:
                await send(ctx, content='Not reloading', ttl=5)
                await send(ctx, content='``{}: {}``'.format(type(e).__name__, e), ttl=5)
                log.error('Reloading {} failed!\n{}: {}'.format(module, type(e).__name__, e))
            else:
                await send(ctx, content='Reloaded %s' % module, ttl=5)
                log.info('Reloaded %s' % module)

    # Shutdown Bot
    @commands.command()
    async def quit(self, ctx):
        await send(ctx, content='Bot has been killed.', ttl=2)
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
