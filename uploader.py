import os
import io
import cv2
import base64
import random
from PIL import Image
from request import HTTPrequest
from RubikaBot import rubika
from mutagen.mp3 import MP3


rb = rubika()


def get_thumb(img:cv2.Mat):
    h, w, c = img.shape
    img = cv2.resize(img, (w // 3, h // 3))
    return img

def get_video_data(filename):
    video = cv2.VideoCapture(filename)

    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    duration = int(frame_count / fps)

    video.set(cv2.CAP_PROP_POS_FRAMES, 0)
    _, first_frame = video.read()
    thumbnail = cv2.imencode('.png', get_thumb(first_frame))[1].tobytes()
    
    video.release()

    return height, width, duration, thumbnail


def get_image_size(file_name) -> list[int]:
    try:
        with Image.open(file_name) as img:
            return list(img.size)
    except Exception as e:
        print(f"Error opening the image file: {e}")
        return []
        
def get_thumbnail(file_name) -> str:
    try:
        with Image.open(file_name) as image:
            image.thumbnail((40, 40))
            changed_image = io.BytesIO()
            image.save(changed_image, format='png')
            return base64.b64encode(changed_image.getvalue()).decode()
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return ""

def base64_decode(data_text: str) -> str:
    return base64.decodebytes(data_text.encode()).decode()

def get_music_time(path_music: str):
    try:
        audio = MP3(path_music)
        return int(audio.info.length)
    except Exception as e:
        print(f"Error getting music time: {e}")
        return 0

def base64_encode(data_text: str) -> str:
    return base64.encodebytes(data_text.encode()).decode()

def delete_empty(text: str) -> str:
    return text.strip()


def upload(data: dict):
    file_type = [
            'music',
            'voice',
            'video',
            'file',
        ]
    try:
        mode_send = data.get('mode')
        target_guid = data.get('guid')
        file_name = data.get('filename')
        music_per = data.get('singer')
        data_msg_id = data['data_msg_id']
        my_guid = data['t_guid']
        caption = data.get('caption')
        
        
        rand_int = random.randint(1, 100)
        file_name_tmp = f"{rand_int}-{file_name}"
        if target_guid is None:
            rb.send_message(my_guid, 'لطفا از صحت نگارش guid مقصد مطمئن شوید', data_msg_id)
            return

        if mode_send is None or mode_send not in file_type:
            rb.send_message(my_guid, 'لطفا از صحت نگارش mode و یا مقدار آن اطمینان حاصل کنید.', data_msg_id)
            return
        
        data_msg = rb.get_message_by_id(my_guid, [data_msg_id])[0]
        data_text = str(data_msg.get('text', ''))

        if data_text and delete_empty(data_text).startswith("http") and 'file_inline' not in data_msg:
            http = HTTPrequest(data_text)
            file_size = http.buffer_size
            if file_size is None or http.response_code != 200:
                raise Exception('Error in base http')
            
            if mode_send == 'music' and not music_per:
                rb.send_message(my_guid, 'برای ارسال آهنگ لازم است نام خواننده را هم وارد کنید\n برای مثال:\n singer : Reza Bahram', data_msg_id)
                return
            
            else:
                size_format_file = rb.sizeFormat(file_size)
                replay_msg = rb.send_message(my_guid, f'درحال دانلود فایل از اینترنت ⬇️\nحجم فایل: {size_format_file}', data_msg_id)
                repey_msg_id = replay_msg['message_update']['message_id']

                http.download(file_name_tmp)

        elif 'file_inline' in data_msg:
            msg_file_data = data_msg['file_inline']    
            if not file_name:
                file_name = msg_file_data['file_name']

            size_format_file = rb.sizeFormat(msg_file_data['size'])

            replay_msg = rb.send_message(my_guid, f"درحال دانلود فایل ⬇️\nحجم فایل: {size_format_file}", data_msg_id)
            repey_msg_id = replay_msg['message_update']['message_id']
                  
            file_size = rb.download(msg_file_data, file_name_tmp)
        else:
            rb.edit_message(my_guid, 'دانلود فایل با خطا مواجه شد!', data_msg_id)
            raise Exception('File error')

        try:
            rb.edit_message(my_guid, f'درحال آپلود فایل ⬆️\nحجم فایل: {size_format_file}', repey_msg_id)
            upload_data = rb.upload_file(file_name_tmp)

            handlers = {
                'music': rb.send_music,
                'voice': rb.send_voice,
                'video': rb.send_video,
                'file': rb.send_document,
            }

            if mode_send in handlers:
                handler = handlers[mode_send]
     
                if mode_send == 'music':
                    if 'file_inline' in data_msg and msg_file_data['type'] != "File":
                        music_time = msg_file_data['time']
                    else:
                        music_time = get_music_time(file_name_tmp)
            
                    handler(target_guid, music_time, upload_data, file_size, file_name, music_per, caption)

                elif mode_send == 'voice':
                    if 'file_inline' in data_msg and msg_file_data['type'] != "File":
                        music_time = msg_file_data['time']
                    else:
                        music_time = get_music_time(file_name_tmp)*1000

                    handler(target_guid,upload_data,file_name,file_size,music_time, caption)

                elif mode_send == 'video':
                    if 'file_inline' in data_msg and msg_file_data['type'] != "File":
                        thumb_str = msg_file_data['thumb_inline']
                        width = msg_file_data['width']
                        height = msg_file_data['height']
                        duration = int(msg_file_data['time']/1000)
                    else:
                        duration, height , width , thumb_bytes = get_video_data(file_name_tmp)
                        thumb_str = base64.encodebytes(thumb_bytes).decode()

                    handler(target_guid,upload_data,file_name,height,width,file_size,thumb_str,duration,caption)

                else: # file upload
                    handler(target_guid, upload_data, file_size, file_name,caption)

                os.remove(file_name_tmp)
                rb.edit_message(my_guid, f'{mode_send.capitalize()} ارسال شد ✅', repey_msg_id)

            else:
                rb.edit_message(my_guid, "از صحت نوع فایل در آپشن mode اطمینان حاصل کنید.", repey_msg_id)
            
        except Exception as e:
            print(f"Error in handling {mode_send}: {e}")

    except Exception as e:
        try:
            os.remove(file_name_tmp)
        except Exception as remove_error:
            print(f"Remove file error: {remove_error}")
        
        print(f"Error in upload: {e}")
        rb.send_message(my_guid, """
لطفاً موارد زیر را بررسی فرمایید:

1. صحت نوع فایل در آپشن mode
2. پیامی که روی آن ریپلای شده است          
3. صحت نگارشی آپشن‌های وارد شده:
guid، mode، filename، singer
""",data_msg_id)

    finally:
        if os.path.isfile(file_name_tmp):
            os.remove(file_name_tmp)