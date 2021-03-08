import os, threading, time
from threading import Thread, main_thread
from functools import partial

from kivymd.app import MDApp
from kivy.clock import mainthread

from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.stacklayout import MDStackLayout

from kivy.uix.scrollview import ScrollView
from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.uix.label import MDLabel
from kivymd.toast import toast
from kivymd.uix.progressbar import MDProgressBar 

# Downloaders
from Downloaders.MangaNelo import MangaNelo
from Downloaders.Rawdevart import RawDevArt
from Downloaders.Kissmanga import KissManga
from Downloaders.Senmanga import SenManga

# Utils
from utils import create_manga_dirs, display_message


class MangaCoverTile(SmartTileWithLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.master = MDApp.get_running_app()
        self.size_hint_y = None
        self.height = "240dp"
        self.font_style = "H6"
        
        self.progressbar = MDProgressBar(value=0,pos_hint={"center_x":.5,"center_y": .5}, opacity = 0)
        self.add_widget(self.progressbar)

    def reset_progressbar(self,*args):
        if isinstance(self.progressbar, MDProgressBar):
            self.remove_widget(self.progressbar)
        self.progressbar = MDProgressBar(value=0,pos_hint={"center_x":.5,"center_y": .5}, opacity = 0)
        self.add_widget(self.progressbar)

        # Remove thread from list since it has finished executing
        self.master.download_threads.pop(self.text) # Text is the title of the manga
        self.master.currently_downloading = False if len(self.master.download_threads) == 0 else True

# Downloaded Manga Display
class MangaCoverContainer(ScrollView):
    def __init__(self, master,**kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.manga_data = self.master.manga_data
        self.downloader_links_methods = {
            "manganelo":MangaNelo.download_manga, 
            "kissmanga":KissManga.download_manga,
            "rawdevart":RawDevArt.download_manga,
            "senmanga":SenManga.download_manga
        }
        self.effect_cls = "ScrollEffect"
        self.bar_width = "10dp"
        self.pos_hint = {"top":.9}
    
        # This grid acts as a container for the number of manga found and the table with the clickable tiles
        self.outer_gird = MDGridLayout(rows=2, adaptive_height=True, padding=("0dp", "20dp", "0dp", "20dp"), pos_hint={"top":.8})
        self.outer_gird.add_widget(MDLabel(text=f"{len(self.manga_data)} manga were found", halign="center", pos_hint = {"center_x":.5,"y":.9}))
        
        # This grid acts a table to store all found manga 
        self.grid = MDStackLayout(adaptive_height=True, orientation="lr-tb", spacing=("20dp","20dp"), padding=("5dp", "30dp", "5dp", "30dp")) 
        
        for title, links_tuple in self.manga_data.items():
            self.btn = MangaCoverTile(source=links_tuple[1], text=title, on_release=partial(self.make_request, title), size_hint=(.25,.25))
            self.grid.add_widget(self.btn)
            
        # Checks to see if any manga were found; An empty dict means no manga were found with the inputted text
        if self.manga_data == {}: self.grid.add_widget(MDLabel(text="No Manga found", halign="center",pos_hint={"center_x":.5, "center_y":.5}))
    
        self.outer_gird.add_widget(self.grid)
        self.add_widget(self.outer_gird)

    # Note: the param tile acts as a button instance
    def make_request(self,title,tile):
        # Calls the appropriate downloader based on the selected site and starts a thread to prevent kivy event loop from locking
        download_thread_target = partial(self.downloader_links_methods.get(self.master.downloader), tile, title, self.manga_data.get(title))
        download_thread = Thread(name=f"Download Thread {title}",target=download_thread_target)

        # Flag used to ensure that the same manga is not downloaded while it is already being downloaded
        if self.master.download_threads.get(title, None) == None: # If a manga is already being downloaded it will not return None
            self.master.download_threads.update({title:download_thread})
            self.master.currently_downloading = True
            tile.progressbar.opacity = 1
            
            # Creates the directory for that manga within the manga root and changes to it
            create_manga_dirs(self.master.downloader, title)
            download_thread.start()
        else:
            display_message(f"{title} is already downloading")

