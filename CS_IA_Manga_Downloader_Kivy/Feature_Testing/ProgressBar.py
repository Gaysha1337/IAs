from __future__ import unicode_literals
import os, requests, time
from kivy.lang import Builder
from kivy.clock import mainthread, Clock
from kivymd.app import MDApp
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.button import MDRaisedButton
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

        @mainthread
        def up(self, inst):
            for i in range(10):
                self.x.value += i
                time.sleep(1)
            time.sleep(2)
            self.x.value = 0
        def build(self):
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "Pink"
            screen = Screen(name="1")
            self.x = MDProgressBar(value=0, max=10)
            screen.add_widget(self.x)

            screen.add_widget(MDRaisedButton(text="Press ME", on_release=Clock.schedule_once(self.up)))

            

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