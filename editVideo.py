import twitchClips
from moviepy.editor import *

import os

FFMPEG_BINARY = os.getenv('FFMPEG_BINARY', 'ffmpeg-imageio')
IMAGEMAGICK_BINARY = os.getenv('IMAGEMAGICK_BINARY', 'C:\\Program Files\\ImageMagick-7.0.8-Q16\\magick.exe')


def edit_video():
    headers = twitchClips.get_headers()
    basepath = twitchClips.basepath  # path of all the clips
    video_info = twitchClips.initialize_clips()  # info of clips paired with their respective mp4 names

    clip_arr = []

    # PLEASE NOTE! https://imagemagick.org/script/download.php is needed in order for moviepy to be able to work completely
    # For windows users: https://stackoverflow.com/questions/51928807/moviepy-cant-detect-imagemagick-binary-on-windows
    # if you are having issues after installing

    print('\nAdding text/resizing clips\n')
    for v in video_info:
        clip = VideoFileClip(basepath + v['video_file'])
        res = (clip.w, clip.h)
        print(res)
        if res != (1920, 1080):
            clip = clip.resize(width=1920, height=1080)
            # print(f'resizing from {res} to 1920,1080\n')
        # else:
            # print('already 1920x1080\n')
        text = TextClip(v['streamer'],
                        fontsize=50,
                        color='white',
                        stroke_color='black',
                        stroke_width=2,
                        font='Calibri-Bold')
        text = text.set_position((10, 15)).set_duration(clip.duration)
        video = CompositeVideoClip([clip, text])
        clip_arr.append(video)

    # for clip in clip_arr:
    #     clip.resize((1920, 1080))

    # transitioning: https://superuser.com/questions/931238/how-to-efficiently-and-automatedly-join-video-clips-using-short-transitions

    final_clip = concatenate_videoclips(clip_arr, method='chain')
    final_clip.write_videofile("edited_video.mp4", threads=8, codec='libx264')

