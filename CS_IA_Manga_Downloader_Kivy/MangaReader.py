import os, plyer
from functools import partial
from glob import glob
from natsort import os_sorted # Windows can't sort alphanumerically, this module can

# Widgets
from kivy.uix.carousel import Carousel
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRectangleFlatButton

# Layouts 
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.stacklayout import MDStackLayout

# Utils and Properties
from utils import resource_path, kill_screen

class MangaReaderChapterSelection(ScrollView):
    def __init__(self, master, title, manga_path, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.manga_path = manga_path
        self.manga_title = title
        self.effect_cls = "ScrollEffect"
        self.scroll_type = ["bars"]
        self.bar_width = "10dp"
        self.pos_hint = {"top":.9}
        self.padding=("20dp", "0dp", "20dp", "0dp") # padding: [padding_left, padding_top, padding_right, padding_bottom]
        
        # Get all the chapter directories and sort them alphanumerically
        self.chapter_dirs = os_sorted([os.path.abspath(dir) for dir in glob(os.path.join(self.manga_path,"*/")) if os.path.isdir(dir)])
        
        self.grid = MDStackLayout(adaptive_height=True,padding=("30dp", "50dp", "30dp", "0dp"), spacing="20dp", pos_hint={"center_x":.5})#, pos_hint={"right":.5}) #padding=("30dp", "5dp")
        
        # Loop to create buttons for each chapter of a manga
        for chapter_dir in self.chapter_dirs:
            chapter_name = os.path.basename(chapter_dir)
            reload_func = lambda manga_title = self.manga_title, name=chapter_name, path=chapter_dir: self.master.create_manga_reader(manga_title, name, path)

            self.chapter_btn = MDRectangleFlatButton(
                text=chapter_name,
                pos_hint={"center_x":.5, "center_y":.8}, 
                #on_release = partial(self.load_chapter_imgs,self.manga_title,chapter_name,chapter_dir)
                on_release = partial(kill_screen, "Manga Reader Carousel", reload_func)
            )
            self.grid.add_widget(self.chapter_btn)
        self.add_widget(self.grid)

    
    def load_chapter_imgs(self, manga_title, name, path, *args):
        screen_name = "Manga Reader Carousel"
        if not self.master.screen_manager.has_screen(screen_name):
            self.master.create_manga_reader(manga_title, name, path)
        else:
            self.master.screen_manager.clear_widgets(screens=[self.master.screen_manager.get_screen(screen_name)])
            self.master.create_manga_reader(manga_title, name, path)
        self.master.screen_manager.current = screen_name

class MangaReaderCarousel(AnchorLayout):
    def __init__(self, master, manga_title,chapter_name,chapter_path,**kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.manga_title = manga_title
        self.chapter_name = chapter_name
        self.chapter_path = chapter_path
        self.padding=("0dp", "100dp", "0dp", "20dp") # padding: [padding_left, padding_top, padding_right, padding_bottom]
        self.chapter_imgs = [os.path.abspath(img) for img in glob(os.path.join(self.chapter_path, "*")) if os.path.isfile(img) and not str(img).endswith(".txt")]
        
        
        self.swiping_direction = "left" if self.master.manga_swiping_direction == "Left to Right (Japanese style)" else "right"
        self.reading_direction = "bottom" if self.master.manga_reading_direction == "Scroll vertically" else self.swiping_direction
        
        self.carousel = Carousel(direction=self.reading_direction)
        
        for index, img in enumerate(self.chapter_imgs):
            image = Image(source=str(img), allow_stretch=True, keep_ratio=True)
            self.inner_carousel_layout = MDRelativeLayout()
            self.inner_carousel_layout.add_widget(MDLabel(text=f"Page {index + 1}/{len(self.chapter_imgs)}", pos_hint={"top":.6}))
            
            self.inner_carousel_layout.add_widget(image)
            self.carousel.add_widget(self.inner_carousel_layout)
     
            self.prev_btn = MDIconButton(icon="menu-left", user_font_size ="200sp", on_release = lambda *x:self.carousel.load_previous(), pos_hint={"center_x":.1, "center_y":.5}) # pos_hint={"left":.2, "y":.5},
            self.next_btn = MDIconButton(icon="menu-right", user_font_size ="200sp", on_release = lambda *x:self.carousel.load_next(), pos_hint={"center_x":.9, "center_y":.5}) # pos_hint={"right":.8, "y":.5}
            
            # Changes the way the arrows load the pages depending on the reading direction
            # True/left --> Left to right (left)  JP ; False/right --> Right to left (right) EN
            if self.swiping_direction == "left" and self.reading_direction != "bottom":
                self.prev_btn = MDIconButton(icon="menu-left", user_font_size ="200sp", on_release = lambda *x:self.carousel.load_next(), pos_hint={"center_x":.1, "center_y":.5}) # pos_hint={"left":.2, "y":.5},
                self.next_btn = MDIconButton(icon="menu-right", user_font_size ="200sp", on_release = lambda *x:self.carousel.load_previous(), pos_hint={"center_x":.9, "center_y":.5}) # pos_hint={"right":.8, "y":.5}
                
            self.inner_carousel_layout.add_widget(self.prev_btn)
            self.inner_carousel_layout.add_widget(self.next_btn)
        self.add_widget(self.carousel)