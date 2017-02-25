import os
import subprocess
import traceback

while True:
    try:
        if os.path.isfile('quit.txt'):
            os.remove('quit.txt')
            break
        p = subprocess.call(['python3', 'selfbot.py'])
    except:
        traceback.print_exc()
