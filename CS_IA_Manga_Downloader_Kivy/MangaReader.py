import os, plyer
from pathlib import Path
from functools import partial

# Widgets
from kivymd.app import MDApp
from kivy.uix.carousel import Carousel
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivymd.uix.label import MDLabel

from kivymd.uix.button import MDIconButton, MDRectangleFlatButton

# Layouts 
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.anchorlayout import AnchorLayout

# Utils and Properties
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.lang import Builder
from kivy.utils import platform  # Used to tell if platform is android
from kivy.core.window import Window

from natsort import os_sorted # Windows can't sort alphanumerically, this module can


class MangaReaderChapterSelection(ScrollView):
    def __init__(self, master, title, manga_path, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.effect_cls = "ScrollEffect"
        self.scroll_type = ["bars"]
        self.bar_width = "10dp"
        self.pos_hint = {"top":.9}
    
        # padding: [padding_left, padding_top, padding_right, padding_bottom]
        self.padding=("20dp", "0dp", "20dp", "0dp")
        #self.spacing = "100dp"
        
        self.manga_path = manga_path
        self.manga_title = title
        # Get all the chapter directories and sort them alphanumerically
        self.chapter_dirs = os_sorted([str(dir) for dir in Path(self.manga_path).glob("*/") if os.path.isdir(dir)])
        self.grid = MDGridLayout(cols=5,adaptive_height=True,padding=("30dp", "30dp", "30dp", "0dp"), spacing="20dp", pos_hint={"center_x":.5})#, pos_hint={"right":.5}) #padding=("30dp", "5dp")
        #self.grid = AnchorLayout(anchor_x="left",anchor_y="top",padding=("30dp", "30dp", "30dp", "0dp"))#, pos_hint={"right":.5}) #padding=("30dp", "5dp")

        for index, chapter_dir in enumerate(self.chapter_dirs):
            chapter_name = os.path.basename(chapter_dir)
            #chapter_imgs = Path(chapter_dir).glob("*")

            self.chapter_btn = MDRectangleFlatButton(text=chapter_name,pos_hint={"center_x":.5, "center_y":.8}, on_release = partial(self.load_chapter_imgs,self.manga_title,chapter_name,chapter_dir))
            self.grid.add_widget(self.chapter_btn)
        self.add_widget(self.grid)

    def load_chapter_imgs(self, manga_title,chapter_name,chapter_path,*args):
        screen_name = "Manga Reader Carousel"
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
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        self.master = master
        self.chapter_parent_dir = os.path.dirname(chapter_path)
        self.manga_title = manga_title
        self.chapter_name = chapter_name
        self.chapter_path = chapter_path
        self.all_chapter_paths = sorted([dir for dir in Path(os.path.dirname(self.chapter_path)).glob("*/") if os.path.isdir(dir)])


        #self.chapter_dirs = [dir for dir in Path(self.chapter_path).glob("*/") if os.path.isdir(dir)]
        self.chapter_imgs = [img for img in Path(self.chapter_path).glob("*") if os.path.isfile(img) and not str(img).endswith(".txt")]
        # padding: [padding_left, padding_top, padding_right, padding_bottom]
        self.padding=("0dp", "100dp", "0dp", "20dp")

        #self.swiping_direction, self.reading_direction = self.master.swiping_direction, self.master.reading_direction
        #print("reading dir:",self.master.manga_reading_direction, " car self.swiping dir: ,", self.master.manga_swiping_direction)
        
        # True --> Left to right (left)  JP ; False --> Right to left (right) EN
        #self.swiping_direction = "left" if self.master.manga_swiping_direction else "right"
        self.swiping_direction = "left" if self.master.manga_swiping_direction == "Left to Right (Japanese style)" else "right"
        
        # True--> vertical ; False--> Horizontal
        #self.reading_direction = "bottom" if self.master.manga_reading_direction else self.swiping_direction
        self.reading_direction = "bottom" if self.master.manga_reading_direction == "Scroll vertically" else self.swiping_direction

        #print(" car reading dir:",self.reading_direction, " car self.swiping dir: ,", self.swiping_direction)
        self.carousel = Carousel(direction=self.reading_direction)
        
        for index, img in enumerate(self.chapter_imgs):
            image = Image(source=str(img), allow_stretch=True)
            self.inner_carousel_layout = MDRelativeLayout()
            self.inner_carousel_layout.add_widget(MDLabel(text=f"Page {index + 1}/{len(self.chapter_imgs)}", pos_hint={"top":.6}))
            
            self.inner_carousel_layout.add_widget(image)
            self.carousel.add_widget(self.inner_carousel_layout)

            # If the reading direction is horizontal add some arrow buttons to easily turn pages
            if self.reading_direction: #!= "bottom":
                
                self.prev_btn = MDIconButton(icon="menu-left", user_font_size ="200sp", on_release = lambda x:self.carousel.load_previous(), pos_hint={"center_x":.1, "center_y":.5}) # pos_hint={"left":.2, "y":.5},
                self.next_btn = MDIconButton(icon="menu-right", user_font_size ="200sp", on_release = lambda x:self.carousel.load_next(), pos_hint={"center_x":.9, "center_y":.5}) # pos_hint={"right":.8, "y":.5}
                
                # Changes the way the arrows load the pages depending on the reading direction
                # True/left --> Left to right (left)  JP ; False/right --> Right to left (right) EN
                if self.swiping_direction == "left" and self.reading_direction != "bottom":
                    self.prev_btn = MDIconButton(icon="menu-left", user_font_size ="200sp", on_release = lambda x:self.carousel.load_next(), pos_hint={"center_x":.1, "center_y":.5}) # pos_hint={"left":.2, "y":.5},
                    self.next_btn = MDIconButton(icon="menu-right", user_font_size ="200sp", on_release = lambda x:self.carousel.load_previous(), pos_hint={"center_x":.9, "center_y":.5}) # pos_hint={"right":.8, "y":.5}
                    
                self.inner_carousel_layout.add_widget(self.prev_btn)
                self.inner_carousel_layout.add_widget(self.next_btn)
            
        self.add_widget(self.carousel)

    # Keyboard methods
    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print('The key', keycode, 'have been pressed', ' - text is %r' % text, ' - modifiers are %r' % modifiers, sep="\n")
 
        if keycode[1] == "right" or keycode[1] == "down":
            self.next_btn.trigger_action(0)
        if keycode[1] == "left" or keycode[1] == "up":
            self.prev_btn.trigger_action(0)
        # Return True to accept the key. Otherwise, it will be used by the system.
        return True
