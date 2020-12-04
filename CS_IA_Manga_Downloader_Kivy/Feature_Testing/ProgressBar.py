from __future__ import unicode_literals
import os, requests
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.progressbar import MDProgressBar
from kivy.uix.screenmanager import Screen, ScreenManager

from tqdm import tqdm

def mainKV():
    KV = '''
    BoxLayout:
        padding: "10dp"

        MDProgressBar:
            value: 50
    '''


    class Test(MDApp):
        def build(self):
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "Pink"
            screen = Screen(name="1")
            self.x = MDProgressBar(value=50, color=self.theme_cls.a)
            screen.add_widget(self.x)

            print(self.x.color, "op co")
            
            #return Builder.load_string(KV)
            return screen


    Test().run()

mainKV()

"""
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
"""