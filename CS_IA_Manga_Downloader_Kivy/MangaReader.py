import os, plyer
from functools import partial
from glob import glob
from natsort import os_sorted # Windows can't sort alphanumerically, this module can

# Widgets
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.carousel import Carousel
from kivy.uix.scatter import Scatter, ScatterPlane
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRectangleFlatButton


# Layouts 
from kivymd.uix.relativelayout import MDRelativeLayout, RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivy.uix.scatterlayout import ScatterLayout
#from kivy.uix.relativelayout import RelativeLayout

# Utils and Properties
from utils import resource_path, kill_screen
from kivy.utils import platform

class MangaReaderChapterSelection(ScrollView):
    def __init__(self, master, title, manga_path, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.manga_path = resource_path(manga_path)
        self.manga_title = title
        self.effect_cls = "ScrollEffect"
        self.bar_width = "10dp"
        self.pos_hint = {"top":.9}
        self.padding=("20dp", "0dp", "20dp", "0dp") # padding: [padding_left, padding_top, padding_right, padding_bottom]
        
        # Get all the chapter directories and sort them alphanumerically
        self.chapter_dirs = os_sorted([os.path.abspath(resource_path(dir)) for dir in glob(os.path.join(self.manga_path,"*/")) if os.path.isdir(dir)])
        self.grid = MDStackLayout(adaptive_height=True,padding=("30dp", "50dp", "30dp", "0dp"), spacing="20dp", pos_hint={"center_x":.5})

        # Loop to create buttons for each chapter of a manga
        for chapter_dir in self.chapter_dirs:
            chapter_name = os.path.basename(resource_path(chapter_dir))
 
            def reload_func(manga_title = self.manga_title, name=chapter_name, path=chapter_dir):
                self.master.create_manga_reader(manga_title, name, path) 

            self.chapter_btn = MDRectangleFlatButton(text=chapter_name, pos_hint={"center_x":.5, "center_y":.8}, 
                on_release = partial(kill_screen, "Manga Reader Carousel", reload_func),
            )
            self.grid.add_widget(self.chapter_btn)
        self.add_widget(self.grid)

class ZoomableImage(ScatterPlane):
    def __init__(self, image_src, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=Clock.schedule_once(self.center_it))
        self.image_src = resource_path(image_src)
        self.do_translation = self.do_rotation = False 
        self.do_scale = True 
        self.scale = self.scale_min= 5
        self.scale_max= 16
        self.size_hint=(None,None)
        self.add_widget(Image(source = resource_path(self.image_src), keep_ratio = False, allow_stretch = True, nocache=True))
        
        Clock.schedule_once(self.center_it)

    def center_it(self, inst):
        self.center = self.parent.center

    def on_touch_down(self, touch):
        # Override Scatter's `on_touch_down` behavior for mouse scroll
        if touch.is_mouse_scrolling:
            if touch.button == 'scrolldown' and self.scale < 10: self.scale = self.scale * 1.1
            
            elif touch.button == 'scrollup' and self.scale > 1: self.scale = self.scale * 0.8
        # If some other kind of "touch": Fall back on Scatter's behavior
        else:
            super().on_touch_down(touch)
    
class MangaCarousel(Carousel):
    def __init__(self, direction, **kwargs):
        super().__init__(**kwargs)
        self.direction = direction

    def on_index(self, *args, **kwargs):
        for child in self.current_slide.walk_reverse(loopback=True):
            if isinstance(child, ZoomableImage):
                child.scale = child.scale_min
                Clock.schedule_once(child.center_it)
        super().on_index(*args, **kwargs)


class MangaReaderCarouselContainer(AnchorLayout):
    def __init__(self, master, manga_title,chapter_name,chapter_path,**kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.manga_title = manga_title
        self.chapter_name = chapter_name
        self.chapter_path = chapter_path
        self.padding=("0dp", "100dp", "0dp", "20dp") # padding: [padding_left, padding_top, padding_right, padding_bottom]
        
        self.chapter_imgs = os_sorted([
            resource_path(img) for img in glob(os.path.join(self.chapter_path, "*")) 
            if os.path.isfile(resource_path(img)) and not resource_path(img).endswith(".txt")    
        ])

        # Debug:
        if platform == "android":
            print(f"Chapter images of {self.manga_title}: {self.chapter_imgs}")
        
        self.swiping_direction = "left" if self.master.manga_swiping_direction == "Left to Right (Japanese style)" else "right"
        self.reading_direction = "bottom" if self.master.manga_reading_direction == "Scroll vertically" else self.swiping_direction
        
        #self.carousel = Carousel(direction=self.reading_direction)
        self.carousel = MangaCarousel(direction=self.reading_direction)
        
        
        for index, img in enumerate(self.chapter_imgs):
            self.scatter = ZoomableImage(image_src=str(img))

            self.inner_carousel_layout = MDRelativeLayout()#size=self.scatter.size)
            self.inner_carousel_layout.add_widget(MDLabel(text=f"Page {index + 1}/{len(self.chapter_imgs)}", pos_hint={"top":.6}))
            
            self.inner_carousel_layout.add_widget(self.scatter)
            self.carousel.add_widget(self.inner_carousel_layout)
     
            #self.prev_btn = MDIconButton(icon="menu-left", user_font_size ="200sp", on_release = lambda *x:self.turn_page(self.carousel.load_previous), pos_hint={"center_x":.1, "center_y":.5}) 
            #self.next_btn = MDIconButton(icon="menu-right", user_font_size ="200sp", on_release = lambda *x:self.turn_page(self.carousel.load_next), pos_hint={"center_x":.9, "center_y":.5})

            self.prev_btn = MDIconButton(icon="menu-left", user_font_size ="200sp", on_release = lambda *x :self.carousel.load_previous(), pos_hint={"center_x":.1, "center_y":.5}) 
            self.next_btn = MDIconButton(icon="menu-right", user_font_size ="200sp", on_release = lambda *x:self.carousel.load_next(), pos_hint={"center_x":.9, "center_y":.5})
            
            # Changes the way the arrows load the pages depending on the reading direction
            # True/left --> Left to right (left)  JP ; False/right --> Right to left (right) EN
            if self.swiping_direction == "left" and self.reading_direction != "bottom":
                self.prev_btn = MDIconButton(icon="menu-left", user_font_size ="200sp", on_release = lambda *x:self.carousel.load_next(), pos_hint={"center_x":.1, "center_y":.5}) 
                self.next_btn = MDIconButton(icon="menu-right", user_font_size ="200sp", on_release = lambda *x:self.carousel.load_previous(), pos_hint={"center_x":.9, "center_y":.5}) 
                #self.prev_btn = MDIconButton(icon="menu-left", user_font_size ="200sp", on_release = lambda *x:self.turn_page(self.carousel.load_next), pos_hint={"center_x":.1, "center_y":.5}) 
                #self.next_btn = MDIconButton(icon="menu-right", user_font_size ="200sp", on_release = lambda *x:self.turn_page(self.carousel.load_previous), pos_hint={"center_x":.9, "center_y":.5}) 

            if platform != "android": 
                self.inner_carousel_layout.add_widget(self.prev_btn)
                self.inner_carousel_layout.add_widget(self.next_btn)

        #self.carousel.bind(on_index = self.turn)
        self.add_widget(self.carousel)

    # Resets the image's zoom whenever a new page is loaded
    def turn_page(self, callback ,*args, **kwargs):
        print(f"args: {args} \n kwargs: {kwargs}")
        print(self.carousel, " carousel ")
        for child in self.carousel.current_slide.walk_reverse(loopback=True):
            if isinstance(child, ZoomableImage):
                print("child: ",child, "scale before: ", child.scale)
                child.scale = child.scale_min
                print("child.scale after: ", child.scale, "min scale: ", child.scale_min)
                
        callback()
        
        
                
