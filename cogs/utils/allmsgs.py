import json
import mimetypes

from random import randint

def quickcmds(message):

    if message == 'shrug':
        return '¯\_(ツ)_/¯', message
    elif message == 'flip':
        return '(╯°□°）╯︵ ┻━┻', message
    elif message == 'unflip':
        return '┬─┬﻿ ノ( ゜-゜ノ)', message
    elif message == 'lenny':
        return '( ͡° ͜ʖ ͡°)', message
    elif message == 'fite':
        return '(ง’̀-‘́)ง', message
    else:
        return None


def custom(prefix, content):

    message = content.lower().replace(prefix, '')
    success = False

    with open('cogs/utils/config.json') as f:
        config = json.load(f)
        with open('cogs/utils/commands.json', 'r') as f:
            commands = json.load(f)
        for i in commands:
            if i.lower() in message.split():
                success = True
                if type(commands[i]) is list:
                    try:
                        if message[len(i) + 1:].isdigit():
                            index = int(message.content[len(i) + 1:].strip())
                        else:
                            title = message[len(i) + 1:]
                            for b, j in enumerate(commands[i]):
                                if j[0] == title.strip():
                                    index = int(b)
                                    break
                        mimetype, encoding = mimetypes.guess_type(commands[i][index][1])
                        zwi = message.split(' ', 2)
                        if len(zwi) != 3:
                            zwi.append(' ')
                        if mimetype and mimetype.startswith('image'):
                            return 'embed', commands[i][index][1], zwi[len(zwi)-1], str(i) + ' ' + str(commands[i][index][0])
                        else:
                            return 'message', commands[i][index][1], zwi[len(zwi)-1], str(i) + ' ' + str(commands[i][index][0])
                    except:
                        index = randint(0, len(commands[i]) - 1)
                        mimetype, encoding = mimetypes.guess_type(commands[i][index][1])
                        zwi = message.split(' ', 2)
                        if len(zwi) != 3:
                            zwi.append(' ')
                        if mimetype and mimetype.startswith('image'):
                            return 'embed', commands[i][index][1], zwi[len(zwi)-1], str(i) + ' ' + str(commands[i][index][0])
                        else:
                            return 'message', commands[i][index][1], zwi[len(zwi)-1], str(i) + ' ' + str(commands[i][index][0])
                else:
                    mimetype, encoding = mimetypes.guess_type(commands[i])
                    zwi = message.split(' ', 1)
                    if len(zwi) != 2:
                        zwi.append(' ')
                    if mimetype and mimetype.startswith('image'):
                        return 'embed', commands[i], zwi[len(zwi)-1], str(i)
                    else:
                        return 'message', commands[i], zwi[len(zwi)-1], str(i)
    if success == True:
        return None
