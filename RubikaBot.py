from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
import json
import base64
import random
import requests
import time
import os

RUBIKA_CLIENT = {"app_name": "Main", "app_version": "3.3.3", "temp_code": "12", "lang_code": "fa", "package": "app.rbmain.a", "platform": "Android"}
ONE_KB = 1024
ONE_MB = ONE_KB * 1024
ONE_GB = ONE_MB * 1024
ONE_TB = ONE_GB * 1024

class rubika:
    def __init__(self,auth=None):
        self.auth = auth

        def replace_char_at(e, t, i):
            return e[0:t] + i + e[t + len(i):]
        
        def secret(e):
            t = e[0:8]
            i = e[8:16]
            n = e[16:24] + t + e[24:32] + i
            s = 0

            while s < len(n):
                char = n[s]
                if '0' <= char <= '9':
                    replacement = chr((ord(char) - ord('0') + 5) % 10 + ord('0'))
                    n = replace_char_at(n, s, replacement)
                else:
                    replacement = chr((ord(char) - ord('a') + 9) % 26 + ord('a'))
                    n = replace_char_at(n, s, replacement)
                s += 1
            return n
        
        
        if not auth:
            try:
                with open("account", "rb") as f:
                    self.account = json.loads(f.read().decode())
                self.auth = self.account.get('auth', None)
            except FileNotFoundError:
                print("Account file not found.")
            except json.JSONDecodeError:
                print("Error decoding JSON from the account file.")

        self.aes_key = bytearray(secret(self.auth), "UTF-8")
        self.aes_iv = bytearray.fromhex('00000000000000000000000000000000')
    
    def encrypt(self, text: str) -> str:
        raw = pad(text.encode('UTF-8'), AES.block_size)
        aes = AES.new(self.aes_key, AES.MODE_CBC, self.aes_iv)
        enc = aes.encrypt(raw)
        result = base64.b64encode(enc).decode('UTF-8')
        return result
    
    def decrypt(self, text:str) -> str:
        aes = AES.new(self.aes_key, AES.MODE_CBC, self.aes_iv)
        dec = aes.decrypt(base64.urlsafe_b64decode(text.encode('UTF-8')))
        result = unpad(dec, AES.block_size).decode('UTF-8')
        return result
    
    def encode_char(self,input_str:str):
        output = ""
        for char in input_str:
            if char.isupper():
                c = chr(((29 - (ord(char) - ord('A'))) % 26) + 65)
            elif char.islower():
                c = chr(((32 - (ord(char) - ord('a'))) % 26) + 97)
            elif char.isdigit():
                c = chr(((13 - (ord(char) - ord('0'))) % 10) + 48)
            else:
                c = char

            output += c

        return output
    
    def sizeFormat(self, size):
        if (size < ONE_KB):
            return "{:.0f}".format(size) + " بایت"
        elif (size < ONE_MB):
            return "{:.0f}".format(size / ONE_KB) + " کیلوبایت"
        elif (size < ONE_GB):
            return "{:.2f}".format(size / ONE_MB) + " مگابایت"
        elif (size < ONE_TB):
            return "{:.2f}".format(size / ONE_GB) + " گیگابایت"    

    def sign_data(self,data_enc:str):
        private_key = self.account['private_key'].encode()
        private_key = RSA.importKey(private_key)

        signer = PKCS1_v1_5.new(private_key)
        hash_obj = SHA256.new(data_enc.encode())
        signature = signer.sign(hash_obj)
        return base64.encodebytes(signature).decode().replace('\n',"")
    
    def maker(self, data: dict, method: str) -> dict:
        request_data = {
            "method": method,
            "input":data,
            "client": RUBIKA_CLIENT
        }

        data_enc = self.encrypt(json.dumps(request_data))
        auth_encoded = self.encode_char(self.auth)
        sing = self.sign_data(data_enc)

        request_payload = {
            "auth": auth_encoded,
            "data_enc": data_enc,
            "sign": sing,
            "api_version":"6"
        }

        response = self.send_req(json_data = request_payload)
        data_enc = response["data_enc"]

        if data_enc:
            data_json = json.loads(self.decrypt(data_enc))

        return data_json['data']
    
    def send_req(self, json_data: dict, max_attempts=5):
        
        headers = {
            "Accept": None,
            "Content-Type":"application/json; charset=UTF-8",
            "User-Agent":"okhttp/3.12.1"
        }

        for _ in range(max_attempts):
            try:
                response = requests.post('https://messengerg2c63.iranlms.ir',json=json_data, headers=headers, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    break
            except requests.exceptions.RequestException as e:
                print(f"Error in send_req: {e}")
                time.sleep(1)
        
        if not result or "data_enc" not in result:
            if result.get('status_det') == 'INVALID_AUTH' and max_attempts > 1:
                time.sleep(5)
                return self.send_req(json_data = json_data, max_attempts = max_attempts - 1)
        
        return result


    def _requestSendFile(self, file_name:str, size:int) -> dict:
        if size > 5000000:
                    size = 5000000        
        res = self.maker({"size": size, "mime": file_name.split('.')[-1], "file_name": file_name}, "requestSendFile")
        return res
    
    def send_document(self, chat_token: str, upload_data, file_size, file_name: str):
        file_inline = {
            "dc_id": upload_data["dc_id"],
            "file_id": str(upload_data["id"]),
            "type": "File",
            "file_name": file_name,
            "size": file_size,
            "mime": file_name.split('.')[-1],
            "access_hash_rec": upload_data["hash_rec"]
        }

        request_data = {
            "file_inline": file_inline,
            "object_guid": chat_token,
            "rnd": str(random.randint(10000,99999))
        }

        return self.maker(request_data, "sendMessage")
    
    def get_message_by_id(self, chat_token, message_id):
        request_data = {"message_ids": message_id,"object_guid": chat_token}
        return self.maker(request_data, "getMessagesByID")['messages']
    
    def send_video(self, chat_token, upload_data, file_name, height, width, size, thumb_inline, duration_sec):
        
        file_inline = {
            "access_hash_rec": upload_data["hash_rec"],
            "auto_play": False,
            "dc_id": upload_data["dc_id"],
            "file_id": str(upload_data["id"]),
            "file_name": file_name,
            "height": height,
            "mime": file_name.split(".")[-1],
            "size": size,
            "thumb_inline": thumb_inline,
            "time": duration_sec * 1000,
            "type": "Video",
            "width": width
        }

        request_data = {
            "file_inline": file_inline,
            "object_guid": chat_token,
            "rnd": str(random.randint(10000, 99999))
        }

        return self.maker(request_data, "sendMessage")
    

    def send_music(self,chat_token,duration_sec,upload_data,file_size,file_name,music_performer):
        file_inline = {
            "access_hash_rec": upload_data["hash_rec"],
            "auto_play": False,
            "dc_id": upload_data["dc_id"],
            "file_id": str(upload_data["id"]),
            "file_name": file_name,
            "music_performer": music_performer,
            "height": 0,
            "mime": "mp3",
            "size": file_size,
            "time": duration_sec,
            "type": "Music",
            "width": 0
        }

        request_data = {
            "file_inline": file_inline,
            "object_guid": chat_token,
            "rnd": str(random.randint(10000, 99999))
        }

        self.maker(request_data,"sendMessage")

    def send_message(self, chat_token, text, reply):
        request_data = {
            "text": text,
            "object_guid": chat_token,
            "rnd": str(random.randint(100000,900000))
        }

        if reply:
            request_data['reply_to_message_id'] = reply

        return self.maker(request_data, "sendMessage")
    
    def get_message(self, chat_token, to_max: bool = False, to_main: bool = False, min_id: str = "0", max_id: str = "0", limit: int = 50):
        request_data = {
            "object_guid": chat_token,
            "limit": limit,
            "min_id": min_id,
            "max_id": max_id
        }
        
        if to_max:
            request_data["sort"] = "FromMin"
        elif to_main:
            request_data["sort"] = "FromMax"

        messages = self.maker(request_data,"getMessages")['messages']

        return messages
    
    def forward_messages(self, from_chat_token, target_token, message_ids: list[str]):
        request_data = {
            "from_object_guid": from_chat_token,
            "message_ids": message_ids,
             "rnd": str(random.randint(100000, 900000)),
            "to_object_guid": target_token
            }
        
        return self.maker(request_data, "forwardMessages")
    
    def get_chats(self):
        response = self.maker({}, "getChats")
        return response['chats']
    

    def edit_message(self, chat_token, new_text, message_id):
        try:
            request_data = {
                "text":new_text,
                "object_guid": chat_token,
                "message_id":message_id
            }

            return self.maker(request_data,"editMessage")
        
        except Exception as e:
            print(f"edit {e}")
    
    def send_voice(self, chat_token: str, upload_data, file_name, file_size, duration_sec):
        file_inline = {
            "access_hash_rec": upload_data["hash_rec"],
            "auto_play": False,
            "dc_id": upload_data["dc_id"],
            "file_id": str(upload_data["id"]),
            "file_name": file_name,
            "height": 0,
            "mime": "mp3",
            "size": file_size,
            "time": duration_sec,
            "type": "Voice",
            "width": 0
        }
        request_data = {
            "file_inline": file_inline,
            "object_guid": chat_token,
            "rnd": str(random.randint(10000, 99999))
        }

        self.maker(request_data,"sendMessage")

    def download(self, file_data, file_name) -> bytes:
        download_url = f"https://messenger{file_data['dc_id']}.iranlms.ir/GetFile.ashx"
        file_size = int(file_data['size'])
        cbff = 0
        try_rc = 0
        ss = requests.Session()

        with open(file_name, 'wb') as file_stream:
            while cbff < file_size:
                headers = {
                    "Accept": None,
                    'Connection': "Keep-Alive",
                    "start-index": str(cbff),
                    "client-app-name": "Main",
                    'file-id': str(file_data['file_id']),
                    "last-index": str(cbff + 2000000),
                    "client-platform":  "Android",
                    "client-app-version":  "3.3.3",
                    'access-hash-rec': file_data['access_hash_rec'],
                    'auth': self.auth,
                    "client-package": "app.rbmain.a",
                    "Content-Type": "application/json",
                    "Content-Length": "0",
                    "User-Agent": "okhttp/3.12.1"
                }

                try:
                    res = ss.post(download_url, headers=headers, timeout=(10,10))
                    if res.status_code == 200:
                        bff = res.content
                        file_stream.write(bff)
                        cbff += len(bff)
                        try_rc = 0
                    
                except requests.RequestException as e:
                    try_rc += 1
                    if try_rc > 20:
                        raise e
                    
                    if try_rc > 0 and try_rc % 5 == 0:
                        ss.close()
                        ss = requests.Session()

                    time.sleep(3)

        return file_size
    

    def upload_file(self, file_name: str):
        file_size = os.path.getsize(file_name)
        file_stream = open(file_name,"rb")
        part_size = 2000000

        while True:
            try:
                upload_data = self._requestSendFile(file_name.split("/")[-1], file_size)
                break
            except Exception:
                time.sleep(5)
        
        c1 = int(file_size / part_size)
        total_part = (c1 if c1 * part_size == file_size else c1 + 1)
        
        header = {
            'auth': self.auth,
            'file-id': str(upload_data["id"]),
            'access-hash-send': upload_data["access_hash_send"],
            "total-part": str(total_part),
            'Accept': None,
            'User-Agent': 'okhttp/3.12.1',
            'Accept-Encoding': 'gzip',
            'Connection': "Keep-Alive",
            'Content-Type': 'application/octet-stream'
        }
        ss = requests.Session()

        for i in range(total_part):
            header["part-number"] = str(i + 1)
            part_bytes = file_stream.read(part_size)
            header["chunk-size"] = str(len(part_bytes))
            res = None
            try_send = 0
            is_error = False

            while True:
                try:
                    if i + 1 == total_part:
                        resp = ss.post(url= upload_data["upload_url"], headers=header, data=part_bytes)
                    else:
                        resp = ss.post(url=upload_data["upload_url"], headers=header, data=part_bytes,timeout=(10, 10))
                    
                    if resp.status_code == 200:
                        res = resp.json()
                        break
                    else:
                        raise Exception(resp.content.decode())
                
                except Exception as e:
                    print("Upload error : ",str(e))
                    time.sleep(2)
                    try_send += 1

                    if try_send > 10:
                        is_error = e
                        break

                    if try_send > 1 and i == 0:
                        is_error = e
                        break

            if is_error or res == None:
                file_stream.close()
                return self.upload_file(file_name)

            if "access_hash_rec" in (res.get("data") or {}):
                upload_data["hash_rec"] = res["data"]["access_hash_rec"]

        file_stream.close()
        return upload_data