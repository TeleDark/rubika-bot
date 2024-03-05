import os

file_name = None
for i in os.listdir():
    if i.endswith(".py") and i.startswith("bot_"):
        file_name = i
        break

os.popen('nohup python3 -u '+file_name+' > out.txt 2> error.txt &')