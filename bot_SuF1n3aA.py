import time
import _thread
from RubikaBot import rubika
import uploader


rb = rubika()

def load_guids(file_path="./guids.txt"):
    guids_dict = {}

    with open(file_path, "r") as f:
        guids_content = f.read().replace("\r", "").split("\n")

    for guid_line in guids_content:
        guid_line = guid_line.strip()
        if len(guid_line) > 20:
            guids_dict[guid_line] = "1"

    return guids_dict

my_guids = load_guids()


def on_message(message: dict, guid):
    client_msg = message["text"].replace("\r", "")
    msg_id = message["message_id"]

    if client_msg.startswith('/upload\n') and 'reply_to_message_id' not in message:
        rb.send_message(guid, 'لطفاً روی فایل یا آدرس مورد نظر برای آپلود، ریپلای بزنید', reply=msg_id)
        return
    
    if client_msg.startswith('/upload\n'):
        client_msg = client_msg.split('\n')[1:]

        data = {}
        is_caption = False
        caption_value = ''
        for i in client_msg:
            if not is_caption and i == '':
                continue
            
            if 'caption' in i.lower():
                caption_value = i.split(":")[1].strip()+"\n"
                is_caption = True

            elif is_caption:
                caption_value += i.strip()+"\n"

            else:
                key, value = map(str.strip, i.split(':'))
                data[key] = value

        data['caption'] = caption_value
        data['t_guid'] = guid
        data["data_msg_id"] = message['reply_to_message_id']
        _thread.start_new_thread(uploader.upload,(data,))

    elif client_msg.startswith('/start'):
        rb.send_message(guid,"""
active ✅

برای دیدن راهنما help/ را ارسال کنید""",reply=msg_id)
    
    elif client_msg.startswith('/help'):
        rb.send_message(guid,"""
به منظور استفاده از ربات، حتما به برخی نکات توجه فرمایید:

برای آپلود، در ابتدای پیام خود upload/ را ارسال نموده و پس از آن در خط بعدی، آپشن‌های مربوطه را به ربات اعلام کنید.

توجه داشته باشید که برخی از آپشن‌ها اختیاری هستند، در حالی که برخی دیگر باید حتما استفاده شوند.

به عنوان مثال:

آپشن mode برای تعیین نوع فایل استفاده می‌شود. حتماً مقدار این آپشن باید با توجه به نوع فایل شما مشخص گردد.

انواع فایل : file, video, music, voice 
مثال:
mode : video

آپشن guid یکی دیگر از آپشن‌های لازم برای آپلود است. در این آپشن، باید GUID کانال یا گروه مورد نظر برای آپلود فایل را وارد نمایید. به عنوان مثال:
guid : c0Bx3EV0835316b092410e6b4bb4b70z

در آپشن filename ، نام فایل مورد نظر را وارد کنید. اگر مود فایل شما file باشد، این نام به عنوان نام فایل در زمان ارسال ذخیره خواهد شد.

آپشن singer نیز باید حتماً در صورتی که نوع فایل موزیک باشد، وارد شود و نام خواننده موزیک را در آن مشخص کنید.
مثال:
singer : Reza Bahram

آپشن caption, این اپشن باید حتماا اخرین آپشنی باشد که انتخاب میکنید و میتوانید متنی که میخواهید برای پست مدنظرتان استفاده شود را بعد از ان قرار دهید
مثال:
caption:
#یوتیوب 

پشت صحنه کلیپ 

➣ツ @you_chanel ♡
""",reply=msg_id)

def process_chats():
    for chat in rb.get_chats():
        object_guid = chat['object_guid']

        if object_guid in my_guids:
            last_message = chat['last_message']
            my_guids[object_guid] = last_message['message_id']

def check_messages():
    while True:
        time.sleep(5)

        for guid, last_message_id in my_guids.items():
            try:
                msgs = rb.get_message(guid, to_max=True, min_id=last_message_id)

                if msgs and msgs[0]['message_id'] == last_message_id:
                    del msgs[0]
                    time.sleep(5)

                for msg in msgs:
                    my_guids[guid] = msg['message_id']

                    if 'text' in msg and msg['text']:
                        try:
                            on_message(msg, guid)
                            time.sleep(2)
                        except Exception as e:
                            rb.send_message(guid, 'به گذاشتن : بعد از آپشن توجه کنید', reply=msg['message_id'])
            except Exception as e:
                rb.send_message(guid, 'لطفا از صحیح بودن GUID مطمئن شوید', reply=msg['message_id'])
                print('guid error: ', e)

#  process_chats
process_chats()
# check messages if new....
check_messages()
