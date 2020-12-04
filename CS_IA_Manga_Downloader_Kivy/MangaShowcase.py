import os, threading, time
from threading import Thread

from kivymd.uix.boxlayout import MDBoxLayout
from Homepage import MangaCheckBox

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
from Downloaders.MangaNelo import MangaNelo
from Downloaders.raw_dev_art import RawDevArt
from Downloaders.kissmanga import KissManga
from Downloaders.Senmanga import SenManga

# The ScrollView widget provides a scrollable view
from kivy.uix.recycleview import RecycleView
from kivy.uix.scrollview import ScrollView

# Utils
from kivy.lang import Builder
from utils import create_manga_dirs, PausableThread


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
        self.downloader_links_methods = {"manganelo":MangaNelo.download_manga, "kissmanga":KissManga.download_manga,"rawdevart":RawDevArt.download_manga,"senmanga":SenManga.download_manga}
        self.effect_cls = "ScrollEffect"
        self.scroll_type = ["bars"]
        self.bar_width = "10dp"
        self.pos_hint = {"top":.9}
        
        self.outer_gird = MDGridLayout(rows=2,adaptive_height=True, padding=("0dp", "20dp", "0dp", "0dp"))
        self.outer_gird.add_widget(MDLabel(text=f"{len(self.manga_data)} manga were found", halign="center",pos_hint = {"center_x":.5,"top":.7}))
        
        # padding: [padding_left, padding_top, padding_right, padding_bottom]
        self.grid = MDGridLayout(cols=5,adaptive_height=True,padding=("30dp", "50dp", "30dp", "100dp"), spacing="20dp") #padding=("30dp", "5dp")
        self.grid.cols = 5 if platform == "win" else 1 # set the num of cols depeneding on device; on android: 1 is easier (UI purpose)
        
        for title, links_tuple in self.manga_data.items():
            print("linkes tuples", links_tuple)
            self.btn = MangaCoverTile(source=links_tuple[1], text=title, on_release=partial(self.make_request, title))
            self.grid.add_widget(self.btn)
            
        
        if self.manga_data == {}:
            self.grid.add_widget(MDLabel(text="No Manga found", halign="center",pos_hint={"center_x":.5, "center_y":.5}))
            #self.outer_gird.add_widget(MDLabel(text="No Manga found", halign="center",pos_hint={"center_x":.5, "center_y":.5}))
        self.outer_gird.add_widget(self.grid)
        #self.add_widget(self.grid)
        self.add_widget(self.outer_gird)

    #@mainthread
    # the code wont run unless *args is written; it claims '3 args where passed in the partial func above'
    # Note: tile acts as an instance of the button
    # If the client attempts to change the download path while a manga is being downloaded an error will popup
    def make_request(self,title,tile):
        self.master.is_a_manga_being_downloaded = True 
        self.master.selected_manga = title
        toast(f"Downloading {title}")
        tile.progressbar.opacity = 1                    
        # Calls the appropriate downloader based on the selected site
        #self.downloader_links_methods.get(self.master.downloader, lambda *args: "invalid downloader or download method")(self.master, tile,title, self.manga_data.get(title))
        create_manga_dirs(self.master.downloader ,title)
        
        print("cwd: ", os.getcwd())
        
        # Calls the appropriate downloader based on the selected site and starts a thread to allow prevent kivy event loop from locking
        #threading.Thread(name="Download Thread",target=partial(self.downloader_links_methods.get(self.master.downloader, lambda *args: "invalid downloader or download method"), self.master, tile, title, self.manga_data.get(title))).start()
        download_thread_target = partial(self.downloader_links_methods.get(self.master.downloader, lambda *args: "invalid downloader or download method"), self.master, tile, title, self.manga_data.get(title))
        self.master.download_thread = PausableThread(name="Download Thread",target=download_thread_target)
        self.master.download_thread.daemon = True
        self.master.download_thread.start()