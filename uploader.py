import os
from RubikaBot import rubika
import cv2
import base64
from request import HTTPrequest
import base64
import traceback
import io
import PIL.Image
from mutagen.mp3 import MP3


rb = rubika()


def get_thumb(img:cv2.Mat):
    h, w, c = img.shape
    img = cv2.resize(img, ( int(w/3) , int(h/3) ) )
    return img
def get_video_data(filename):
    video = cv2.VideoCapture(filename)
    width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = video.get(cv2.CAP_PROP_FPS)
    duration = int(frame_count / fps)
    video.set(cv2.CAP_PROP_POS_FRAMES,0)
    im_png = cv2.imencode('.png', get_thumb(video.read()[1]))[1]
    return duration, int(height) , int(width) , im_png.tobytes()
def getImageSize(file_name) -> list[int]:
    return list(PIL.Image.open(file_name).size)
def get_thumbnail(file_name) -> str:
    image = PIL.Image.open(file_name)
    image.thumbnail((40, 40))
    changed_image = io.BytesIO()
    image.save(changed_image,format='png')
    return base64.b64encode(changed_image.getvalue()).decode()
def base64_decode(data_text:str):
    return base64.decodebytes(data_text.encode()).decode()
def get_music_time(path_music) -> int:
    return int(MP3(path_music).info.length)


def base64_encode(data_text:str):
    return base64.encodebytes(data_text.encode()).decode()


def delete_empty(text:str):
    while text.endswith(" "):
        text = text[:-1]
    while text.startswith(" "):
        text = text[1:]
    return text


def upload(data:dict):
    try:
        mode_send:str = data['mode']
        print(data)
        file_name = (data['file_name'] if 'file_name' in data else None)
        target_guid = (data['target'] if 'target' in data else None)
        music_per = (data['music_per'] if 'music_per' in data else None)
        data_msg_id = data['data_msg_id']
        my_guid = data['t_guid']    

        data_msg = rb.get_message_by_id(my_guid,[data_msg_id])[0]
        data_text = str(data_msg['text'] if 'text' in data_msg else "")
        
        if data_text and delete_empty(data_text).startswith("http") and 'file_inline' not in data_msg:
            http = HTTPrequest(data_text)
            file_size = http.buffer_size
            if file_size == None or http.response_code != 200:
                raise Exception('error in base http')
            
            if mode_send == 'music' and not music_per:
                rb.send_message(my_guid,'برای ارسال آهنگ لازم است نام خواننده را هم وارد کنید\n برای مثال:\n music_per : Reza Bahram',data_msg_id)
                return
            else: 
                rb.send_message(my_guid,'درحال دانلود فایل از اینترنت ⬇️',data_msg_id)
                http.download(file_name)
        elif 'file_inline' in data_msg:
            msg_file_data = data_msg['file_inline']
            if not file_name:
                file_name = msg_file_data['file_name']
            rb.send_message(my_guid,'درحال دانلود فایل ⬇️',data_msg_id)
            file_size = rb.download(msg_file_data,file_name)
        else:
            rb.send_message(my_guid,f'دانلود فایل با خطا مواجه شد !',data_msg_id)
            raise Exception('file error')
        rb.send_message(my_guid,'درحال آپلود فایل ⬆️',data_msg_id)
        
        upload_data = rb.upload_file(file_name)
        
        if mode_send.startswith('music'):
            if 'file_inline' in data_msg and msg_file_data['type'] != "File":
                music_time = msg_file_data['time']
            else:
                music_time = get_music_time(file_name)
            
            if not music_per:
                rb.send_message(my_guid,'برای ارسال آهنگ لازم است نام خواننده را هم وارد کنید\n برای مثال:\n music_per : Reza Bahram',data_msg_id)
            if music_per:
                rb.send_music(target_guid,int(music_time),upload_data,file_size,file_name,music_per)
                os.remove(file_name)
                rb.send_message(my_guid,'آهنگ ارسال شد ✅',data_msg_id)
            return
        elif mode_send.startswith('voice'):
            if 'file_inline' in data_msg and msg_file_data['type'] != "File":
                music_time = msg_file_data['time']
            else:
                music_time = get_music_time(file_name)*1000
            rb.send_voice(target_guid,upload_data,file_name,file_size,music_time)
            os.remove(file_name)
            rb.send_message(my_guid,'ویس ارسال شد ✅',data_msg_id)
            return
        elif mode_send.startswith('video'):
            if 'file_inline' in data_msg and msg_file_data['type'] != "File":
                thumb_str = msg_file_data['thumb_inline']
                width = msg_file_data['width']
                height = msg_file_data['height']
                duration = int(msg_file_data['time']/1000)
            else:
                duration, height , width , thumb_bytes = get_video_data(file_name)
                thumb_str = base64.encodebytes(thumb_bytes).decode()
            rb.send_video(target_guid,upload_data,file_name,height,width,file_size,thumb_str,duration)
            os.remove(file_name)
            rb.send_message(my_guid,'ویدیو ارسال شد ✅',data_msg_id)
            return
        elif mode_send.startswith('file'):
            rb.send_document(target_guid,upload_data,file_size,file_name)
            os.remove(file_name)
            rb.send_message(my_guid,'فایل ارسال شد ✅',data_msg_id)
            return
        else:
            raise Exception('mode error')
    except Exception as e:
        try:
            os.remove(file_name)
        except:
            print("remove file error:", e)
        try:
            rb.send_message(my_guid, f"نوع فایل رو اشتباه وارد کردید، لطفا از صحیح بودن mode فایل مطمئن شوید {e}",data_msg_id)
        except:
            print("upload file error:", e)
        traceback.print_exc()