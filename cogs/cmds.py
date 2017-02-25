import asyncio
import json
import logging
import re

from discord.ext import commands

log = logging.getLogger('LOG')


class Customcmds:

    def __init__(self, bot):
        self.bot = bot

    # List all custom commands without links
    @commands.group()
    async def cmds(self, ctx):
        if ctx.invoked_subcommand is None:
            p = commands.Paginator(prefix='```css')
            with open('cogs/utils/commands.json', 'r') as com:
                cmds = json.load(com)
            p.add_line('[List of Custom Commands]')
            for cmd in cmds:
                if type(cmds[cmd]) == list:
                    msg = cmd + ' { '
                    for i in cmds[cmd]:
                        msg += str(i[0]) + ', '
                    msg = msg[:-2] + ' }'
                    p.add_line(msg)
                else:
                    p.add_line(cmd)
            for page in p.pages:
                await ctx.send(page, delete_after=20)
            await ctx.message.delete()

    # List all custom commands with Links
    @cmds.command()
    async def long(self, ctx):
        p = commands.Paginator(prefix='```json\n{', suffix='}```')
        with open('cogs/utils/commands.json', 'r') as com:
            cmds = json.load(com)
        p.add_line('"List of Custom Commands" :"",')
        p.add_line(empty=True)
        for cmd in cmds:
            msg = '"' + cmd + '" : "'
            if type(cmds[cmd]) == list:
                for i in cmds[cmd]:
                    msg += str(i) + ', '
                msg = msg[:-2] + '",\n'
                p.add_line(msg)
            else:
                msg += str(cmds[cmd]) + '",\n'
                p.add_line(msg)
        for page in p.pages:
            await ctx.send(page, delete_after=20)
        await ctx.message.delete()

    # Add a custom command
    @commands.command()
    async def add(self, ctx, *, msg: str):
        words = msg.strip()

        with open('cogs/utils/commands.json', 'r') as commands:
            cmds = json.load(commands)
            save = cmds

        try:

            # If there are quotes in the message (meaning multiple words for each param)
            if '"' in words:
                entry = re.findall('"([^"]+)"', words)

                # Item for key is list
                if len(entry) == 3:

                    # Key exists
                    if entry[0] in cmds:
                        entries = []
                        for i in cmds[entry[0]]:
                            entries.append(tuple((i[0], i[1])))
                        entries.append(tuple([entry[1], entry[2]]))
                        cmds[entry[0]] = entries
                    else:
                        cmds[entry[0]] = [(entry[1], entry[2])]

                # Item for key is string
                else:
                    cmds[entry[0]] = entry[1]

            # No quotes so spaces seperate params
            else:

                # Item for key is list
                if len(words.split(' ')) == 3:
                    entry = words.split(' ', 2)

                    # Key exists
                    if entry[0] in cmds:
                        entries = []
                        for i in cmds[entry[0]]:
                            entries.append(tuple((i[0], i[1])))
                        entries.append(tuple([entry[1], entry[2]]))
                        cmds[entry[0]] = entries
                    else:
                        cmds[entry[0]] = [(entry[1], entry[2])]

                # Item for key is string
                else:
                    entry = words.split(' ', 1)
                    cmds[entry[0]] = entry[1]

            msg = await ctx.send('Successfully added ``%s`` to ``%s``' % (entry[1], entry[0]))

        except Exception as e:
            with open('cogs/utils/commands.json', 'w') as commands:
                commands.truncate()
                json.dump(save, commands, indent=4)
            msg = await ctx.send('Error, seomthing went wrong. Exception: ``%s``' % e)

        # Update commands.json
        with open('cogs/utils/commands.json', 'w') as commands:
            commands.truncate()
            json.dump(cmds, commands, indent=4)
        await ctx.message.delete()
        await asyncio.sleep(2)
        await msg.delete()

    # Remove a custom command
    @commands.command()
    async def remove(self, ctx, *, msg: str):
        words = msg.strip()

        with open('cogs/utils/commands.json', 'r') as commands:
            cmds = json.load(commands)
            save = cmds

        try:

            # If there are quotes in the message (meaning multiple words for each param)
            success = False
            if '"' in words:
                entry = re.findall('"([^"]+)"', words)

                # Item for key is list
                if len(entry) == 2:

                    # Key exists
                    if entry[0] in cmds:
                        for i in cmds[entry[0]]:
                            if entry[1] == i[0]:
                                cmds[entry[0]].remove(i)
                                msg = await ctx.send('Successfully removed ``%s`` from ``%s``' % (entry[1], entry[0]))
                                success = True
                    else:
                        if entry[0] in cmds:
                            del cmds[entry[0]]
                            success = True
                            msg = await ctx.send('Successfully removed ``%s`` from ``%s``' % (entry[1], entry[0]))

                # Item for key is string
                else:
                    if entry[0] in cmds:
                        oldValue = cmds[entry[0]]
                        del cmds[entry[0]]
                        success = True
                        msg = await ctx.send('Successfully removed ``%s`` from ``%s``' % (oldValue, entry[0]))

            # No quotes so spaces seperate params
            else:

                # Item for key is list
                if len(words.split(' ')) == 2:
                    entry = words.split(' ')

                    # Key exists
                    if entry[0] in cmds:
                        for i in cmds[entry[0]]:
                            if entry[1] == i[0]:
                                cmds[entry[0]].remove(i)
                                msg = await ctx.send('Successfully removed ``%s`` from ``%s``' % (entry[1], entry[0]))
                                success = True
                    else:
                        if entry[0] in cmds:
                            del cmds[entry[0]]
                            success = True
                            msg = await ctx.send('Successfully removed ``%s`` from %``s``' % (entry[1], entry[0]))

                # Item for key is string
                else:
                    entry = words.split(' ', 1)
                    if entry[0] in cmds:
                        oldValue = cmds[entry[0]]
                        del cmds[entry[0]]
                        success = True
                        msg = await ctx.send('Successfully removed ``%s`` from ``%s``' % (oldValue, entry[0]))

            if not success:
                msg = await ctx.send('Could not find specified command.')

        except Exception as e:
            with open('cogs/utils/commands.json', 'w') as commands:
                commands.truncate()
                json.dump(save, commands, indent=4)
            msg = await ctx.send('Error, something went wrong. Exception: ``%s``' % e)

        # Update commands.json
        with open('cogs/utils/commands.json', 'w') as commands:
            commands.truncate()
            json.dump(cmds, commands, indent=4)
        await ctx.message.delete()
        await asyncio.sleep(2)
        await msg.delete()


def setup(bot):
    bot.add_cog(Customcmds(bot))
