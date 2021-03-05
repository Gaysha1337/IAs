# -*- coding: utf-8 -*-
import os, sys, plyer
from kivy.uix.settings import Settings

from kivy.config import Config
_USERAGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
Config.set("network","useragent",_USERAGENT)
Config.set('kivy', 'exit_on_escape', '0')
#Config.set('kivy', 'keyboard_mode', 'systemanddock')
#Config.set('kivy', 'keyboard_mode', 'dock')

# Kivy
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.properties import StringProperty, DictProperty, BooleanProperty, ObjectProperty, ListProperty
from kivy.resources import resource_add_path
from kivy.lang import Builder
from settings import AppSettings

# Keyboard 
from kivy.core.window import Window, Keyboard

# Widgets
from kivymd.toast  import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField

# Screens and Screen-related
from kivy.uix.screenmanager import Screen, ScreenManager
from MangaScreen import MangaScreen
from Homepage import MangaInputPage, LandingPage, MangaReadingPage, DownloadedMangaDisplay
from MangaShowcase import MangaCoverContainer
from MangaReader import MangaReaderChapterSelection, MangaReaderCarouselContainer # This will be a carousel for swiping pages

# Utils
from utils import create_language_dirs, create_root_dir, move_manga_root, resource_path
from utils import show_confirmation_dialog, ConfirmationDialog
from utils import create_screen, switch_to_screen
from kivy.utils import platform


# Setting a default font
from kivy.core.text import LabelBase, DEFAULT_FONT
# android can only use droid, roboto, and dejavu fonts
LabelBase.register(DEFAULT_FONT, resource_path('DATA/NotoSansCJKjp-Regular.otf'))

# The input bar needs to be written in KV else the hint text wont showup
Builder.load_string(
'''

<MangaInputPage>
    MDTextField:
        id: SearchFieldID
        mode: "rectangle"
        max_text_length: 30
        hint_text: "Type in a manga"
        size_hint:(0.5,0.1)
        focus: True
        pos_hint:{'center_x': 0.5, 'center_y': 0.5}
        on_text_validate: root.get_manga_query_data()
'''
)
class MangaDownloader(MDApp):
    # This property will contain any data about any found manga from the user input (download links, title, cover image link, etc...)
    manga_data = DictProperty(None)
    # This property will be a reference to the selected manga site from which the app will download from
    downloader = StringProperty(None)
    # This property will check to see if a manga is being downloaded; used to show a popup if the download path is changed
    currently_downloading = BooleanProperty(False)
    # The Manga Root is the folder where all manga will be downloaded to; the sub directories corespond to the manga language
    manga_root_dir, english_manga_dir, japanese_manga_dir = StringProperty(None), StringProperty(None), StringProperty(None)
    # A reference to the current screen object (not the name)
    current_screen = ObjectProperty(None)

    download_threads = DictProperty({})
 
    def __init__(self):
        super().__init__()
        # Android related
        writable_dir = resource_path(self.user_data_dir)

        # Import android permissions:
        if platform == "android":
            from android.permissions import request_permissions, Permission
            from android.storage import primary_external_storage_path

            # https://www.youtube.com/watch?v=okpiDnSR4z8
            def permission_callback(permission, results):
                if all([result for result in results]):
                    print("Got all permissions, writable dir = ", primary_external_storage_path())
                    writable_dir = primary_external_storage_path() 
                else:
                    print("Did not get all permissions")
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE], permission_callback)

        
            print("Writable dir var = ", writable_dir, " writable == external storage?: ", writable_dir == primary_external_storage_path())
        # C:\Users\dimit\AppData\Roaming\mangadownloader\Manga 
        self.manga_root_dir = resource_path(os.path.join(writable_dir, "Manga"))

        self.default_settings_vals = {
            'theme_mode':'Dark',
            'color_scheme':'Pink',
            'default_downloader': "rawdevart",
            'download_path': resource_path(self.manga_root_dir),
            'manga_reading_direction': 'Swipe Horizontally', # Defaults to reading horizontally (swiping)
            'manga_swiping_direction':"Right to Left (English style)" # Defaults to English style: left to right
        }
        
    # Build the settings and sets their default values
    def build_config(self, config):
        config.setdefaults('Settings', self.default_settings_vals)
        
    # This defines the path and name where the .ini file is located
    # On android, the client wont be able to view the config file with a file explorer
    def get_application_config(self):
        return str(os.path.join(self.user_data_dir, 'mangadownloader.ini'))
     
    def build_settings(self, settings):
        settings.add_json_panel('Manga Downloader Settings', self.config, data=AppSettings.json_settings)
    # Method that builds all the GUI elements    
    def build(self):
        Window.bind(on_request_close=self.on_request_close) # Method called before app exit
        self.title = "Manga Downloader"
        self.icon = resource_path("Icons/MangaDownloaderIcon.ico")
        self.dialog = None # Used to get user confirmation

        # Settings
        self.settings_cls = AppSettings.ScrollableSettings # Section is called 'Settings'
        self.use_kivy_settings = False

        # Customizable Settings 
        self.theme_cls.theme_style = self.config.get("Settings", "theme_mode") # Dark or Light
        self.theme_cls.primary_palette = self.config.get("Settings", "color_scheme")
        self.downloader = self.config.get("Settings", "default_downloader") # The default manga downloading site
        self.manga_reading_direction = self.config.get("Settings", "manga_reading_direction")
        self.manga_swiping_direction = self.config.get("Settings", "manga_swiping_direction")

        # Get a keyboard for shortcuts and text input
        Window.bind(on_key_down=self._on_keyboard_down)
    
        # Screen related
        self.screen_manager = ScreenManager()

        self.reading_screens = ["Reading Page", "Manga Reader Chapter Selection", "Manga Reader Carousel"]
        self.downloading_screens = ["Manga Input Page", "Manga Showcase", "Downloaded Manga Showcase"]

        self.create_landing_page()
    
        return self.screen_manager

    def on_request_close(self, *args):
        show_confirmation_dialog(
            title= "Are you sure you want to exit the app?",
            text= "Warning: The Download for the manga may stop when you attempt to switch apps or shutdown your android device",
            proceed_callback = self.stop
        )
        return True

    def on_start(self, **kwargs):
        self.current_screen = self.screen_manager.get_screen(self.screen_manager.current)

        # Android related
        writable_dir = resource_path(self.user_data_dir)

        # Import android permissions:
        if platform == "android":
            from android.permissions import request_permissions, Permission
            from android.storage import primary_external_storage_path

            # https://www.youtube.com/watch?v=okpiDnSR4z8
            def permission_callback(permission, results):
                if all([result for result in results]):
                    print("Got all permissions, writable dir = ", primary_external_storage_path())
                    writable_dir = primary_external_storage_path() 
                else:
                    print("Did not get all permissions")
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE], permission_callback)

        
            print("Writable dir var = ", writable_dir, " writable == external storage?: ", writable_dir == primary_external_storage_path())
        # C:\Users\dimit\AppData\Roaming\mangadownloader\Manga 
        self.manga_root_dir = resource_path(os.path.join(writable_dir, "Manga"))

        print(f"[LOG]: {self.manga_root_dir}")

        self.default_settings_vals = {
            'theme_mode':'Dark',
            'color_scheme':'Pink',
            'default_downloader': "rawdevart",
            'download_path': resource_path(self.manga_root_dir),
            'manga_reading_direction': 'Swipe Horizontally', # Defaults to reading horizontally (swiping)
            'manga_swiping_direction':"Right to Left (English style)" # Defaults to English style: left to right
        }

        # The path where all manga will be downloaded to (default is manga root)
        # If it is changed while a manga is being downloaded an error will pop up
        self.download_path = resource_path(self.config.get("Settings", "download_path"))
        
        # Initial Directory creation 
        # If the user has changed the default download path (AKA: the manga root path) then set the manga root to the newly set path
        self.manga_root_dir = self.download_path if self.manga_root_dir != self.download_path else self.manga_root_dir
        self.english_manga_dir = resource_path(os.path.join(self.manga_root_dir, "English Manga"))
        self.japanese_manga_dir = resource_path(os.path.join(self.manga_root_dir, "Raw Japanese Manga"))

        if not os.path.exists(self.manga_root_dir):
            create_root_dir(self.manga_root_dir)
            create_language_dirs([self.english_manga_dir,self.japanese_manga_dir])
            

    # Android Methods
    def on_pause(self):
      # Here you can save data if needed
      return True

    def on_resume(self):
        # Here you can check if any data needs replacing (usually nothing)
        pass

    # Keyboard Methods
    def _on_keyboard_down(self, keyboard, key, scancode, text, modifiers, *args):
        #print("self:", self, "keyboard: ", keyboard,"key: ",key ,"scancode: ",scancode, "text: ",text, "modifiers: ",modifiers, "args*: ",*args)
        #print('The key', keycode, 'have been pressed', ' - text is %r' % text, ' - modifiers are %r' % modifiers," - keyboard: - %r" % keyboard, sep="\n")
        if key in ["escape", 27]:#if keycode[1] in ["escape", 27]:
            settings_open = self.close_settings()
            if isinstance(self._app_settings, Settings): 
                self.close_settings()
                self.destroy_settings()
                
            if self.current_screen.name == "Landing Page":
                if not isinstance(self.dialog, ConfirmationDialog) and not settings_open:#not isinstance(self._app_settings, Settings): 
                    self.on_request_close()
                    self.dialog = None

                #elif: 
            else: 
                switch_to_screen(self.current_screen.prev_screen)
            
        # Keyboard shortcuts to go between the images of a chapter
        if self.current_screen.name == "Manga Reader Carousel" and platform != "android":
            if key in [Keyboard.string_to_keycode(keyboard, key_code) for key_code in ["right","down", "d", "s"]]: #if keycode[1] in ["right","down", "d", "s"]: 
                self.manga_reader.next_btn.trigger_action(0)

            if key in [Keyboard.string_to_keycode(keyboard, key_code) for key_code in ["left","up", "a", "w"]]:#if keycode[1] in ["left","up", "a", "w"]:
                self.manga_reader.prev_btn.trigger_action(0)
                
        # Return True to accept the key. Otherwise, it will be used by the system.
        return True


    """ Landing Page Screen """

    def create_landing_page(self):
        self.landing_page = LandingPage(self)
        create_screen(name="Landing Page", prev_screen="Landing Page", content=self.landing_page)     

    """ Downloading Related Screens """

    # Creates the page where the user can input a manga to be downloaded
    def create_manga_search_page(self):
        self.manga_search_page = MangaInputPage(self)
        create_screen(name="Manga Input Page", prev_screen="Landing Page", content=self.manga_search_page)
    
    # Creates the manga display grid when the user has input a name
    def create_manga_display(self):
        self.manga_display = MangaCoverContainer(self)
        create_screen(name="Manga Showcase", prev_screen="Manga Input Page", content=self.manga_display)
        
        
    """ Reading Related Screens """

    # Creates the page where the user can choose to read manga in English or Japanese
    def create_manga_reading_page(self):
        self.manga_reader_page = MangaReadingPage(self)
        create_screen(name="Reading Page", prev_screen="Landing Page", content=self.manga_reader_page)

    # Creates the manga display for all downloaded manga found in a specific language
    def create_manga_read_display(self, language):
        self.download_manga_display = DownloadedMangaDisplay(self, language)
        create_screen(name="Downloaded Manga Showcase", prev_screen="Reading Page",content=self.download_manga_display)

    # Creates a display with buttons of the downloaded chapters 
    def create_manga_reader_chapter_selection(self, title, manga_path):
        self.chapter_selector = MangaReaderChapterSelection(self, title, manga_path)
        create_screen(name="Manga Reader Chapter Selection", prev_screen="Downloaded Manga Showcase", content=self.chapter_selector)

    # Creates the swiping carousel for reading a downloaded manga
    def create_manga_reader(self,manga_title,chapter_name,chapter_path):
        self.manga_reader = MangaReaderCarouselContainer(self, manga_title,chapter_name, chapter_path)
        create_screen(name="Manga Reader Carousel", prev_screen="Manga Reader Chapter Selection", content=self.manga_reader)

    # This method can handle any changes made to the settings, it also changes them when they are changed
    def on_config_change(self, config, section, key, value):
        from kivy.uix.settings import Settings
        #print("are settings open? ", self._app_settings, isinstance(self._app_settings, Settings))
        """
        This func exists because if the client changes the download path while downloading a manga
        then not all the chapters will be downloaded to the new path
        """ 
        def change_download_path(value=value):
            root_src, new_root_dst = resource_path(self.download_path), resource_path(value)
            try:
                # Recursive function to move the english and Japanese manga containing folders to the new destination
                move_manga_root(root_src, new_root_dst)
                self.manga_root_dir = self.download_path = resource_path(self.config.get("Settings", "download_path"))
                toast(f"Manga Download Path has been changed to {self.manga_root_dir}")
            except PermissionError: 
                toast("Permission Error occurred; You maybe don't have access")
            except:
                if root_src != new_root_dst: 
                    toast("Unknown Error: If you have moved any folders/files yourself, they will appear in the new path")

        # Warning incase client tries to change download path while downloading a manga
        if key == "download_path" and os.path.isdir(resource_path(os.path.join(value))):
            if self.currently_downloading:
                toast(
                    "Warning: The download path has been changed while a manga is being downloaded." +
                    "\nAll new chapters will be downloaded to the new path"
                )
            change_download_path()

        # A callback function for a confirmation dialog to confirm reseting all setting to their default values
        def reset_settings_config(inst):
            if isinstance(self.dialog, MDDialog):
                self.dialog.dismiss(force=True)
                self.dialog = None

            config.setall("Settings",self.default_settings_vals)
            config.write()
            change_download_path(self.default_settings_vals.get("download_path"))

            # Refreshes the settings menu to show that the default settings have been applied
            self.close_settings()
            self.destroy_settings()
            self.open_settings()

        # This section will reset all settings to their default values
        if key == "configchangebuttons":
            show_confirmation_dialog(
                title= "Reset to Factory Settings Confirmation: ",
                text= "Warning: This will remove all current settings!\nAny Downloaded Manga will be moved to the default download folder!",
                proceed_callback = reset_settings_config
            )
            
        self.theme_cls.theme_style = self.config.get("Settings", "theme_mode")
        self.theme_cls.primary_palette = self.config.get("Settings", "color_scheme")
        self.downloader = self.config.get("Settings", "default_downloader")
        self.manga_swiping_direction = self.config.get("Settings", "manga_swiping_direction")
        self.manga_reading_direction = self.config.get("Settings", "manga_reading_direction")

    
if __name__ == "__main__":
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    
    # https://stackoverflow.com/questions/64142867/kivymd-with-pyinstaller-hooks-images-not-showing-in-the-standalone-exe
    if getattr(sys, 'frozen', False):
        # this is a Pyinstaller bundle
        resource_add_path(sys._MEIPASS)
        resource_add_path(os.path.join(sys._MEIPASS, 'DATA'))
    MangaDownloader().run()


"""
Bibliograpgy:
- Fix for EXE app crashing when attempting to change download path
 https://stackoverflow.com/questions/57399081/pyinstaller-having-difficulty-building-filechooserlistview-via-kivy

- Fix for EXE crash when Japanese input detected (I didnt add all of the files from pykakasi/data, but rather the whole folder)
  https://qiita.com/kanedaq/items/0533336915a375dd72c1
"""
