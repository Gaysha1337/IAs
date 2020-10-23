from functools import partial
import os
from os.path import isfile
from pathlib import Path
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage, Image
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.uix.stacklayout import StackLayout
from kivymd.uix.boxlayout import MDBoxLayout

from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton, MDRectangleFlatButton, MDRectangleFlatIconButton

from kivymd.uix.gridlayout import GridLayout, MDGridLayout
from kivymd.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout

from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.lang import Builder
from kivy.utils import platform  # Used to tell if platform is android


class MangaReaderChapterSelection(MDBoxLayout):
    def __init__(self, master, title, manga_path, **kwargs):
        super().__init__(**kwargs)
        # padding: [padding_left, padding_top, padding_right, padding_bottom]
        self.padding=("20dp", "0dp", "20dp", "0dp")
        self.spacing = "100dp"
        self.master = master
        self.manga_path = manga_path
        self.manga_title = title
        self.chapter_dirs = [dir for dir in Path(self.manga_path).glob("*/") if os.path.isdir(dir)]

        for index, chapter_dir in enumerate(self.chapter_dirs):
            chapter_name = os.path.basename(chapter_dir)
            chapter_imgs = Path(chapter_dir).glob("*")
            #print("last file", max(chapter_imgs))

            self.chapter_btn = MDRectangleFlatButton(text=chapter_name, pos_hint={"center_x":.5, "center_y":.8}, on_release = partial(self.load_chapter_imgs,self.manga_title,chapter_name,chapter_dir))
            #print(self.chapter_btn.path)
            self.add_widget(self.chapter_btn)

    def load_chapter_imgs(self, manga_title,chapter_name,chapter_path,*args):
        screen_name = "Manga Reader"
        #if not self.master.screen_manager.has_screen("Manga Reader"):
        if not self.master.screen_manager.has_screen(screen_name):
            self.master.create_manga_reader(manga_title,chapter_name, chapter_path)

        else:
            self.master.screen_manager.clear_widgets(screens=[self.master.screen_manager.get_screen(screen_name)])
            self.master.create_manga_reader(manga_title,chapter_name, chapter_path)
        self.master.screen_manager.current = screen_name


class MangaReaderCarousel(AnchorLayout):
    def __init__(self, master, manga_title,chapter_name,chapter_path,**kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.manga_title = manga_title
        self.chapter_name = chapter_name
        self.chapter_path = chapter_path
        
        #self.chapter_dirs = [dir for dir in Path(self.chapter_path).glob("*/") if os.path.isdir(dir)]
        self.chapter_imgs = [img for img in Path(self.chapter_path).glob("*") if os.path.isfile(img)]
        # padding: [padding_left, padding_top, padding_right, padding_bottom]
        self.padding=("0dp", "100dp", "0dp", "10dp")

        print("reading dir:",self.master.manga_reading_direction, " car self.swiping dir: ,", self.master.manga_swiping_direction)
        # True --> Right to left (left) ; False --> Left to right (right)
        self.swiping_direction = "left" if self.master.manga_swiping_direction else "right"
        # True--> vertical ; False--> Horizontal
        self.reading_direction = "bottom" if self.master.manga_reading_direction else self.swiping_direction

        print(" car reading dir:",self.reading_direction, " car self.swiping dir: ,", self.swiping_direction)
        self.carousel = Carousel(direction=self.reading_direction)
        """
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
        """
        self.title_label, self.chapter_label, self.page_label = MDLabel(text=self.manga_title), MDLabel(), MDLabel()
        
        """
        for chapter_dir in self.chapter_dirs:
            chapter_name = os.path.basename(chapter_dir)
            chapter_imgs = Path(chapter_dir).glob("*")
            #print("last file", max(chapter_imgs)) 
            for img in chapter_imgs:
                #print(index + 1, "index #")
                image = Image(source=str(img), allow_stretch=True)
                self.inner_carousel_layout = MDRelativeLayout()
                self.inner_carousel_layout.add_widget(image)
                self.carousel.add_widget(self.inner_carousel_layout)

                # If the reading direction is horizontal add some arrow buttons to easily turn pages
                if self.reading_direction != "bottom":
                    self.prev_btn = MDIconButton(icon="menu-left", user_font_size ="200sp", on_release = lambda x:self.carousel.load_previous(), pos_hint={"center_x":.1, "center_y":.5}) # pos_hint={"left":.2, "y":.5},
                    self.next_btn = MDIconButton(icon="menu-right", user_font_size ="200sp", on_release = lambda x:self.carousel.load_next(), pos_hint={"center_x":.9, "center_y":.5}) # pos_hint={"right":.8, "y":.5}
                    self.inner_carousel_layout.add_widget(self.prev_btn)
                    self.inner_carousel_layout.add_widget(self.next_btn)
                
            break
        """

        for img in self.chapter_imgs:
            image = Image(source=str(img), allow_stretch=True)
            self.inner_carousel_layout = MDRelativeLayout()
            self.inner_carousel_layout.add_widget(image)
            self.carousel.add_widget(self.inner_carousel_layout)

            # If the reading direction is horizontal add some arrow buttons to easily turn pages
            if self.reading_direction != "bottom":
                self.prev_btn = MDIconButton(icon="menu-left", user_font_size ="200sp", on_release = lambda x:self.carousel.load_previous(), pos_hint={"center_x":.1, "center_y":.5}) # pos_hint={"left":.2, "y":.5},
                self.next_btn = MDIconButton(icon="menu-right", user_font_size ="200sp", on_release = lambda x:self.carousel.load_next(), pos_hint={"center_x":.9, "center_y":.5}) # pos_hint={"right":.8, "y":.5}
                self.inner_carousel_layout.add_widget(self.prev_btn)
                self.inner_carousel_layout.add_widget(self.next_btn)
            
        self.add_widget(self.carousel)

    def load_next_chapter(self):
        self.carousel.load_next()

    def load_prev_chapter(self):
        pass

            
if __name__ == "__main__":
    from pathlib import WindowsPath
    reading_dir = ""