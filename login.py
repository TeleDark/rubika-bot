import time
import json
import base64
import secrets
import requests
import RubikaBot
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from colorama import Fore, Style

GREEN = Fore.GREEN
RED = Fore.RED
PLAIN = Style.RESET_ALL

rb = RubikaBot.rubika('wydswubheyliypmlxvzxcjrjrwlbcgaa')


def send(data, method):
    base_url = "https://messengerg2c226.iranlms.ir/"
    
    payload = {
        "method": method,
        "input": data,
        "client": RubikaBot.RUBIKA_CLIENT
    }

    data_peyload = {
        "tmp_session": rb.auth,
        "data_enc": rb.encrypt(json.dumps(payload)),
        "api_version": "6"
    }

    headers = {
        "Accept": "application/json; charset=UTF-8",
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "okhttp/3.12.1"
    }

    max_retries = 5
    for _ in range(max_retries):
        try:
            response = requests.post(
                base_url,
                json = data_peyload,
                headers=headers
            )

            if response.status_code == 200:
                decrypted_data = rb.decrypt(response.json()['data_enc'])
                return json.loads(decrypted_data)
            
        except requests.RequestException as e:
            print(f"Error: {e}")
            time.sleep(3)

    return None

def encode_char(input_str: str):
    output = ""
    for char in input_str:
        if char.isupper():
            encoded_char = chr((29 - (ord(char) - ord('A'))) % 26 + ord('A'))
        elif char.islower():
            encoded_char = chr((32 - (ord(char) - ord('a'))) % 26 + ord('a'))
        elif char.isdigit():
            encoded_char = chr((13 - (ord(char) - ord('0'))) % 10 + ord('0'))
        else:
            encoded_char = char
            
        output += encoded_char
    return output

def make_sign_in_public_key(public_key: RSA.RsaKey):
    der_encoded_key = base64.encodebytes(public_key.export_key('DER')).decode()
    encoded_key = encode_char(der_encoded_key)

    result_key = f"-----BEGIN PUBLIC KEY-----\r\n{encode_char(encoded_key)}-----END PUBLIC KEY-----"
    result_key = base64.encodebytes(result_key.encode()).decode()

    return encode_char(result_key)

def generate_key(key_size=1024):
    return RSA.generate(key_size)

def generate_hash(length=26):
    characters = "1234567890"
    random_hash = ''.join(secrets.choice(characters) for _ in range(length))
    return random_hash

def save_account_info(auth, user_guid, private_key):
    account = {
        "auth": auth,
        "guid": user_guid,
        "private_key": private_key
    }

    with open("account", "w") as file:
        json.dump(account, file)


def login():
    try:
        phone = input("phone (98912...) : ")

        data = {
            "phone_number": phone,
            "send_type": "SMS"
        }

        response = send(data, "sendCode")
        
        if response['data']['has_confirmed_recovery_email']:
            print(f"{Style.BRIGHT}{RED}Two-Setup Verification: True{PLAIN}")
            return

        phone_code_hash = response['data']['phone_code_hash']
        sign_code = input("code : ")

        rsa_key = generate_key()

        data = {
            "phone_number": phone,
            "phone_code": sign_code,
            "phone_code_hash": phone_code_hash,
            "public_key": make_sign_in_public_key(rsa_key.public_key())
        }

        response = send(data, "signIn")
        response_data = response['data']

        user_guid = response_data['user']['user_guid']

        cipher = PKCS1_OAEP.new(rsa_key)
        auth = response_data['auth']
        auth = base64.decodebytes(auth.encode())
        auth = cipher.decrypt(auth).decode()

        save_account_info(auth, user_guid, rsa_key.export_key().decode())

        rb = RubikaBot.rubika()

        data = {
            "token_type": "Firebase",
            "token": "",
            "app_version": "MA_3.3.3",
            "lang_code": "fa",
            "system_version": "SDK 29",
            "device_model": "Xiaomi",
            "device_hash": generate_hash(),
            "is_multi_account": False
        }

        rb.maker(data,"registerDevice")
        print(f"{Style.BRIGHT}{GREEN}You logged in{PLAIN}")

    except KeyError as ke:
        print(f"KeyError: {ke}")
    except ValueError as ve:
        print(f"ValueError: {ve}")
    
    except Exception as e:
        print(f"Login Error: {e}")

if __name__ == "__main__":
    login()