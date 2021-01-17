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

# Downloaders
from Downloaders.MangaNelo import MangaNelo
from Downloaders.Rawdevart import RawDevArt
from Downloaders.Kissmanga import KissManga
from Downloaders.Senmanga import SenManga

# The ScrollView widget provides a scrollable view
from kivy.uix.recycleview import RecycleView
from kivy.uix.scrollview import ScrollView

# Utils
from kivy.lang import Builder
from utils import create_manga_dirs


class MangaCoverTile(SmartTileWithLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.master = MDApp.get_running_app()
        self.size_hint_y = None
        self.height = "240dp"
        self.font_style = "H6"
        #self.size_hint = (.25,.25)
        
        self.progressbar = MDProgressBar(value=0,pos_hint={"center_x":.5,"center_y": .5}, opacity = 0)
        self.add_widget(self.progressbar)

    def reset_progressbar(self,*args):
        if isinstance(self.progressbar, MDProgressBar):
            self.remove_widget(self.progressbar)
        self.progressbar = MDProgressBar(value=0,pos_hint={"center_x":.5,"center_y": .5}, opacity = 0)
        self.add_widget(self.progressbar)

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
        self.scroll_wheel_distance = "20sp"
        self.do_scroll_y = True
        self.pos_hint = {"top":.9}
        
        
        # This grid acts as a container for the number of manga found and the table with the clickable tiles
        self.outer_gird = MDGridLayout(rows=2, adaptive_height=True, padding=("0dp", "20dp", "0dp", "20dp"), pos_hint={"top":.8})
        self.outer_gird.add_widget(MDLabel(text=f"{len(self.manga_data)} manga were found", halign="center", pos_hint = {"center_x":.5,"y":.9}))
        
        # padding: [padding_left, padding_top, padding_right, padding_bottom]
        
        # This grid acts a table to store all found manga 
        self.grid = MDStackLayout(adaptive_height=True, orientation="lr-tb", spacing=("20dp","20dp"), padding=("5dp", "30dp", "5dp", "30dp")) 
        
        for title, links_tuple in self.manga_data.items():
            print("linkes tuples", links_tuple)
            self.btn = MangaCoverTile(source=links_tuple[1], text=title, on_release=partial(self.make_request, title), size_hint=(.25,.25))
            self.grid.add_widget(self.btn)
            
        # Checks to see if any manga were found; An empty dict means no manga were found with the inputted text
        if self.manga_data == {}: 
            self.grid.add_widget(MDLabel(text="No Manga found", halign="center",pos_hint={"center_x":.5, "center_y":.5}))
    
        self.outer_gird.add_widget(self.grid)
        self.add_widget(self.outer_gird)

    #@mainthread
    # the code wont run unless *args is written; it claims '3 args where passed in the partial func above'
    # Note: tile acts as an instance of the button
    # If the client attempts to change the download path while a manga is being downloaded an error will popup
    def make_request(self,title,tile):
        self.master.currently_downloading = True 
        toast(f"Downloading {title}")
        tile.progressbar.opacity = 1                    
        
        # Creates the directory for that manga within the manga root and changes to it
        create_manga_dirs(self.master.downloader, title)
        
        # Calls the appropriate downloader based on the selected site and starts a thread to allow prevent kivy event loop from locking
        #threading.Thread(name="Download Thread",target=partial(self.downloader_links_methods.get(self.master.downloader, lambda *args: "invalid downloader or download method"), self.master, tile, title, self.manga_data.get(title))).start()
        download_thread_target = partial(self.downloader_links_methods.get(self.master.downloader, lambda *args: "invalid downloader or download method"), self.master, tile, title, self.manga_data.get(title))
        self.master.download_thread = Thread(name="Download Thread",target=download_thread_target, daemon=True)
        self.master.download_thread.start()