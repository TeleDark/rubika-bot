import os
from colorama import Fore, Style

GREEN= Fore.GREEN
PLAIN = Style.RESET_ALL

def find_bot_file():
    for file in os.listdir():
        if file.endswith(".py") and file.startswith("bot_"):
            return file
    return None

def start_bot(file_name):
    os.popen(f'nohup python3 -u {file_name} > log.txt 2> error.log &')

def main():
    file_name = find_bot_file()
    if file_name:
        start_bot(file_name)
        print(f"{Style.BRIGHT}{GREEN}The bot has been started{PLAIN}")

if __name__ == "__main__":
    main()
