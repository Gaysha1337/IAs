# -*- coding: utf-8 -*-
import os

# Kivy
from kivymd.app import MDApp
from kivy.properties import StringProperty, DictProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock

# Widgets
from kivymd.uix.button import MDIconButton, MDRectangleFlatIconButton, MDFlatButton
from kivymd.toast  import toast
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.dialog import MDDialog

# Screens and Screen-related
from kivy.uix.screenmanager import ScreenManager, Screen
from Homepage import MangaSearchPage, LandingPage, MangaReadingPage, DownloadedMangaDisplay
from MangaShowcase import MangaCoverContainer
from MangaReader import MangaReaderChapterSelection, MangaReaderCarousel # This will be a carousel for swiping pages

# Utils
from kivy.lang import Builder
from settings import AppSettings
from kivy.config import Config
from functools import partial
from utils import create_language_dirs, create_root_dir, move_manga_root

# Setting a default font
from kivy.core.text import LabelBase, DEFAULT_FONT
# android can only use droid, roboto, and dejavu fonts
LabelBase.register(DEFAULT_FONT, 'NotoSansCJKjp-Regular.otf')

# Kivy strings
from kivy_strings import *

_USERAGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"



Builder.load_string(manga_input_kv_str) # The input bar needs to be written in KV else the hint text wont showup

Config.set("network","useragent",_USERAGENT)

class ConfirmationDialog(MDDialog):
    def __init__(self, title, text, proceed_button_callback,**kwargs):
        self.master = MDApp.get_running_app()
        self.title =  title
        self.text = text
        self.auto_dismiss = False
        self.proceed_button_callback = proceed_button_callback
        self.buttons =[
            MDFlatButton(text="PROCEED", on_release= lambda *args:Clock.schedule_once(partial(self.proceed_button_callback))),
            MDFlatButton(text="CANCEL", on_release= lambda *args:self.dismiss())
        ]
        # Parent constructor is here to create the buttons; DO NOT MOVE!
        super().__init__(**kwargs)
        

class ToolBar(MDToolbar):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.master = MDApp.get_running_app()
        self.current_screen = self.master.screen_manager.get_screen(self.master.screen_manager.current)
        self.title = self.master.title
        self.id = "Toolbar"
        self.pos_hint = {"top":1}
        self.elevation = 10
        self.left_action_items = [["home", lambda x: self.switch_to_screen("Landing Page")],["cog", lambda x: MDApp.get_running_app().open_settings()]]
        self.right_action_items = [["undo", lambda x: self.switch_to_screen(self.current_screen.prev_screen)]]
        
    def switch_to_screen(self, screen_name):
        self.master.screen_manager.current = screen_name

class MangaScreen(Screen): 
    def __init__(self,prev_screen="Landing Page",**kwargs):
        super().__init__(**kwargs)
        self.prev_screen = prev_screen
           
    def on_pre_enter(self, *args, **kwargs):
        self.add_widget(ToolBar()) 


class MangaDownloader(MDApp):
    # This property is declared here as 'global' property, it will contain any found manga related to user input
    manga_data = DictProperty(None)
    # This property will be a reference to the selected manga site from which the app will download from
    downloader = StringProperty(None)
    # This property will check to see if a manga is being downloaded; used to show a popup if the download path is changed
    is_a_manga_being_downloaded = BooleanProperty(False)
    # The folder where all manga will be downloaded to, AKA: the manga root
    manga_root_dir = StringProperty(None)
    # The folders which will contain manga in english or Japanese
    english_manga_dir, japanese_manga_dir = StringProperty(None), StringProperty(None)
    
    def __init__(self):
        super().__init__()
        # C:\Users\dimit\AppData\Roaming\mangadownloader\Manga
        self.manga_root_dir = os.path.join(self.user_data_dir, "Manga")
        #self.english_manga_dir = os.path.join(self.manga_root_dir, "English Manga")
        #self.japanese_manga_dir = os.path.join(self.manga_root_dir, "Raw Japanese Manga")

        self.default_settings_vals = {
            'theme_mode':'Dark',
            'color_scheme':'Pink',
            'default_downloader': "rawdevart",
            'download_path':self.manga_root_dir,
            'manga_reading_direction': 'Swipe Horizontally', # Defaults to reading horizontally (swiping)
            'manga_swiping_direction':"Right to Left (English style)" # Defaults to English style: left to right
        }
        
    # Build the settings and sets their default values
    def build_config(self, config):
        config.setdefaults('Settings', self.default_settings_vals)

    def build_settings(self, settings):
        settings.add_json_panel('Manga Downloader Settings', self.config, data=AppSettings.json_settings)
        
    # Method that builds all the GUI elements    
    def build(self):
        self.title = "Manga Downloader"
        self.dialog = None # Used to get user confirmation

        # Settings
        self.settings_cls = AppSettings.ScrollableSettings # Section is called 'Settings'
        self.use_kivy_settings = False

        # Customizable Settings 
        self.theme_cls.theme_style = self.config.get("Settings", "theme_mode") # Dark or Light
        self.theme_cls.primary_palette = self.config.get("Settings", "color_scheme")
        self.downloader = self.config.get("Settings", "default_downloader") # The default manga downloading site
        
        # The path where all manga will be downloaded to (default is manga root)
        # If the client changes the download path while a manga is being downloaded an error will pop up
        self.download_path = self.config.get("Settings", "download_path") 
        
        self.manga_reading_direction = self.config.get("Settings", "manga_reading_direction")
        self.manga_swiping_direction = self.config.get("Settings", "manga_swiping_direction")
        
        # Manga Root Directory
        # If the user has changed the default download path (AKA: the manga root path) then set the manga root to the newly set path
        self.manga_root_dir = self.download_path if self.manga_root_dir != self.download_path else self.manga_root_dir
        print("before create root meth","self.download path", self.download_path, "self.manga root", self.manga_root_dir, sep="\n")
        self.english_manga_dir = os.path.join(self.manga_root_dir, "English Manga")
        self.japanese_manga_dir = os.path.join(self.manga_root_dir, "Raw Japanese Manga")
        create_root_dir(self.manga_root_dir)
        create_language_dirs([self.english_manga_dir,self.japanese_manga_dir])
        print("after create root meth", "self.download path", self.download_path, "self.manga root", self.manga_root_dir, sep="\n")
        
        # Screen related
        self.screen_manager = ScreenManager()

        self.landing_page = LandingPage(self)
        screen = MangaScreen(name="Landing Page")
        screen.add_widget(self.landing_page)
        self.screen_manager.add_widget(screen)

        #self.reading_screens = ["Reading Page", "Manga Reader Chapter Selection", "Manga Reader Carousel"]
        #self.downloading_screens = ["Manga Input Page", "Manga Showcase", "Downloaded Manga Showcase"]

        return self.screen_manager

    """ Downloading Related Screens """

    # Creates the page where the user can input a manga to be downloaded
    def create_manga_search_page(self):
        self.manga_search_page = MangaSearchPage(self)
        screen = MangaScreen(name="Manga Input Page")
        screen.add_widget(self.manga_search_page)
        self.screen_manager.add_widget(screen)
    
    # Creates the manga display grid when the user has input a name
    def create_manga_display(self):
        self.manga_display = MangaCoverContainer(self)
        screen = MangaScreen(name="Manga Showcase", prev_screen="Manga Input Page")
        screen.add_widget(self.manga_display)
        self.screen_manager.add_widget(screen)

    """ Reading Related Screens """

    # Creates the page where the user can choose to read manga in English or Japanese
    def create_manga_reading_page(self):
        self.manga_reader_page = MangaReadingPage(self)
        screen = MangaScreen(name="Reading Page")
        screen.add_widget(self.manga_reader_page)
        self.screen_manager.add_widget(screen)

    # Creates the manga display for all downloaded manga found in a specific language
    def create_manga_read_display(self, language):
        #self.manga_display = RV(self)
        self.download_manga_display = DownloadedMangaDisplay(self, language)
        screen = MangaScreen(name="Downloaded Manga Showcase", prev_screen="Reading Page")
        screen.add_widget(self.download_manga_display)
        self.screen_manager.add_widget(screen)

    # Creates a display with buttons of the downloaded chapters 
    def create_manga_reader_chapter_selection(self, title, manga_path):
        self.chapter_selector = MangaReaderChapterSelection(self, title, manga_path)
        screen = MangaScreen(name="Manga Reader Chapter Selection", prev_screen="Downloaded Manga Showcase")
        screen.add_widget(self.chapter_selector)
        self.screen_manager.add_widget(screen)

    # Creates the swiping carousel for reading a downloaded manga
    def create_manga_reader(self,manga_title,chapter_name,chapter_path):
        self.manga_reader = MangaReaderCarousel(self, manga_title,chapter_name, chapter_path)
        screen = MangaScreen(name="Manga Reader Carousel", prev_screen="Manga Reader Chapter Selection")
        screen.add_widget(self.manga_reader)
        self.screen_manager.add_widget(screen)


    # This method can handle any changes made to the settings, it also changes them when they are changed
    def on_config_change(self, config, section, key, value):
        print(config, section, key, value, "config change event fired")

        """
        This func exists because if the client changes the download path while downloading a manga
        then not all the chapters will be downloaded to the new path
        """ 
        def change_download_path(value=value):
            root_src, new_dst = os.path.join(self.download_path), os.path.join(value)
            print("src: ", root_src, "dst: ", new_dst)
            try:
                # Recursive function to move the english and Japanese manga containing folders to the new destination
                move_manga_root(root_src,new_dst)
                print(f"Download Path was successfully moved to {new_dst}")
                self.manga_root_dir = self.download_path = self.config.get("Settings", "download_path")
                toast(f"Manga Download Path has been changed to {self.manga_root_dir}")
            
            except PermissionError:
                toast("Permission Error occurred; You maybe don't have access")
            except:
                if root_src != new_dst:
                    toast("Unknown Error: Files have not been moved")

        # A callback function for a confirmation dialog
        def reset_settings_config(inst):
            if isinstance(self.dialog, MDDialog):
                self.dialog.dismiss(force=True)
                self.dialog = None
            config.setall("Settings",self.default_settings_vals)
            config.write()
            change_download_path(self.default_settings_vals.get("download_path"))
            self.close_settings()
            self.destroy_settings()
            self.open_settings()

        # This section will reset all settings to their default values
        if key == "configchangebuttons":
            self.dialog = None
            if not self.dialog:
                self.dialog = ConfirmationDialog(
                    title= "Reset to Factory Settings Confirmation: ",
                    text= "Warning: This will remove all current settings!\nAny Downloaded Manga will be moved to the default download folder!",
                    proceed_button_callback = reset_settings_config)
            self.dialog.open()
            
        # Moves the root/download folder to the new path
        if key == "download_path" and os.path.isdir(os.path.join(value)):
            if self.is_a_manga_being_downloaded:
                # I have given up on this; it is not a part of my requirements
                toast("Warning: The download path has been changed while a manga is being downloaded. All new chapters will be downloaded to the new path")
            change_download_path()
        
        self.theme_cls.theme_style = self.config.get("Settings", "theme_mode")
        self.theme_cls.primary_palette = self.config.get("Settings", "color_scheme")
        #self.pc_download_path = self.config.get("Settings", "PCDownloadPath")
        #self.android_download_path = self.config.get("Settings", "AndroidDownloadPath")
        #self.download_path = self.config.get("Settings", "download_path") 
        self.downloader = self.config.get("Settings", "default_downloader")

        if key == "manga_swiping_direction": self.manga_swiping_direction = self.config.get("Settings", "manga_swiping_direction")

        if key == "manga_reading_direction": self.manga_reading_direction = self.config.get("Settings", "manga_reading_direction")

if __name__ == "__main__":
    MangaDownloader().run()
