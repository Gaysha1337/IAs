from functools import partial
import os
import sys
from pathlib import Path
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout

from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDRectangleFlatButton, MDRectangleFlatIconButton

from kivymd.uix.snackbar import Snackbar
from kivymd.toast import toast


from kivymd.uix.gridlayout import GridLayout, MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout

from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.lang import Builder
from kivy.utils import platform  # Used to tell if platform is android

from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.menu import MDDropdownMenu, RightContent
from kivymd.uix.selectioncontrol import MDCheckbox

from Downloaders.manga_nelo_OOP import MangaNelo
from Downloaders.raw_dev_art import RawDevArt
from Downloaders.kissmanga import KissManga
from Downloaders.Senmanga import SenManga

from pykakasi import kakasi, wakati

# Kivy strings
from kivy_strings import *


class MangaCheckBox(MDCheckbox):
    instances = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__class__.instances.append(self)
        self.active = False
        self.group = "group"
        self.check_btn = MDCheckbox(pos_hint={'center_x': .5, 'center_y': .5}, size=("48dp", "48dp"), size_hint=(None, None))
        self.checkbox_site = None
        self.allow_no_selection = False
        # self.add_widget(self.check_btn) # This line adds an extra checkbox, I am keeping here for reflection reason


class RightContentCls(RightContent):
    def __init__(self, checkbox_site, **kwargs):
        super().__init__(**kwargs)
        self.master = MDApp.get_running_app()
        #self.input_bar = MDApp.get_running_app().manga_search_page.input_bar
        self.check_btn = MangaCheckBox()
        self.check_btn.allow_no_selection = False
        self.checkbox_site = checkbox_site
        self.check_btn.checkbox_site = checkbox_site
        
        # This if statement needs to be here, so a toast wont appear when the app is opened
        if self.master.downloader == checkbox_site:
            self.check_btn.active = True
            #MangaSearchPage.downloader = self.checkbox_site
            self.master.downloader = self.checkbox_site
        self.check_btn.bind(active=self.checked)
        self.add_widget(self.check_btn)

    # This function gets run whenever, a checkbox is ticked or unticked
    def checked(self, checkbox, value):
        if value:
            self.master.downloader = self.checkbox_site
            toast(text=f"Manga will be searched on the site: {self.master.downloader}")
            #self.input_bar.focus = True
       

class MangaSearchPage(RelativeLayout):
    # downloader = None  # MDApp.get_running_app().default_downloader

    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.input_bar = self.ids.SearchFieldID
        self.input_bar.focus = True

        # Downloader related
        #self.query = self.ids.SearchFieldID.text
        self.query = self.input_bar.text
        self.downloader_sites = ["manganelo", "rawdevart", "kissmanga", "senmanga"]

        # Side menu
        icons = iter(["./Manga Site Logos/manga_nelo_icon.png", "./Manga Site Logos/rawdevart_logo.png","./Manga Site Logos/kissmanga_logo.png", "./Manga Site Logos/sen_manga_logo.png"])
        menu_items = [{"height": "70dp", "right_content_cls": RightContentCls(site), "icon": next(icons), "text": site} for site in self.downloader_sites]
        self.btn = MDRaisedButton(text="Manga sites", pos_hint={"center_x": .85, "center_y": .5})
        self.btn.bind(on_press=lambda x: self.menu.open())
        self.menu = MDDropdownMenu(caller=self.btn, items=menu_items, width_mult=4)
        self.menu.bind(on_release=self.menu_callback)
        self.add_widget(self.btn)

    def show_japanese_text(self):
        """
        kakasi_converter = kakasi()
        kakasi_converter.setMode("H","a") # Hiragana to ascii, default: no conversion
        kakasi_converter.setMode("K","a") # Katakana to ascii, default: no conversion
        kakasi_converter.setMode("J","a") # Japanese to ascii, default: no conversion
        kakasi_converter.setMode("s", True) # add space, default: no separator
        #kakasi_converter.setMode("C", True) # capitalize, default: no capitalize
        kakasi_converter.setMode("r","Hepburn") # default: use Hepburn Roman table
        text = self.ids.SearchFieldID.text
        text = text.encode("utf-8")
        conv = kakasi_converter.getConverter()
        result = conv.do(text)
        self.ids.SearchFieldID.text = result
        """
        pass

    # Had to install dev version for callback to work
    def menu_callback(self, instance_menu, instance_menu_item):
        for i in instance_menu_item.children:
            for j in i.children:
                for k in j.children:
                    #print(k, type(k))
                    if isinstance(k, MangaCheckBox):
                        if not k.active:
                            k.active = True
                            #MangaSearchPage.downloader = k.checkbox_site
                            self.master.downloader = k.checkbox_site
                        else:
                            k.active = False

    # This method is called within the kivy_strings.py file, on the event: on_text_validate
    def get_manga_query_data(self):
        self.master.input_query = self.input_bar.text

        # Manga Nelo only accepts english input:
        if self.master.downloader == "manganelo":
            os.chdir(self.master.english_manga_dir)
            self.manganelo = MangaNelo(self.input_bar.text)
            self.absract_get_query_data(self.manganelo)

        # Raw Dev Art accepts Japanese and English input
        elif self.master.downloader == "rawdevart":
            os.chdir(self.master.japanese_manga_dir)
            self.raw_dev_art = RawDevArt(self.input_bar.text)
            self.absract_get_query_data(self.raw_dev_art)

        # KissManga accepts Japanese and English input
        elif self.master.downloader == "kissmanga":
            os.chdir(self.master.english_manga_dir)
            self.kiss_manga = KissManga(self.input_bar.text)
            self.absract_get_query_data(self.kiss_manga)
            
        # Sen Manga accepts Japanese and English input
        elif self.master.downloader == "senmanga":
            os.chdir(self.master.japanese_manga_dir)
            self.sen_manga = SenManga(self.input_bar.text)
            self.absract_get_query_data(self.sen_manga)
        else:
            print("Error")
            toast(f"Error: No manga site called {self.master.downloader}")

    def absract_get_query_data(self, site_obj):
        #self.raw_dev_art = RawDevArt(self.ids.SearchFieldID.text)
        print(self.master.input_query, "in abs get query meth")
        if site_obj.hasErrorOccured == False:
            self.master.manga_data = site_obj.manga_data
            if not self.master.screen_manager.has_screen("Manga Showcase"):
                self.master.create_manga_display()

            # This bit acts as refresh for the manga cover display
            else:
                self.master.screen_manager.clear_widgets(screens=[self.master.screen_manager.get_screen("Manga Showcase")])
                self.master.create_manga_display()

            self.master.screen_manager.current = "Manga Showcase"
        else:
            toast(site_obj.popup_msg)
            #print(site_obj.popup_msg)
        self.input_bar.text = ""
        
# TODO:Have a file system with covers of the manga; user shouldnt be able to delete manga covers
# TODO: create JSON to store cover image and links. Should it be one file for all manga or one in each manga folder
# RelativeLayout

class MangaReadingPage(MDRelativeLayout):
    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master

        self.btn_text = ["Japanese (raw) Manga", "       English Manga          "]

        self.japanese_manga_btn = MDRectangleFlatButton(text=self.btn_text[0], pos_hint={"center_x":.5, "center_y":.6}, on_release=self.go_to_read_downloaded_manga)
        self.english_manga_btn = MDRectangleFlatButton(text=self.btn_text[1],pos_hint={"center_x":.5, "center_y":.4}, on_release=self.go_to_read_downloaded_manga)

        self.add_widget(self.japanese_manga_btn)
        self.add_widget(self.english_manga_btn)

    def go_to_read_downloaded_manga(self, inst):
        screen_name = "Downloaded Manga Showcase"
        # Japanese
        if inst.text == self.btn_text[0]:
            if not self.master.screen_manager.has_screen(screen_name):
                self.master.create_manga_read_display(language="Japanese")
            # This bit acts as refresh for the manga cover display
            else:
                self.master.screen_manager.clear_widgets(screens=[self.master.screen_manager.get_screen(screen_name)])
                self.master.create_manga_read_display(language="Japanese")
        # English
        elif inst.text == self.btn_text[1]:
            if not self.master.screen_manager.has_screen(screen_name):
                self.master.create_manga_read_display(language="English")
            # This bit acts as refresh for the manga cover display
            else:
                self.master.screen_manager.clear_widgets(screens=[self.master.screen_manager.get_screen(screen_name)])
                self.master.create_manga_read_display(language="English")
        self.master.screen_manager.current = screen_name
        

class MangaCoverTile(SmartTileWithLabel):
    instances = []
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__class__.instances.append(self)
        self.size_hint_y = None
        self.height = "240dp"
        self.font_style = "H6"

# Reading Manga Display
class DownloadedMangaDisplay(ScrollView):
    # master is used to reference the root app
    # language is used to display the download manga from that language (english or Japanese)
    def __init__(self, master,language, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.effect_cls = "ScrollEffect"
        self.scroll_type = ["bars"]
        self.bar_width = "10dp"
        self.pos_hint = {"top":.9}

        self.language_folder = self.master.japanese_manga_dir if language == "Japanese" else self.master.english_manga_dir

        self.manga_folders = [str(dir) for dir in Path(self.language_folder).glob("*/")]
        self.manga_cover_imgs = [str(img_path) for img_path in Path(self.language_folder).glob("*/*.jpg")]
        self.manga_tile_data = list(zip(self.manga_folders, self.manga_cover_imgs))

        # padding: [padding_left, padding_top, padding_right, padding_bottom]
        self.grid = MDGridLayout(cols=5,adaptive_height=True,padding=("30dp", "50dp", "30dp", "100dp"), spacing="20dp") #padding=("30dp", "5dp")

        for i in range(5):
            self.manga_num_label = MDLabel(pos_hint = {"center_x":.5,"center_y":1})
            if i == 3:
                self.manga_num_label.text = f"{len(self.manga_folders)} manga were found"
            self.grid.add_widget(self.manga_num_label)

        for i in self.manga_tile_data:
            title, manga_path = i[0].split("\\")[-1], i[0]
            self.btn = MangaCoverTile(source=i[1], text=title, on_release=partial(self.go_to_reader_chapter_selection, title, manga_path))
            self.grid.add_widget(self.btn)
        self.add_widget(self.grid)

    def go_to_reader_chapter_selection(self,title, manga_path,inst):
        #print("inst: ", inst, "title: ", title, "manga path", manga_path)
        # This bit acts as refresh for the manga cover display
        screen_name = "Manga Reader Chapter Selection"
        #if not self.master.screen_manager.has_screen("Manga Reader"):
        if not self.master.screen_manager.has_screen(screen_name):
            self.master.create_manga_reader_chapter_selection(title, manga_path)

        else:
            self.master.screen_manager.clear_widgets(screens=[self.master.screen_manager.get_screen(screen_name)])
            self.master.create_manga_reader_chapter_selection(title, manga_path)
        self.master.screen_manager.current = screen_name


# RelativeLayout
class LandingPage(RelativeLayout):
    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        # self.size_hint = (None, None)
        # DO NOT DELETE THE SPACES IN "Read Manga"
        self.btn_texts = ["Download Manga", "Read Manga          "]

        self.download_btn = MDRectangleFlatIconButton(text=self.btn_texts[0], icon="download-box",  pos_hint={"center_x": .5, "center_y": .4}, user_font_size="64sp", on_release=self.go_to_screen)
        self.read_btn = MDRectangleFlatIconButton(text=self.btn_texts[1], icon="book-open-page-variant", pos_hint={"center_x": .5, "center_y": .6}, user_font_size="64sp", on_release=self.go_to_screen)
        self.add_widget(self.read_btn)
        self.add_widget(self.download_btn)

    def go_to_screen(self, inst):
        self.master.screen_manager.current = 'Search page' if inst.text == "Download Manga" else 'Reading page'
        self.master.manga_search_page.ids["SearchFieldID"].focus = True if inst.text == "Download Manga" else False
        print(self.master.screen_manager.screen_names)        


"""
class MangaDownloader(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"

        self.root = Builder.load_file(os.path.join(".","KivyFiles","manga_input.kv"))

        self.screen_manager = ScreenManager()

        self.manga_search_page = MangaSearchPage(self)
        screen = Screen(name="Search page")
        screen.add_widget(self.manga_search_page)
        self.screen_manager.add_widget(screen)
        

        return self.screen_manager
        # return screen
"""
if __name__ == "__main__":
    MangaDownloader().run()
