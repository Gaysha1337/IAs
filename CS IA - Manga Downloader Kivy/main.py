import os, json, plyer
from functools import partial

from kivy.uix.button import Button
from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton, MDRectangleFlatIconButton
from kivymd.uix.snackbar import Snackbar

from kivy.properties import ListProperty, DictProperty

from kivy.lang import Builder
from kivy.utils import platform  # Used to tell if platform is android

from kivy.uix.screenmanager import ScreenManager, Screen

# Downloaders
from Downloaders.manga_nelo_OOP import MangaNelo

# Screens
from Homepage import MangaSearchPage
from MangaShowcase import RV, MangaCoverContainer

# Kivy strings
from kivy_strings import *

# Utils
from settings import AppSettings
from kivy.config import Config

Config.set("network","useragent","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'")

Builder.load_string(manga_input_kv_str) # The input bar needs to be wirrten in KV else the hint text wont showup
Builder.load_string(manga_display_kv_str)


class MangaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self, *args, **kwargs):
        self.settings_btn = MDIconButton(icon="cog", pos_hint={"center_x": .9, "center_y": .9}, user_font_size="64sp", on_press = lambda inst: MDApp.get_running_app().open_settings())
        self.settings_btn.text_color = "Pink"
        #self.settings_btn.bind(on_press = lambda inst: MangaDownloader.get_running_app().open_settings())
        self.add_widget(self.settings_btn)

        self.home_btn = MDIconButton(icon="home", pos_hint={"center_x": .1, "center_y": .9}, user_font_size="64sp")
        self.home_btn.bind(on_press = self.go_to_home_screen)
        self.add_widget(self.home_btn)


    def go_to_home_screen(self,inst):
        self.manager.current = "Search page"

    def show_error_popup(self,text):
        Snackbar(text=text).open()


class MangaDownloader(MDApp):
    # This property is declared here as 'global' property, it will contain any found manga related to user input
    manga_data = DictProperty(None)

    def build(self):
        self.title = "Manga Downloader"

    
        # Customizable Settings
        self.theme_cls.theme_style = self.config.get("Settings", "theme_mode")
        self.theme_cls.primary_palette = self.config.get("Settings", "color_scheme")
        self.download_path = self.config.get("Settings", "DownloadPath")
        self.default_manga_site = self.config.get("Settings", "default_manga_site")


        self.settings_cls = AppSettings.ScrollableSettings # Section is called 'Settings'
        self.use_kivy_settings = False

        self.screen_manager = ScreenManager()

        self.manga_search_page = MangaSearchPage(self)
        screen = MangaScreen(name="Search page")
        screen.add_widget(self.manga_search_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

    # Creates the manga display grid when the user has input a name
    def create_manga_display(self):
        #self.manga_display = RV(self)
        self.manga_display = MangaCoverContainer(self)

        screen = MangaScreen(name="Manga Showcase")
        screen.add_widget(self.manga_display)
        self.screen_manager.add_widget(screen)

        #print(self.screen_manager.screen_names)

    def build_config(self, config):
        user_downloads_dir = plyer.storagepath.get_downloads_dir()

        config.setdefaults('Settings', {
            'boolexample': True,
            'numericexample': 10,
            'optionsexample': 'option2',
            'stringexample': 'some_string',
            'DownloadPath': user_downloads_dir,
            'theme_mode':'Light',
            'color_scheme':'Red'}
        )

    def build_settings(self, settings):
        # You can add multiple panels
        settings.add_json_panel('Manga Downloader Settings', self.config, data=AppSettings.json_settings)

    # This method can handle any changes made to the settings, it also changes them when they are changed
    def on_config_change(self, config, section, key, value):
        print(config, section, key, value, "fuwhrif")
        self.theme_cls.theme_style = self.config.get("Settings", "theme_mode")
        self.theme_cls.primary_palette = self.config.get("Settings", "color_scheme")
        self.download_path = self.config.get("Settings", "DownloadPath")
        self.default_manga_site = self.config.get("Settings", "default_manga_site")


if __name__ == "__main__":
    MangaDownloader().run()
