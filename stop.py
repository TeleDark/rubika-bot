import os
from colorama import Fore, Style
GREEN = Fore.GREEN
PLAIN = Style.RESET_ALL

file_name = None
for i in os.listdir():
    if i.endswith(".py") and i.startswith("bot_"):
        file_name = i
        break


for i in os.popen("ps -ef").read().split("\n"):
    if file_name in i:
            prc_id = i = i[9:17]
            prc_id = int(prc_id)
            r = os.popen("kill -9 "+str(prc_id))


for i in os.listdir():
    if i.endswith(".mp3") or i.endswith(".mp4") or i.endswith(".mkv") or i.endswith(".mp3"):
        os.remove(i)

print(f"{Style.BRIGHT}{GREEN}The bot has been Stopped.\n{PLAIN}")