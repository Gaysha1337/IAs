# -*- coding: utf-8 -*-
import os
import shutil

# Kivy
from kivymd.app import MDApp
from kivy.properties import StringProperty, DictProperty

# Widgets
from kivymd.uix.button import MDIconButton, MDRectangleFlatIconButton
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.toolbar import MDToolbar

# Screens and Screen-related
from kivy.uix.screenmanager import ScreenManager, Screen
from Homepage import MangaSearchPage, LandingPage, MangaReadingPage, DownloadedMangaDisplay
from MangaShowcase import RV, MangaCoverContainer
from MangaReader import MangaReaderChapterSelection, MangaReaderCarousel # This will be a carousel for swiping pages

# Utils
from kivy.lang import Builder
from settings import AppSettings
from kivy.config import Config

from utils import create_language_dirs, create_root_dir

# Setting a default font (does this work on android?)
from kivy.core.text import LabelBase, DEFAULT_FONT
LabelBase.register(DEFAULT_FONT, 'NotoSansCJKjp-Regular.otf')

# Kivy strings
from kivy_strings import *

_USERAGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"


# android can only use droid, roboto, and dejavu fonts
Builder.load_string(manga_input_kv_str) # The input bar needs to be written in KV else the hint text wont showup
#Builder.load_string(manga_display_kv_str)
Config.set("network","useragent",_USERAGENT)

class ToolBar(MDToolbar):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.title = "Manga Downloader"
        self.id = "Toolbar"
        self.pos_hint = {"top":1}#{"center_y":.955}
        self.elevation = 10
        self.left_action_items = [["cog", lambda x: MDApp.get_running_app().open_settings()]]
        self.right_action_items = [["home", lambda x: self.go_to_home_screen]]
        
    def go_to_home_screen(self, inst):
        #self.manager.current = "Landing Page"
        MDApp.get_running_app().screen_manager.current = "Landing Page"

class MangaScreen(Screen): 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
           
    def on_pre_enter(self, *args, **kwargs):
        self.toolbar = ToolBar(title="Manga Downloader", pos_hint={"top":1})#{"center_y":.955}
        self.toolbar.left_action_items = [["cog", lambda x: MDApp.get_running_app().open_settings()]]
        self.toolbar.right_action_items = [["home", lambda x: self.go_to_home_screen()]]
        self.add_widget(self.toolbar) 

    def go_to_home_screen(self):
        #self.manager.current = "Search page"
        self.manager.current = "Landing Page"

    def show_error_popup(self,text):
        Snackbar(text=text).open()


class MangaDownloader(MDApp):

    # This property is declared here as 'global' property, it will contain any found manga related to user input
    manga_data = DictProperty(None)
    # This property will be a reference to the selected manga site from which the app will download from
    downloader = StringProperty(None)
    # This property will hold a reference to the user's search input (not the manga they chose)
    input_query = StringProperty(None)
    # This property will hold a reference to the user's selected manga when they click on a tile
    # TODO: Can it be used only for downloading manga or reading it?
    selected_manga = StringProperty(None)
    # The folder where all manga will be downloaded to, AKA: the manga root
    manga_root_dir = StringProperty(None)
    # The folders which will contain manga in english or Japanese
    english_manga_dir, japanese_manga_dir = StringProperty(None), StringProperty(None)
    # Reference for the download folder for the selected manga to be downloaded
    current_manga_dir = StringProperty(None)

    def __init__(self):
        super().__init__()
        # C:\Users\dimit\AppData\Roaming\mangadownloader\Manga
        self.manga_root_dir = os.path.join(self.user_data_dir, "Manga")
        self.english_manga_dir = os.path.join(self.manga_root_dir, "English Manga")
        self.japanese_manga_dir = os.path.join(self.manga_root_dir, "Raw Japanese Manga")
        
    # Build the settings and sets their default values
    def build_config(self, config):
        #TODO: Not sure if this applies to PC
        #user_downloads_dir = plyer.storagepath.get_downloads_dir()
        #user_downloads_dir = os.path.join(self.user_data_dir, "Manga")

        config.setdefaults('Settings', {
            'theme_mode':'Dark',
            'color_scheme':'Pink',
            'default_downloader': "rawdevart",
            'download_path':self.manga_root_dir,
            'manga_reading_direction': int(False), # Defaults to reading horizontally (swiping)
            'manga_swiping_direction':int(False), # Defaults to English style: left to right; True is Japanese (right to left)
            'optionsexample': 'option2',
            }
        )

    def build_settings(self, settings):
        # You can add multiple panels
        settings.add_json_panel('Manga Downloader Settings', self.config, data=AppSettings.json_settings)
    
    def build(self):
        self.title = "Manga Downloader"

        # Settings
        self.settings_cls = AppSettings.ScrollableSettings # Section is called 'Settings'
        self.use_kivy_settings = False

        # Customizable Settings
        self.theme_cls.theme_style = self.config.get("Settings", "theme_mode") # Dark or Light
        self.theme_cls.primary_palette = self.config.get("Settings", "color_scheme")
        self.download_path = self.config.get("Settings", "download_path") # The path where all manga will be downloaded to (default is manga root)
        self.downloader = self.config.get("Settings", "default_downloader") # The default manga downloading site
        # getint is used to convert the string val into int and into a boolean
        self.manga_reading_direction = bool(int(self.config.getint("Settings", "manga_reading_direction"))) or None
        self.manga_swiping_direction = bool(int(self.config.getint("Settings", "manga_swiping_direction"))) or None
        
        print("before create root meth")
        print("self.download path", self.download_path)
        print("self.manga root", self.manga_root_dir)
        # Manga Root Directory

        # If the user has changed the default download path (AKA: the manga root path) then set the manga root to the newly set path
        self.manga_root_dir = self.download_path if self.manga_root_dir != self.download_path else self.manga_root_dir
        create_root_dir(self.manga_root_dir)
        create_language_dirs([self.english_manga_dir,self.japanese_manga_dir])
        print("after create root meth")
        print("self.download path", self.download_path)
        print("self.manga root", self.manga_root_dir)
        # Screen related
        self.screen_manager = ScreenManager()

        self.landing_page = LandingPage(self)
        screen = MangaScreen(name="Landing Page")
        screen.add_widget(self.landing_page)
        self.screen_manager.add_widget(screen)

        self.manga_reader_page = MangaReadingPage(self)
        screen = MangaScreen(name="Reading page")
        screen.add_widget(self.manga_reader_page)
        self.screen_manager.add_widget(screen)

        self.manga_search_page = MangaSearchPage(self)
        screen = MangaScreen(name="Search page")
        screen.add_widget(self.manga_search_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

    # Creates the manga display grid when the user has input a name
    def create_manga_display(self):
        self.manga_display = MangaCoverContainer(self)
        screen = MangaScreen(name="Manga Showcase")
        screen.add_widget(self.manga_display)
        self.screen_manager.add_widget(screen)

    # Creates the manga display for all downloaded manga found in a specific language
    def create_manga_read_display(self, language):
        #self.manga_display = RV(self)
        self.download_manga_display = DownloadedMangaDisplay(self, language)
        screen = MangaScreen(name="Downloaded Manga Showcase")
        screen.add_widget(self.download_manga_display)
        self.screen_manager.add_widget(screen)

    # Creates a display with buttons of the downloaded chapters 
    def create_manga_reader_chapter_selection(self,title, manga_path):
        self.chapter_selector = MangaReaderChapterSelection(self, title, manga_path)
        screen = MangaScreen(name="Manga Reader Chapter Selection")
        screen.add_widget(self.chapter_selector)
        self.screen_manager.add_widget(screen)

    # Creates the swiping carousel for reading a downloaded manga
    def create_manga_reader(self,manga_title,chapter_name,chapter_path):
        self.manga_reader = MangaReaderCarousel(self, manga_title,chapter_name, chapter_path)
        screen = MangaScreen(name="Manga Reader")
        screen.add_widget(self.manga_reader)
        self.screen_manager.add_widget(screen)

    # This method can handle any changes made to the settings, it also changes them when they are changed
    def on_config_change(self, config, section, key, value):
        print(config, section, key, value, "fuwhrif")

        # Moves the root/download folder to the new path
        if key == "download_path" and os.path.isdir(os.path.join(value)):
            src, dst = os.path.join(self.download_path), os.path.join(value)

            # Changes the src depending on if the user selected path has ends with 'Manga'
            src = os.path.join(src, "Manga") if not self.download_path.endswith("Manga") else src
            try:
                shutil.move(src=src, dst=dst)
            except PermissionError:
                pass
                #self.config.set("Settings", "download_path", os.path.join(value,"Manga"))
                #self.config.write()
            self.manga_root_dir = self.download_path = self.config.get("Settings", "download_path")
        
        self.theme_cls.theme_style = self.config.get("Settings", "theme_mode")
        self.theme_cls.primary_palette = self.config.get("Settings", "color_scheme")
        #self.pc_download_path = self.config.get("Settings", "PCDownloadPath")
        #self.android_download_path = self.config.get("Settings", "AndroidDownloadPath")
        #self.download_path = self.config.get("Settings", "download_path") 
        self.downloader = self.config.get("Settings", "default_downloader")

        self.manga_reading_direction = bool(int(self.config.getint("Settings", "manga_reading_direction")))
        self.manga_swiping_direction = bool(int(self.config.getint("Settings", "manga_swiping_direction")))

        #print("reading dir:",self.manga_reading_direction, "self.swiping dir: ,", self.manga_swiping_direction)
        

if __name__ == "__main__":
    MangaDownloader().run()
