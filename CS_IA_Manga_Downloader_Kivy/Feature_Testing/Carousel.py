from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.button import MDIconButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.label import MDLabel


class ToolBar(MDToolbar):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.title = "Manga Downloader"
        self.id = "Toolbar"
        self.pos_hint = {"top":1}
        self.elevation = 10
        self.left_action_items = [["cog", lambda x: print("inweuid")]]
        self.right_action_items = [["home", lambda x: print("hwrihwkedwh")]]
        
    def go_to_home_screen(self, inst):
        #self.manager.current = "Landing Page"
        #MDApp.get_running_app().screen_manager.current = "Landing Page"
        print("hiwhr")

class MangaScreen(Screen): 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
           
    def on_pre_enter(self, *args, **kwargs):
        self.toolbar = ToolBar(title="Manga Downloader")#{"center_y":.955} , pos_hint={"top":1}
        self.toolbar.left_action_items = [["cog", lambda x: print("inejof")]]
        self.toolbar.right_action_items = [["home", lambda x: print("inejof")]]
        self.add_widget(self.toolbar) 


# TODO: Create a class which shows an image and two buttons each side make it a relative layout

class ImgCarousel(AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # padding: [padding_left, padding_top, padding_right, padding_bottom]
        self.padding=("0dp", "50dp", "0dp", "10dp")
        self.carousel = Carousel(direction='right')
        #self.carousel.pos_hint = {"top":.9}
        for i in range(10):
            src = "https://i.imgur.com/x7WdmHBb.jpg"
            image = AsyncImage(source=src, allow_stretch=True)
            self.inner_carousel_layout = MDRelativeLayout()
            self.prev_btn = MDIconButton(icon="menu-left", user_font_size ="200sp", on_release = lambda x:self.carousel.load_previous(), pos_hint={"center_x":.1, "center_y":.5}) # pos_hint={"left":.2, "y":.5},
            self.next_btn = MDIconButton(icon="menu-right", user_font_size ="200sp", on_release = lambda x:self.carousel.load_next(), pos_hint={"center_x":.9, "center_y":.5}) # pos_hint={"right":.8, "y":.5}

            self.inner_carousel_layout.add_widget(image)
            self.inner_carousel_layout.add_widget(self.prev_btn)
            self.inner_carousel_layout.add_widget(self.next_btn)
            self.carousel.add_widget(self.inner_carousel_layout)
        self.add_widget(self.carousel)
        

class CarouselApp(MDApp):
    def build(self):
        self.manager = ScreenManager()
        self.carousel = ImgCarousel()
        screen = MangaScreen(name="carousel screen")
        screen.add_widget(self.carousel)
        self.manager.add_widget(screen)
        return self.manager


CarouselApp().run()