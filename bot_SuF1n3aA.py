import time
from RubikaBot import rubika
import uploader
import _thread


rb = rubika()


def delete_empty(text:str):
    while text.endswith(" "):
        text = text[:-1]
    while text.startswith(" "):
        text = text[1:]
    return text


my_guids = {
    
}


f= open("guids.txt","rb")
r = f.read().decode()
f.close()


for i in r.replace("\r","").split("\n"):
    if len(i) > 20:
        i = delete_empty(i)
        my_guids[i] = "1"


def on_message(message:dict,t_guid):
    msg_text:str = message["text"]
    msg_text = msg_text.replace("\r","")
    
    msg_id = message["message_id"]
    
    if msg_text.startswith('/upload\n'):
        if 'reply_to_message_id' not in message:
            rb.send_message(t_guid,'error !\nnot reply to file message !',reply=msg_id)
            return
        
        msg_text = msg_text.split('\n')
        del msg_text[0]
        data = {}
        for i in msg_text:
            i = i.split(' : ')
            data[delete_empty(i[0])] = delete_empty(i[1])
        data['t_guid'] = t_guid
        data["data_msg_id"] = message['reply_to_message_id']
        
        _thread.start_new_thread(uploader.upload,(data,))

    elif msg_text.startswith('/start'):
        rb.send_message(t_guid,"active ✅",reply=msg_id)


for chat in rb.get_chats():
    if chat['object_guid'] in my_guids:
        my_guids[chat['object_guid']] = chat['last_message']['message_id']


while True:
    time.sleep(10)
    for guid in my_guids:
        try:
            msgs = rb.get_message(guid,to_max=True,min_id=my_guids[guid])
            if len(msgs) > 0 and msgs[0]['message_id'] == my_guids[guid]:
                del msgs[0]
            for msg in msgs:
                my_guids[guid] = msg['message_id']
                if 'text' in msg and msg['text'] and len(msg['text']) > 0:
                    try:
                        on_message(msg,guid)
                    except:
                        rb.send_message(guid,'error',reply=msg['message_id'])
                    time.sleep(5)
        except Exception as e:
            rb.send_message(guid,'لطفا از صحیح بودن GUID مطمئن شوید',reply=msg['message_id'])
            print('guid error: ',e)