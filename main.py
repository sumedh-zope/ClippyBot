from hashlib import new
from logging import error
import os,discord,pytube
from dotenv import load_dotenv
from mega import Mega

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

mega = Mega()
new_mega = mega.login(os.getenv('MEGA_USR'), os.getenv('MEGA_PWD'))

@client.event
async def on_ready():
    print(f'{client.user} has connected!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return 

    clean_content = message.content.split(' ')

    if clean_content[0] == "!clip":
        
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
            
            if yt.length > 1500:
                await message.channel.send(f"Length of given video exceeds {yt.length//60} minutes, which is currently unsupported.")
                return 
                
            yt.streams.get_highest_resolution().download(output_path="./videos",filename=f"down_{message.author}")
            os.system(f"ffmpeg -i ./videos/down_{message.author} -ss {start_time} -to {end_time} ./videos/down_{message.author}_temp.mp4")

            main_folder = new_mega.find('discord_videos')
            
            file = new_mega.upload(f"videos/down_{message.author}_temp.mp4", main_folder[0])

            await message.channel.send(f"{new_mega.get_upload_link(file)}")

            os.remove(f"./videos/down_{message.author}")
            os.remove(f"./videos/down_{message.author}_temp.mp4")

        except:
            await message.channel.send(f"Some error occured :(")
            return

        await message.channel.send(f"clipped")
    
client.run(TOKEN)