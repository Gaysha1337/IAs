from functools import partial
import os
import sys
from pathlib import Path
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.uix.scrollview import ScrollView
from kivymd.uix.filemanager import MDFileManager
from kivymd.app import MDApp
from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout

from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDRectangleFlatButton, MDRectangleFlatIconButton

from kivymd.uix.snackbar import Snackbar
from kivymd.toast import toast
#from kivymd.toast.kivytoast import toast
from kivymd.toast.kivytoast.kivytoast import Toast


from kivymd.uix.gridlayout import GridLayout, MDGridLayout
from kivymd.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout

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

class MangaReaderCarousel(AnchorLayout):
    def __init__(self, master, manga_path,**kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.manga_path = manga_path
        self.padding=("0dp", "50dp", "0dp", "10dp")

        # True --> Right to left (left) ; False --> Left to right (right)
        self.swiping_direction = "left" if self.master.manga_swiping_direction == 1 else "right"
        # True--> vertical ; False--> Horizontal
        self.reading_direction = "bottom" if self.master.manga_reading_direction == 1 else self.swiping_direction

        self.carousel = Carousel(direction=self.reading_direction)
        for i in range(10):
            src = "https://i.imgur.com/x7WdmHBb.jpg"
            image = AsyncImage(source=src, allow_stretch=True)
            self.inner_carousel_layout = MDRelativeLayout()
            self.inner_carousel_layout.add_widget(image)

            if self.reading_direction != "bottom":
                self.prev_btn = MDIconButton(icon="menu-left", user_font_size ="200sp", on_release = lambda x:self.carousel.load_previous(), pos_hint={"center_x":.1, "center_y":.5}) # pos_hint={"left":.2, "y":.5},
                self.next_btn = MDIconButton(icon="menu-right", user_font_size ="200sp", on_release = lambda x:self.carousel.load_next(), pos_hint={"center_x":.9, "center_y":.5}) # pos_hint={"right":.8, "y":.5}
                self.inner_carousel_layout.add_widget(self.prev_btn)
                self.inner_carousel_layout.add_widget(self.next_btn)

            self.carousel.add_widget(self.inner_carousel_layout)
        self.add_widget(self.carousel)

        """
        print("reading dir", self.reading_direction)
        if self.reading_direction != "bottom":
            print("in if")
            self.prev_btn = MDIconButton(icon="arrow-left-bold", user_font_size ="64sp", pos_hint={"center_x":.2}, on_release = lambda x:self.carousel.load_previous())
            self.next_btn = MDIconButton(icon="arrow-right-bold", user_font_size ="64sp",  pos_hint={"center_x":.8}, on_release = lambda x:self.carousel.load_next())
            self.add_widget(self.prev_btn)
            self.add_widget(self.next_btn)"""

             

if __name__ == "__main__":
    MangaDownloader().run()
