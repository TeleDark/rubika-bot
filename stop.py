import os
from colorama import Fore, Style

GREEN = Fore.GREEN
PLAIN = Style.RESET_ALL


def find_bot_file():
    for file in os.listdir():
        if file.endswith(".py") and file.startswith("bot_"):
            return file
    return None

def stop_bot(file_name):
    process_lines = os.popen("ps -ef").read().split("\n")
    for line in process_lines:
        if file_name in line:
            columns = line.split()
            prc_id_index = columns[1]
            try:
                prc_id = int(prc_id_index)
                os.system(f"kill -9 {prc_id}")
            except ValueError:
                print(f"Error: Invalid process ID found in line: {line}")

def delete_media_files():
    media_extensions = {".mp3", ".mp4", ".mkv"}
    for file in os.listdir():
        if any(file.endswith(ext) for ext in media_extensions):
            os.remove(file)


def main():
    file_name = find_bot_file()

    if file_name:
        stop_bot(file_name)
        delete_media_files()
        print(f"{Style.BRIGHT}{GREEN}The bot has been stopped{PLAIN}")

if __name__ == "__main__":
    main()