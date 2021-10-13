import requests
import datetime as dt
from datetime import timedelta
import urllib.request
import sys
import os

# global variables:
game_name = ''

# auth stuff for TwitchAPI
# a local token is generated each time you need to access the Twitch API, which is what the below is doing
def get_headers():
    auth_body = {
        "client_id": "TOKEN HERE",
        "client_secret": "TOKEN HERE",
        "grant_type": "client_credentials"
    }
    
    temp = requests.post("https://id.twitch.tv/oauth2/token", auth_body)
    temp_json = temp.json()
    acc_token = temp_json["access_token"]

    headers = {
        "Client-ID": "TOKEN HERE",
        "Authorization": f"Bearer {acc_token}"
    }
    return headers


# path of where the clips will be downloaded to your computer, can change
basepath = 'tmp\\'  # tmp\ will create a temporary inside the virtual environment to hold these downloaded files


# progress of each downloaded clip, not needed
def dl_progress(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write("\r...%d%%" % percent)
    sys.stdout.flush()


def initialize_clips():

    # getting the dates of today and yesterday in order clips from the past day
    today = dt.date.today()  # - timedelta(days=2)
    yesterday = dt.date.today() - timedelta(days=1)
    # tstring = f"{today}T00:00:00Z"
    begin = f"{yesterday}T00:00:00Z"
    end = f"{yesterday}T23:59:59Z"
    headers = get_headers()

    # this will store any info needed to edit into the video
    video_info = []

    # request top clips from whatever game, needs gameid, can change how many clips to search for after the 'first' parameter
    # Guilty Gear Strive id: 517159
    # Paladins id: 491115
    
    
    # Search for the game you would like!
    game_input = input('Please enter the name of the game you want the id for: ')
    game_input.replace(' ', '%20')
    game_info = requests.get(f"https://api.twitch.tv/helix/games?name={game_input}", headers=headers)
    game_json = game_info.json()
    try:
        game_id, game_name = game_json['data'][0]['id'], game_json['data'][0]['name']
    except IndexError as e:
        print('Please rerun the program and enter a valid game name.')
        exit()

    clips = requests.get(
        f"https://api.twitch.tv/helix/clips?game_id={game_id}&first=40&started_at={begin}&ended_at={end}",
        headers=headers)  # top of yesterday
    
    # clips = requests.get(
    #     f"https://api.twitch.tv/helix/clips?game_id=491115&first=10",
    #     headers=headers) # top all time
    
    clips_json = clips.json()
    print('downloading clips...')
    title = clips_json['data']
    for clip in clips_json['data']:
        if clip['duration'] > 4:  # only take clips over however many seconds, obv can be changed
            out_filename = clip['id'] + '.mp4'
            mp4_url = clip['thumbnail_url'].split("-preview", 1)[0] + '.mp4'  # url of video download
            video_info.append({'video_file': out_filename, 'streamer': clip['broadcaster_name']})  # any other information from the streamer would be stored in this array
            # print(f'\ncurrently downloading: {mp4_url}')

            output_path = basepath + out_filename

            if not os.path.exists(basepath):
                os.makedirs(basepath)

            try:
                urllib.request.urlretrieve(mp4_url, output_path, reporthook=dl_progress)
            except:
                print("An exception occurred")
    return video_info

# print(f'\n{video_info}')



