import os,discord,pytube
from dotenv import load_dotenv
from mega import Mega
import threading
import time

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#processes
client = discord.Client()
mega = Mega()

new_mega = mega.login(os.getenv('MEGA_USR'), os.getenv('MEGA_PWD'))

#global required variables
time_limit = 600
delete_time = 3600   

@client.event
async def on_ready():
    print(f'{client.user} has connected!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return 

    clean_content = message.content.split(' ')

    if clean_content[0] == "!ping": #respond command to test bot
        
        await message.reply("PONG")

    if clean_content[0] == "!get": #Get complete video (!get link) 
        
        try: 
            yt = pytube.YouTube(clean_content[1])

            if yt.length > time_limit:
                await message.channel.send(f"Length of given video exceeds {time_limit//60} minutes, which is currently unsupported.")
                return 

            get_func_thread = threading.Thread(target=get_func, args=(message, yt))
            get_func_thread.start()

            return       

        except:
            await message.reply("Some error occured :(")
            return

    if clean_content[0] == "!clip": #Get clipped video (!clip link start end)
        
        if os.path.isfile(f"./videos/down_{message.author}"):
            await message.channel.send(f"Previous file is still being processed, please wait till it is processed.")
            return
            
        try:
            yt = pytube.YouTube(clean_content[1])

            start_time = clean_content[2]
            end_time = clean_content[3]

            if start_time == "" or end_time == "":
                await message.channel.send(f"wrong format, format is : '!clip [yt_link] [start_time in seconds] [end_time in seconds]'")
                return 

            if int(start_time) > int(end_time):
                await message.channel.send(f"start_time is greater than end_time")
                return 
            
            if int(start_time) > yt.length or int(end_time) > yt.length:
                await message.channel.send(f"start_time or end_time is greater than length of the video, length of the video is {yt.length}")
                return 
            
            if int(start_time) < 0 or int(end_time) < 0:
                await message.channel.send(f"start_time or end_time is negative")
                return 
            
            if yt.length > time_limit:
                await message.channel.send(f"Length of given video exceeds {time_limit//60} minutes, which is currently unsupported.")
                return 

            clip_func_thread = threading.Thread(target=clip_func, args=(message, yt, start_time, end_time))
            clip_func_thread.start()

            return

        except:
            await message.channel.send(f"Some error occured :(")
            return

def delete_file_func(file):
    time.sleep(delete_time)
    new_mega.delete(f"{new_mega.get_id_from_obj(file)}")

def get_func(message,yt):

    yt.streams.get_highest_resolution().download(output_path="./videos",filename=f"down_{message.author}")

    main_folder = new_mega.find('discord_videos')
    file = new_mega.upload(f"./videos/down_{message.author}", main_folder[0])
    os.remove(f"./videos/down_{message.author}")

    client.loop.create_task(message.reply(f"File is only valid for {delete_time//3600} hour(s), link : {new_mega.get_upload_link(file)}"))

def clip_func(message, yt, start_time, end_time):
    yt.streams.get_highest_resolution().download(output_path="./videos",filename=f"down_{message.author}")
    os.system(f"ffmpeg -i ./videos/down_{message.author} -ss {start_time} -to {end_time} ./videos/down_{message.author}_temp.mp4")

    main_folder = new_mega.find('discord_videos')
    
    file = new_mega.upload(f"videos/down_{message.author}_temp.mp4", main_folder[0])

    os.remove(f"./videos/down_{message.author}")
    os.remove(f"./videos/down_{message.author}_temp.mp4")
    
    delete_thread = threading.Thread(target=delete_file_func, args=(file))
    delete_thread.start()

    client.loop.create_task(message.reply(f"File is only valid for {delete_time//3600} hour(s), link : {new_mega.get_upload_link(file)}")) 

client.run(TOKEN)