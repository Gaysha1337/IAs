from __future__ import unicode_literals
import os, requests
from kivy.lang import Builder
from kivymd.app import MDApp

from tqdm import tqdm
"""
def mainKV():
    KV = '''
    BoxLayout:
        padding: "10dp"

        MDProgressBar:
            value: 50
    '''


    class Test(MDApp):
        def build(self):
            return Builder.load_string(KV)


    Test().run()
"""
def main_tqdm():
    print(__file__, "--file--")
    device_root_dir = os.path.abspath(pathlib.Path(os.path.expanduser("~")).drive)
    os.listdir()

#main_tqdm()


import youtube_dl

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(["https://www.youtube.com/watch?v=hF1sqWiqppE"])