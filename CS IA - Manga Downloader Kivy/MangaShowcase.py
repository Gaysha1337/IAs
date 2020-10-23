import os, threading
from threading import Thread

from kivymd.uix.boxlayout import MDBoxLayout
from Homepage import MangaCheckBox

from kivy.core.window import Window
from kivy.uix.label import Label
from kivymd.app import MDApp
from kivy.clock import Clock, mainthread
from kivy.properties import ListProperty, DictProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton, MDIconButton, MDRectangleFlatIconButton

from kivy.uix.screenmanager import Screen, ScreenManager

from kivymd.uix.gridlayout import GridLayout
from kivymd.uix.gridlayout import MDGridLayout
#from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.stacklayout import MDStackLayout

from kivy.uix.relativelayout import RelativeLayout

from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.toast import toast

from functools import partial
from kivy.utils import platform  # Used to tell if platform is android
from kivymd.uix.progressbar import MDProgressBar 
from kivymd.uix.card import MDCard, MDSeparator

# Downloaders
from Downloaders.manga_nelo_OOP import MangaNelo
from Downloaders.raw_dev_art import RawDevArt
from Downloaders.kissmanga import KissManga
from Downloaders.Senmanga import SenManga

# The ScrollView widget provides a scrollable view
from kivy.uix.recycleview import RecycleView
from kivy.uix.scrollview import ScrollView

from kivy.lang import Builder
from kivy.graphics import Rectangle, Color
from utils import download_manga, create_manga_dirs

from kivy_strings import manga_display_kv_str


class RV(RecycleView):
    manga_data = DictProperty(None)

    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        print(MDApp.get_running_app().manga_data, "in RV class in init")
        #self.effect_cls = StiffScrollEffect

        self.data = [
            {
                'text': str(x),
                'source': self.manga_data.get(x)[1],
                'on_release': partial(self.make_request, x),
                'pos_hint': {'center_x': .5, 'center_y': .5}
            }
            for x in self.manga_data
        ]
        #print(self.manga_data, "in RV class")

    def make_request(self, title):
        print(title, self.manga_data.get(title))
        MangaNelo.download_manga(title, self.manga_data.get(title))

class MangaCoverTile(SmartTileWithLabel):
    instances = []
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__class__.instances.append(self)
        self.size_hint_y = None
        self.height = "240dp"
        self.font_style = "H6"
        #self.bind(on_release = self.get_tile_data)

        self.progressbar = MDProgressBar(value=0,pos_hint={"center_x":.5,"center_y": .5})
        self.progressbar.opacity = 0
        self.add_widget(self.progressbar)
       

    #TODO: Check if manga is already downloaded
    def get_tile_data(self,*args):
        pass

# Downloaded Manga Display
class MangaCoverContainer(ScrollView):
    def __init__(self, master,**kwargs):
        super().__init__(**kwargs)
        self.master = master
        #self.screen_toolbar = self.master.screen_manager.current_screen.toolbar
        self.manga_data = self.master.manga_data
        self.downloader_links_methods = {"manganelo":MangaNelo.download_manga, "rawdevart":RawDevArt.download_manga,"kissmanga":KissManga.download_manga,"senmanga":SenManga.download_manga}
        self.found_manga = [] # This list is ordered like on the screen, self.grid.children is not 
        self.effect_cls = "ScrollEffect"
        self.scroll_type = ["bars"]
        self.bar_width = "10dp"
        self.pos_hint = {"top":.9}
        
        # padding: [padding_left, padding_top, padding_right, padding_bottom]
        self.grid = MDGridLayout(cols=5,adaptive_height=True,padding=("30dp", "50dp", "30dp", "100dp"), spacing="20dp") #padding=("30dp", "5dp")
        #self.grid = MDBoxLayout(adaptive_height=True,padding=("30dp", "50dp", "30dp", "100dp"), spacing="20dp") #padding=("30dp", "5dp")

        for i in range(5):
            self.manga_num_label = MDLabel(pos_hint = {"center_x":.5,"center_y":1})
            if i == 3:
                self.manga_num_label.text = f"{len(self.manga_data)} manga were found"
            self.grid.add_widget(self.manga_num_label)    

        for title, links_tuple in self.manga_data.items():
            self.btn = MangaCoverTile(source=links_tuple[1], text=title, on_release=partial(self.make_request, title))
            self.grid.add_widget(self.btn)
            print(self.btn.size)
        
        if self.manga_data == {}:
            self.grid.add_widget(MDLabel(text="No Manga found", halign="center",pos_hint={"center_x":.5, "center_y":.5}))
        self.add_widget(self.grid)

    @mainthread
    # the code wont run unless *args is written; it claims '3 args where passed in the partial func above'
    # Note: tile acts as an instance of the button
    def make_request(self,title,tile):
        self.master.selected_manga = title
        toast(f"Downloading {title}")
        tile.progressbar.opacity = 1                    
        # Calls the appropriate downloader based on the selected site
        #self.downloader_links_methods.get(self.master.downloader, lambda *args: "invalid downloader or download method")(self.master, tile,title, self.manga_data.get(title))
        create_manga_dirs(self.master.downloader ,title)
        
        print("cwd: ", os.getcwd())
        # Calls the appropriate downloader based on the selected site and starts a thread to allow prevent kivy event loop from locking
        threading.Thread(target=partial(self.downloader_links_methods.get(self.master.downloader, lambda *args: "invalid downloader or download method"), self.master, tile, title, self.manga_data.get(title))).start()


if __name__ == "__main__":
    Builder.load_string(manga_display_kv_str)

    class MangaScreen(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.settings_btn = MDIconButton(icon="cog", pos_hint={
                                             "center_x": .9, "center_y": .9}, user_font_size="64sp", on_press=lambda inst: MDApp.get_running_app().open_settings())
            # self.settings_btn.bind(on_press = lambda inst: MangaDownloader.get_running_app().open_settings())
            self.add_widget(self.settings_btn)

            self.home_btn = MDIconButton(icon="home", pos_hint={
                                         "center_x": .1, "center_y": .9}, user_font_size="64sp")
            self.home_btn.bind(on_press=self.go_to_home_screen)
            self.add_widget(self.home_btn)

        def go_to_home_screen(self, inst):
            self.manager.current = "Search page"

    class MyApp(MDApp):
        def build(self):
            self.manager = ScreenManager()
            self.rv = RV(self)
            screen = MangaScreen(name="RV")
            screen.add_widget(self.rv)
            self.manager.add_widget(screen)

            return self.manager
    MyApp().run()
