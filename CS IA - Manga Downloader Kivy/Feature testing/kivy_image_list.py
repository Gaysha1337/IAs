import os
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.gridlayout import GridLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout

from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.uix.button import MDIconButton, MDRectangleFlatIconButton
from kivy.uix.label import Label


from kivy.lang import Builder
from functools import partial


from kivymd.app import MDApp
from kivy.config import Config


import requests
import urllib.request


imgURL = "https://avt.mkklcdnv6.com/21/c/13-1583488508.jpg"
imgURL = "https://cdn-images-1.medium.com/max/800/1*RO3AhbppPUFJBZwt3gUW-A.png"



Config.set("network","useragent","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'")


req = urllib.request.Request(imgURL, headers={"User-Agent":Config.get("network","useragent")})

urllib.request.urlopen(req)


cover_display = '''

<MangaCoverTile@SmartTileWithLabel>
    size_hint_y: None
    height: "240dp"

ScrollView:
    MDGridLayout:
        cols: 3
        adaptive_height: True
        padding: dp(4), dp(4)
        spacing: dp(4)

        AsyncImage:
            source: "http://i.imgur.com/xWCzcwC.jpg"
            #source: "https://avt.mkklcdnv6.com/21/c/13-1583488508.jpg"


        MangaCoverTile:
            #source: "./KivyFiles/akeno_himejima.jpg"
            source: "https://avt.mkklcdnv6.com/21/c/13-1583488508.jpg"
            text: "Cat 1: cat-1.jpg"

        MangaCoverTile:
            source: "./KivyFiles/akeno_himejima.jpg"
            text: "Cat 2: cat-2.jpg"
            tile_text_color: app.theme_cls.accent_color

        MangaCoverTile:
            source: "./KivyFiles/akeno_himejima.jpg"
            text: "Cat 3: cat-3.jpg"
            tile_text_color: app.theme_cls.accent_color

'''

covers = ['https://rawdevart.com/media/comic/the-strongest-dull-princes-secret-battle-for-the-throne/covers/The_Strongest_Dull_Princes_Secret_Battle_for_the_Throne_1.jpg.320x320_q85.jpg', 'https://rawdevart.com/media/comic/kage-no-jitsuryokusha-ni-naritakute/covers/Kage_no_Jitsuryokusha_ni_Naritakute_1.jpg.320x320_q85.jpg', 'https://rawdevart.com/media/comic/hazure-skill-kage-ga-usui-o-motsu-guild-shokuin-ga-jitsuha-densetsu-no-ansatsusha/covers/Hazure_Skill_Kage_ga_Usui_1.jpg.320x320_q85.jpg', 'https://rawdevart.com/media/comic/kage-no-jitsuryokusha-ni-naritakute-shadow-gaiden/covers/Kage_no_Jitsuryokusha_ni_Naritakute_Shadow_Gaiden_1.jpg.320x320_q85.jpg'] + ['https://rawdevart.com/media/comic/the-strongest-dull-princes-secret-battle-for-the-throne/covers/The_Strongest_Dull_Princes_Secret_Battle_for_the_Throne_1.jpg.320x320_q85.jpg', 'https://rawdevart.com/media/comic/kage-no-jitsuryokusha-ni-naritakute/covers/Kage_no_Jitsuryokusha_ni_Naritakute_1.jpg.320x320_q85.jpg', 'https://rawdevart.com/media/comic/hazure-skill-kage-ga-usui-o-motsu-guild-shokuin-ga-jitsuha-densetsu-no-ansatsusha/covers/Hazure_Skill_Kage_ga_Usui_1.jpg.320x320_q85.jpg', 'https://rawdevart.com/media/comic/kage-no-jitsuryokusha-ni-naritakute-shadow-gaiden/covers/Kage_no_Jitsuryokusha_ni_Naritakute_Shadow_Gaiden_1.jpg.320x320_q85.jpg'] + ['https://rawdevart.com/media/comic/the-strongest-dull-princes-secret-battle-for-the-throne/covers/The_Strongest_Dull_Princes_Secret_Battle_for_the_Throne_1.jpg.320x320_q85.jpg', 'https://rawdevart.com/media/comic/kage-no-jitsuryokusha-ni-naritakute/covers/Kage_no_Jitsuryokusha_ni_Naritakute_1.jpg.320x320_q85.jpg', 'https://rawdevart.com/media/comic/hazure-skill-kage-ga-usui-o-motsu-guild-shokuin-ga-jitsuha-densetsu-no-ansatsusha/covers/Hazure_Skill_Kage_ga_Usui_1.jpg.320x320_q85.jpg', 'https://rawdevart.com/media/comic/kage-no-jitsuryokusha-ni-naritakute-shadow-gaiden/covers/Kage_no_Jitsuryokusha_ni_Naritakute_Shadow_Gaiden_1.jpg.320x320_q85.jpg'] + ['https://rawdevart.com/media/comic/the-strongest-dull-princes-secret-battle-for-the-throne/covers/The_Strongest_Dull_Princes_Secret_Battle_for_the_Throne_1.jpg.320x320_q85.jpg', 'https://rawdevart.com/media/comic/kage-no-jitsuryokusha-ni-naritakute/covers/Kage_no_Jitsuryokusha_ni_Naritakute_1.jpg.320x320_q85.jpg', 'https://rawdevart.com/media/comic/hazure-skill-kage-ga-usui-o-motsu-guild-shokuin-ga-jitsuha-densetsu-no-ansatsusha/covers/Hazure_Skill_Kage_ga_Usui_1.jpg.320x320_q85.jpg', 'https://rawdevart.com/media/comic/kage-no-jitsuryokusha-ni-naritakute-shadow-gaiden/covers/Kage_no_Jitsuryokusha_ni_Naritakute_Shadow_Gaiden_1.jpg.320x320_q85.jpg']
class MangaCoverTile(SmartTileWithLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        #self.size_hint=(1, None)
        self.height = "240dp"


class MangaCoverContainer(ScrollView, MDBoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        #self.do_scroll_y = True
        #self.rel = MDRelativeLayout()
        self.grid = MDGridLayout(cols=3, adaptive_height=True,padding = ("4dp", "4dp"),spacing = "4dp")
        
        for index, cover in enumerate(covers):
            self.btn = MangaCoverTile(source=cover, text=str(index))
            self.grid.add_widget(self.btn)
        self.add_widget(self.grid)
        #self.rel.add_widget(self.grid)
        #self.add_widget(self.rel)

class MangaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

    def on_pre_enter(self, *args, **kwargs):
        self.settings_btn = MDIconButton(icon="cog", pos_hint={"center_x": .9, "center_y": .9}, user_font_size="64sp", on_press = lambda inst: MDApp.get_running_app().open_settings())
        #self.settings_btn.bind(on_press = lambda inst: MangaDownloader.get_running_app().open_settings())
        self.add_widget(self.settings_btn)

        self.home_btn = MDIconButton(icon="home", pos_hint={"center_x": .1, "center_y": .9}, user_font_size="64sp")
        self.home_btn.bind(on_press = self.go_to_home_screen)
        self.add_widget(self.home_btn)


    def go_to_home_screen(self,inst):
        self.manager.current = "Search page"

    def show_error_popup(self,text):
        Snackbar(text=text).open()


class MyApp(MDApp):
    def build(self):

        # Image source path needs to set from where the python file is, not the kv file

        #return Builder.load_file(os.path.join(".","KivyFiles","manga_covers.kv"))
        self.manager = ScreenManager()
        
        self.cont = MangaCoverContainer()
        screen = MangaScreen(name="list")
        screen.add_widget(self.cont)
        self.manager.add_widget(screen)
        return self.manager


        #return Builder.load_string(cover_display)



MyApp().run()
