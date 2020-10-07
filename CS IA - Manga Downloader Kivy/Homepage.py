import os
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton

from kivymd.uix.snackbar import Snackbar
from kivymd.toast import toast

from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.gridlayout import GridLayout
from kivymd.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout


from kivy.lang import Builder
from kivy.utils import platform  # Used to tell if platform is android

from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.button import MDIconButton
from kivymd.uix.menu import MDDropdownMenu, RightContent
from kivymd.uix.selectioncontrol import MDCheckbox

from Downloaders.manga_nelo_OOP import MangaNelo


# Kivy strings
from kivy_strings import *


class MangaCheckBox(MDCheckbox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active = False
        self.group = "group"
        self.check_btn = MDCheckbox(pos_hint={'center_x': .5, 'center_y': .5}, size=("48dp", "48dp"), size_hint=(None, None))
        # self.add_widget(self.check_btn) # This line adds an extra checkbox, I am keeping here for reflection reason


class RightContentCls(RightContent):
    def __init__(self, checkbox_site, **kwargs):
        super().__init__(**kwargs)
        self.check_btn = MangaCheckBox()
        self.checkbox_site = checkbox_site
        self.check_btn.checkbox_site = checkbox_site            

        # This if statement needs to be here, so a toast wont appear when the app is opened
        if MDApp.get_running_app().default_manga_site == checkbox_site:
            self.check_btn.active = True
            MangaSearchPage.downloader = self.checkbox_site
        
        self.check_btn.bind(active=self.checked)
        self.add_widget(self.check_btn)

    def checked(self, checkbox, value):
        if value:
            toast(f"Manga will be searched on the site: {self.checkbox_site}")
            #print(self.checkbox_site, "self.checkboxsie")
            MangaSearchPage.downloader = self.checkbox_site


class MangaSearchPage(RelativeLayout):
    downloader = None#MDApp.get_running_app().default_manga_site
    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master

        # Downloader related
        self.query = None
        self.manganelo = None
        
        # Side menu
        icons = iter(["manga_nelo_icon.png", "rawdevart_logo.png","kissmanga_logo.png", "manga_nelo_icon.png"])
        menu_items = [{"height":"70dp","right_content_cls": RightContentCls(site), "icon": next(icons), "text": site} for site in ["manganelo", "rawart", "kissmanga", "idk"]]
        self.btn = MDRaisedButton(text="Manga sites", pos_hint={"center_x": .85, "center_y": .5})
        self.btn.bind(on_press=lambda x: self.menu.open())
        self.menu = MDDropdownMenu(caller=self.btn, items=menu_items, width_mult=4)
        self.menu.bind(on_release=self.menu_callback)
        self.add_widget(self.btn)

    # Had to install dev version for callback to work
    def menu_callback(self, instance_menu, instance_menu_item):
        for i in instance_menu_item.children:
            for j in i.children:
                for k in j.children:
                    #print(k, type(k))
                    if isinstance(k, MangaCheckBox):
                        if not k.active:
                            k.active = True
                            MangaSearchPage.downloader = k.checkbox_site
                            #print(k.checkbox_site, "k.checkbox")
                        else:
                            k.active = False
   

    # This method is called within the kivy_strings.py file, on the event: on_text_validate
    def get_manga_query_data(self):
        self.query = self.ids.SearchFieldID.text
        print(MangaSearchPage.downloader, " in get manga meth")
        self.manganelo = MangaNelo(self.query)
        if self.manganelo.hasErrorOccured == False:
            MDApp.get_running_app().manga_data = self.manganelo.manga_data

            self.master.create_manga_display()
            self.master.screen_manager.current = "Manga Showcase"
        else:
            toast(self.manganelo.popup_msg)

    def get_manganelo_query_data(self):
        pass

    def abstract_get_query_data(self):
        pass


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
        #return screen
"""
if __name__ == "__main__":
    MangaDownloader().run()
