# Program to explain how to use recycleview in kivy
import os
# import the kivy module
from kivymd.app import MDApp
from kivy.properties import ListProperty, DictProperty
from kivy.uix.boxlayout import BoxLayout


from kivymd.uix.button import MDRectangleFlatButton, MDIconButton, MDRectangleFlatIconButton

from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.uix.relativelayout import RelativeLayout

from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.uix.button import MDIconButton

from functools import partial
from kivy.utils import platform  # Used to tell if platform is android

from Downloaders.manga_nelo_OOP import MangaNelo
from kivy.network.urlrequest import UrlRequest

# The ScrollView widget provides a scrollable view
from kivy.uix.recycleview import RecycleView
from kivy.uix.scrollview import ScrollView
from kivymd.stiffscroll import StiffScrollEffect

from kivy.lang import Builder


from kivy_strings import manga_display_kv_str


"""
manga_data_list = [
    {'chapter_number': 1, 'chapter_name': 'Dark Blood Age Chapter 1', 'img_links': [
        'https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_1/1.jpg']},
    {'chapter_number': 2, 'chapter_name': 'Dark Blood Age Chapter 2', 'img_links': [
        'https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_2/1.jpg']},
    {'chapter_number': 3, 'chapter_name': 'Dark Blood Age Chapter 3', 'img_links': [
        'https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_3/1.jpg']},
    {'chapter_number': 4, 'chapter_name': 'Dark Blood Age Chapter 4', 'img_links': [
        'https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_4/1.jpg']},
    {'chapter_number': 5, 'chapter_name': 'Dark Blood Age Chapter 5', 'img_links': [
        'https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_5/1.jpg', 'https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_5/2.jpg']},
    {'chapter_number': 6, 'chapter_name': 'Dark Blood Age Chapter 6', 'img_links': [
        'https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_6/1.jpg']},
    {'chapter_number': 7, 'chapter_name': 'Dark Blood Age Chapter 7', 'img_links': [
        'https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_7/1.jpg', 'https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_7/2.jpg']},
    {'chapter_number': 8, 'chapter_name': 'Dark Blood Age Chapter 8', 'img_links': ['https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_8/1.jpg']}, {'chapter_number': 9, 'chapter_name': 'Dark Blood Age Chapter 9', 'img_links': ['https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_9/1.jpg', 'https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_9/2.jpg']}, {'chapter_number': 10, 'chapter_name': 'Dark Blood Age Chapter 10', 'img_links': ['https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_10/1.jpg']}, {'chapter_number': 11, 'chapter_name': 'Dark Blood Age Chapter 11', 'img_links': ['https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_11/1.jpg']}, {'chapter_number': 12, 'chapter_name': 'Dark Blood Age Chapter 12', 'img_links': ['https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_12/1.jpg', 'https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_12/2.jpg']}, {'chapter_number': 13, 'chapter_name': 'Dark Blood Age Chapter 13', 'img_links': ['https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_13/1.jpg']}, {'chapter_number': 14, 'chapter_name': 'Dark Blood Age Chapter 14', 'img_links': ['https://s5.mkklcdnv5.com/mangakakalot/s2/ss923461/chapter_14/1.jpg']}, {'chapter_number': 15, 'chapter_name': 'Dark Blood Age Chapter 15', 'img_links': ['https://s8.mkklcdnv8.com/mangakakalot/s2/ss923461/chapter_15/1.jpg', 'https://s8.mkklcdnv8.com/mangakakalot/s2/ss923461/chapter_15/2.jpg']}, {'chapter_number': 16, 'chapter_name': 'Dark Blood Age Chapter 16', 'img_links': ['https://s8.mkklcdnv8.com/mangakakalot/s2/ss923461/chapter_16/1.jpg']}, {'chapter_number': 17, 'chapter_name': 'Dark Blood Age Chapter 17', 'img_links': ['https://s8.mkklcdnv8.com/mangakakalot/s2/ss923461/chapter_17/1.jpg', 'https://s8.mkklcdnv8.com/mangakakalot/s2/ss923461/chapter_17/2.jpg']}, {'chapter_number': 18, 'chapter_name':
'Dark Blood Age Chapter 18', 'img_links': ['https://s8.mkklcdnv8.com/mangakakalot/s2/ss923461/chapter_18/1.jpg']}, {'chapter_number': 19, 'chapter_name': 'Dark Blood Age Chapter 19', 'img_links': ['https://s8.mkklcdnv8.com/mangakakalot/s2/ss923461/chapter_19/1.jpg']}, {'chapter_number': 20, 'chapter_name': 'Dark Blood Age Chapter 20', 'img_links': ['https://s8.mkklcdnv8.com/mangakakalot/s2/ss923461/chapter_20/1.jpg', 'https://s8.mkklcdnv8.com/mangakakalot/s2/ss923461/chapter_20/2.jpg']}, {'chapter_number': 21, 'chapter_name': 'Dark Blood Age Chapter 21', 'img_links': ['https://s8.mkklcdnv8.com/mangakakalot/s2/ss923461/chapter_21/1.jpg']}, {'chapter_number': 22, 'chapter_name': 'Dark Blood Age Chapter 22', 'img_links': ['https://s8.mkklcdnv8.com/mangakakalot/s2/ss923461/chapter_22/1.jpg']}
]"""
# Define the Recycleview class which is created in .kv file


class RV(RecycleView):
    manga_data = DictProperty(None)

    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        print(MDApp.get_running_app().manga_data, "in RV class in init")
        #self.effect_cls = StiffScrollEffect

        self.data = [
            {
                'text': str(x),
                'source': self.manga_data.get(x)[1],
                'on_release': partial(self.make_request, x),
                'pos_hint': {'center_x': .5, 'center_y': .5}
            }
            for x in self.manga_data
        ]
        #print(self.manga_data, "in RV class")

    def make_request(self, title):
        print(title, self.manga_data.get(title))
        MangaNelo.download_manga(title, self.manga_data.get(title))

        """
		# print(self.properties().get("manga_data"), "parent: running from self.butt in RV")
		for i in x.get('img_links'):
			# print('button', x.get('img_links'), 'pressed')
			print('button', i, 'pressed')
		"""


class MangaCoverTile(SmartTileWithLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = "240dp"


class MangaCoverContainer(ScrollView):
    def __init__(self, master,**kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.manga_data = MDApp.get_running_app().manga_data
        #self.rel = MDRelativeLayout()
        self.grid = MDGridLayout(cols=5, adaptive_height=True, padding=("4dp", "4dp"), spacing="4dp")
        #self.rel.add_widget(self.grid)

        for title, links_tuple in self.manga_data.items():
            print(title, "in for loop this val is cover", " v val: ", links_tuple)
            self.btn = MangaCoverTile(source=links_tuple[1], text=title)
            self.grid.add_widget(self.btn)
        self.add_widget(self.grid)


if __name__ == "__main__":
    Builder.load_string(manga_display_kv_str)

    class MangaScreen(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.settings_btn = MDIconButton(icon="cog", pos_hint={
                                             "center_x": .9, "center_y": .9}, user_font_size="64sp", on_press=lambda inst: MDApp.get_running_app().open_settings())
            # self.settings_btn.bind(on_press = lambda inst: MangaDownloader.get_running_app().open_settings())
            self.add_widget(self.settings_btn)

            self.home_btn = MDIconButton(icon="home", pos_hint={
                                         "center_x": .1, "center_y": .9}, user_font_size="64sp")
            self.home_btn.bind(on_press=self.go_to_home_screen)
            self.add_widget(self.home_btn)

        def go_to_home_screen(self, inst):
            self.manager.current = "Search page"

    class MyApp(MDApp):
        def build(self):
            self.manager = ScreenManager()
            self.rv = RV(self)
            screen = MangaScreen(name="RV")
            screen.add_widget(self.rv)
            self.manager.add_widget(screen)

            return self.manager
    MyApp().run()
