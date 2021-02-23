import os, sys
from functools import partial
from pathlib import Path
from kivy.clock import Clock
from kivy.uix.button import Button
from kivymd.app import MDApp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.stacklayout import MDStackLayout

from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton, MDRectangleFlatIconButton
from kivymd.toast import toast
from kivymd.uix.menu import MDDropdownMenu, RightContent
from kivymd.uix.selectioncontrol import MDCheckbox

# Downloader classes
from Downloaders.MangaNelo import MangaNelo
from Downloaders.Rawdevart import RawDevArt
from Downloaders.Kissmanga import KissManga
from Downloaders.Senmanga import SenManga

# Utils
from utils import convert_from_japanese_text, resource_path, kill_screen, show_confirmation_dialog

class LandingPage(MDRelativeLayout):
    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        
        self.btn_texts = ["Download Manga", "Read Manga          "]

        self.download_btn = MDRectangleFlatIconButton(text=self.btn_texts[0], icon="download-box",  pos_hint={"center_x": .5, "center_y": .4}, user_font_size="64sp", on_release=self.go_to_screen)
        self.read_btn = MDRectangleFlatIconButton(text=self.btn_texts[1], icon="book-open-page-variant", pos_hint={"center_x": .5, "center_y": .6}, user_font_size="64sp", on_release=self.go_to_screen)
        self.add_widget(self.read_btn)
        self.add_widget(self.download_btn)

    def go_to_screen(self, inst):
        if inst.text == "Download Manga":
            kill_screen("Manga Input Page", lambda *args: self.master.create_manga_search_page())
            self.master.manga_search_page.ids["SearchFieldID"].focus = True if inst.text == "Download Manga" else False
            
        else: kill_screen("Reading Page", lambda*args: self.master.create_manga_reading_page())

class MangaCheckBox(MDCheckbox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.__class__.instances.append(self)
        self.master = MDApp.get_running_app()
        self.active = False
        self.group = "group"
        self.check_btn = MDCheckbox(pos_hint={'center_x': .5, 'center_y': .5}, size=("48dp", "48dp"), size_hint=(None, None))
        self.checkbox_site = None
        self.allow_no_selection = False

        

class RightContentCls(RightContent):
    def __init__(self, checkbox_site, **kwargs):
        super().__init__(**kwargs)
        self.master = MDApp.get_running_app()
        self.check_btn = MangaCheckBox()
        self.check_btn.allow_no_selection = False
        self.checkbox_site = self.check_btn.checkbox_site = checkbox_site
    
        # This if statement needs to be here, so a toast wont appear when the app is opened
        # It is ensures that the default site is pre-checked
        if self.master.downloader == checkbox_site:
            self.check_btn.active = True
            self.master.downloader = self.checkbox_site
        self.check_btn.bind(active=self.checked)
        self.add_widget(self.check_btn)

    # This function gets run whenever, a checkbox is ticked or unticked
    def checked(self, checkbox, value):
        if value:
            self.master.downloader = self.checkbox_site
            toast(text=f"Manga will be searched on the site: {self.master.downloader}")

class MangaInputPage(MDRelativeLayout):
    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.input_bar = self.ids.SearchFieldID
        self.downloader_sites = ["manganelo", "kissmanga", "rawdevart", "senmanga"]

        # Side menu
        icons = iter(
            [resource_path("./DATA/manga_nelo_icon.png"),resource_path("./DATA/kissmanga_logo.png"), 
            resource_path("./DATA/rawdevart_logo.png"), resource_path("./DATA/sen_manga_logo.png")]
        )
        menu_items = [{"height": "70dp", "right_content_cls": RightContentCls(site), "icon": next(icons), "text": site} for site in self.downloader_sites]
        self.btn = MDRaisedButton(text="Manga sites", pos_hint={"center_x": .85, "center_y": .5}, on_release=lambda x: self.menu.open())
        self.menu = MDDropdownMenu(caller=self.btn, items=menu_items, width_mult=4)
        self.menu.bind(on_release=self.menu_callback)
        self.add_widget(self.btn)

    # Had to install dev version for callback to work
    def menu_callback(self, instance_menu, instance_menu_item):
        for child in instance_menu_item.walk_reverse(loopback=True):
            if isinstance(child, MangaCheckBox) and child.checkbox_site == instance_menu_item.text: 
                if not child.active:
                    child.active = True
                    self.master.downloader = child.checkbox_site
        
    # This method is called from the KV code, on the event: on_text_validate
    def get_manga_query_data(self):
        jp_to_en_text = convert_from_japanese_text(self.input_bar.text.strip())
        downloader_sites = {"manganelo": MangaNelo, "rawdevart": RawDevArt,"kissmanga": KissManga,"senmanga": SenManga}

        # Instantiates appropriate downloader site with the converted text
        downloader_site = downloader_sites.get(self.master.downloader)(jp_to_en_text)
        
        if downloader_site is not None and downloader_site.hasErrorOccured == False:
            self.master.manga_data = downloader_site.manga_data
            kill_screen("Manga Showcase", lambda *args: self.master.create_manga_display())
        else: 
            toast(downloader_site.popup_msg)
        self.input_bar.text = ""

class MangaReadingPage(MDRelativeLayout):
    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.btn_text = ["Japanese (raw) Manga", "       English Manga          "]

        self.japanese_manga_btn = MDRectangleFlatButton(text=self.btn_text[0],pos_hint={"center_x":.5, "center_y":.6}, on_release=self.go_to_read_downloaded_manga)
        self.english_manga_btn = MDRectangleFlatButton(text=self.btn_text[1],pos_hint={"center_x":.5, "center_y":.4}, on_release=self.go_to_read_downloaded_manga)
        
        for btn in [self.japanese_manga_btn, self.english_manga_btn]:
            self.add_widget(btn)

    def go_to_read_downloaded_manga(self, inst):
        language = "Japanese" if inst.text == self.btn_text[0] else "English"
        kill_screen("Downloaded Manga Showcase", lambda *args: self.master.create_manga_read_display(language=language))
            
class MangaCoverTile(SmartTileWithLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.master = MDApp.get_running_app()
        self.size_hint_y = None
        self.height = "240dp"
        self.font_style = "H6"

# Reading Manga Display
class DownloadedMangaDisplay(ScrollView):
    def __init__(self, master, language, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.effect_cls = "ScrollEffect"
        self.bar_width = "10dp"
        self.pos_hint = {"top":.9}
        self.do_scroll_y = True

        self.language_folder = self.master.japanese_manga_dir if language == "Japanese" else self.master.english_manga_dir

        self.manga_folders = [resource_path(str(dir)) for dir in Path(self.language_folder).glob("*/")]
        self.manga_cover_imgs = [resource_path(str(img_path)) for img_path in Path(self.language_folder).glob("*/*.jpg")]
        self.manga_tile_data = list(zip(self.manga_folders, self.manga_cover_imgs))

        # This grid acts as a container for the number of manga found and the table with the clickable tiles
        self.outer_gird = MDGridLayout(rows=2, adaptive_height=True, padding=("0dp", "20dp", "0dp", "20dp"), pos_hint={"top":.8})
        self.outer_gird.add_widget(MDLabel(text=f"{len(self.manga_folders)} manga were found", halign="center", pos_hint = {"center_x":.5,"y":.9}))

        self.grid = MDStackLayout(adaptive_height=True, orientation="lr-tb", spacing=("20dp","20dp"), padding=("5dp", "30dp", "5dp", "30dp"))
        
        for i in self.manga_tile_data:
            title, manga_path = i[0].split("\\")[-1], i[0]
            reload_func = lambda title=title, manga_path=manga_path:self.master.create_manga_reader_chapter_selection(title, manga_path)
            self.btn = MangaCoverTile(source=i[1], text=title, size_hint=(.25,.25), on_release=partial(kill_screen,"Manga Reader Chapter Selection", reload_func))
            self.grid.add_widget(self.btn)
        
        self.outer_gird.add_widget(self.grid)
        self.add_widget(self.outer_gird)