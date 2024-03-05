## rubika bot for upload file 

## Setup
```
apt update && apt install -y python3-pip ffmpeg libsm6 libxext6 && pip install -r requirements.txt
```
<hr>
</br>


### Login
```
python3 login.py
```
### Start
```
python3 start.py
```
### Stop
```
python3 stop.py
```
<hr>
</br>

## Options

### The way of giving instructions to the robot
##### Some options are optional, while others are necessary.

```
/upload
option : value
option...
```
##### When configuring the first option, you enter its name, then add a space, put a colon, add another space, and set its value. After that, go to the next line for the next option, ensuring that the specified spacing is maintained.


### This options is necessary

##### Different modes of file upload
```
mode : 
file , video , music , voice
```

##### You need to send the GUID of the channel, group, or private chat where you want the upload to occur. The bot's account must have message-sending access in that chat. For instance, if it's a channel, the bot should be an admin.
```
target : GUID
```

##### You should enter the file name along with its format. This option is necessary when your file source is a link. When your source is a forwarded file, meaning you forwarded a file to the bot, this option is optional
```
file_name : example.mp4
```

##### This option is the name of the singer. It is required when uploading music
```
music_per : Reza Bahram
```