import requests
import RubikaBot
import json
import time
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import random

rb = RubikaBot.rubika('wydswubheyliypmlxvzxcjrjrwlbcgaa')


def send(data,method):
    js = {
        "method":method,"input":data,
        "client":RubikaBot.rubika_client
    }
    js = {
        "tmp_session":rb.auth,
        "data_enc":rb.encrypt(json.dumps(js)),
        "api_version":"6"
    }
    headers = {
        "Accept":"application/json; charset=UTF-8",
        "Content-Type":"application/json; charset=UTF-8",
        "User-Agent":"okhttp/3.12.1"
    }
    try_s = 0
    while try_s < 5:
        try:
            r= requests.post(
                "https://messengerg2c226.iranlms.ir/",
                json=js,
                headers=headers
            )
            if r.status_code == 200:
                return json.loads(rb.decrypt(r.json()['data_enc']))
        except:
            time.sleep(3)
def encode_char(input_str:str):
    output = ""
    for i in input_str:
        if i.isupper():
            c = chr(((29 - (ord(i) - ord('A'))) % 26) + 65)
        elif i.islower():
            c = chr(((32 - (ord(i) - ord('a'))) % 26) + 97)
        elif i.isdigit():
            c = chr(((13 - (ord(i) - ord('0'))) % 10) + 48)
        else:
            c = i
        output += c
    return output
def make_sign_in_public_key(public_key:RSA.RsaKey):
    public_key = base64.encodebytes(public_key.export_key('DER')).decode()
    public_key = encode_char(public_key)
    public_key = "-----BEGIN PUBLIC KEY-----\r\n" + encode_char(public_key) + "-----END PUBLIC KEY-----"
    public_key = base64.encodebytes(public_key.encode()).decode()
    return encode_char(public_key)
def generate_key():
    return RSA.generate(1024)
def generate_hash():
    a = "1234567890"
    r = ""
    for i in range(26):
        r += random.choice(a)
    return r


phone = input("phone (98912...) : ")


data = {
    "phone_number":phone,
    "send_type":"SMS"
}
res = send(data,"sendCode")
phone_code_hash = res['data']['phone_code_hash']


sign_code = input("code : ")


RsaKey = generate_key()


data = {
    "phone_number":phone,
    "phone_code":sign_code,
    "phone_code_hash":phone_code_hash,
    "public_key":make_sign_in_public_key(RsaKey.public_key())
}
res = send(data,"signIn")
res = res['data']

guid = res['user']['user_guid']

cipher = PKCS1_OAEP.new(RsaKey)
auth = res['auth']
auth = base64.decodebytes(auth.encode())
auth = cipher.decrypt(auth).decode()


account = {
    "auth":auth,
    "guid":guid,
    "private_key":RsaKey.export_key().decode()
}
f = open("account","wb")
f.write(json.dumps(account).encode())
f.close()


rb = RubikaBot.rubika()

data = {
    "token_type":"Firebase",
    "token":"",
    "app_version":"MA_3.3.3",
    "lang_code":"fa",
    "system_version":"SDK 29",
    "device_model":"Xiaomi",
    "device_hash":generate_hash(),
    "is_multi_account":False
}

res = rb.maker(data,"registerDevice")
print("ok")




