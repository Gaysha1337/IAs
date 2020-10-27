import kivy
import json
import plyer
from kivymd.app import MDApp

from kivy.uix.settings import Settings
from kivy.uix.settings import SettingOptions
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.settings import SettingSpacer
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.uix.popup import Popup

from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.settings import SettingsWithSidebar

from kivymd.uix.button import MDIconButton

from kivy.uix.label import Label

from plyer.facades.storagepath import StoragePath

from kivy_strings import *

settings_json = json.dumps([
    {'type': 'title',
     'title': 'Settings'},

    {'type': 'bool',
     'title': 'A boolean setting',
     'desc': 'Boolean description text',
     'section': 'Settings',
     'key': 'boolexample'},

    {'type': 'numeric',
     'title': 'A numeric setting',
     'desc': 'Numeric description text',
     'section': 'Settings',
     'key': 'numericexample'},

    {'type': 'scrolloptions',
     'title': 'Theme',
     'desc': 'Dark theme or Light theme',
     'section': 'Settings',
     'key': 'theme_mode',
     'options': ['Dark', 'Light']},

    {'type': 'scrolloptions',
     'title': 'Color scheme',
     'desc': 'This settings affects the color of:Text, borders... but not the theme(light or dark)',
     'section': 'Settings',
     'key': 'color_scheme',
     'options': ['Red', 'Pink', 'Purple', 'DeepPurple', 'Indigo', 'Blue', 'LightBlue', 'Cyan', 'Teal', 'Green', 'LightGreen', 'Lime', 'Yellow', 'Amber', 'Orange', 'DeepOrange', 'Brown', 'Gray', 'BlueGray']},

    {'type': 'path',
     'title': 'Download Folder Path',
     'desc': "All downloaded manga will be found in this folder called 'manga_downloader_root' ",
     'section': 'Settings',
     'key': 'DownloadPath'},
     
    {'type': 'string',
     'title': 'A string setting',
     'desc': 'String description text',
     'section': 'Settings',
     'key': 'stringexample'}])

class AppSettings:
    
    json_settings = json.dumps([
            {'type': 'title',
            'title': 'Color Scheme and Theme Settings'},

            {'type': 'scrolloptions',
            'title': 'Theme',
            'desc': 'Dark theme or Light theme',
            'section': 'Settings',
            'key': 'theme_mode',
            'options': ['Dark', 'Light']},

            {'type': 'scrolloptions',
            'title': 'Color scheme',
            'desc': 'This settings affects the color of: Text, borders... but not the theme(light or dark)',
            'section': 'Settings',
            'key': 'color_scheme',
            'options': ['Red', 'Pink', 'Purple', 'DeepPurple', 'Indigo', 'Blue', 'LightBlue', 'Cyan', 'Teal', 'Green', 'LightGreen', 'Lime', 'Yellow', 'Amber', 'Orange', 'DeepOrange', 'Brown', 'Gray', 'BlueGray']},

            {'type': 'title',
            'title': 'Download Settings'},

            {'type': 'scrolloptions',
            'title': 'Default Manga Site',
            'desc': 'The default site that will be used to download manga',
            'section': 'Settings',
            'key': 'default_downloader',
            'options': ["manganelo", "rawdevart", "kissmanga", "senmanga"]},

            {'type': 'path',
            'title': 'Download Folder Path',
            'desc': "All downloaded manga will be found in a folder called 'Manga' ",
            'section': 'Settings',
            'key': 'download_path'},

            {'type': 'title',
            'title': 'Manga Reader Settings'},

            {'type': 'bool',
            'title': 'Manga Reading Direction',
            'desc': 'Turn on to scroll vertically while reading. Turn off to swipe horizontally for reading',
            'section': 'Settings',
            'key': 'manga_reading_direction'},

            {'type': 'bool',
            'title': 'Manga Reading Swipe Direction',
            'desc': 'Turn on to use the Japanese way of reading manga: Right to Left, while swiping; default is: Left to Right.',
            'section': 'Settings',
            'key': 'manga_swiping_direction'},])


    class SettingScrollOptions(SettingOptions):

        def _create_popup(self, instance):
            # global oORCA
            # create the popup

            content = GridLayout(cols=1, spacing='5dp')
            scrollview = ScrollView(do_scroll_x=False)
            scrollcontent = GridLayout(cols=1,  spacing='5dp', size_hint=(None, None))
            scrollcontent.bind(minimum_height=scrollcontent.setter('height'))
            self.popup = popup = Popup(content=content, title=self.title, size_hint=(0.5, 0.9),  auto_dismiss=False)
            # we need to open the popup first to get the metrics
            popup.open()
            # Add some space on top
            content.add_widget(Widget(size_hint_y=None, height=dp(2)))
            # add all the options
            uid = str(self.uid)
            for option in self.options:
                state = 'down' if option == self.value else 'normal'
                btn = ToggleButton(text=option, state=state, group=uid, size=(
                    popup.width, dp(55)), size_hint=(None, None))
                btn.bind(on_release=self._set_option)
                scrollcontent.add_widget(btn)

            # finally, add a cancel button to return on the previous panel
            scrollview.add_widget(scrollcontent)
            content.add_widget(scrollview)
            content.add_widget(SettingSpacer())
            # btn = Button(text='Cancel', size=((oORCA.iAppWidth/2)-sp(25), dp(50)),size_hint=(None, None))
            btn = Button(text='Cancel', size=(popup.width, dp(50)), size_hint=(0.9, None))
            btn.bind(on_release=popup.dismiss)
            content.add_widget(btn)

    class ScrollableSettings(Settings):
        def __init__(self, *args, **kwargs):
            super().__init__(**kwargs)
            self.register_type('scrolloptions', AppSettings.SettingScrollOptions)

class SettingsInterface(BoxLayout):
    pass

class SettingsApp(MDApp):
    Builder.load_string(settings_page_kv_str)

    def build(self):

        self.theme_cls.theme_style="Light"
        self.settings_cls=AppSettings.ScrollableSettings
        self.use_kivy_settings=False

        self.screen_manager=ScreenManager()
        
        self.interface=SettingsInterface()
        screen=Screen(name = "Settings")
        screen.add_widget(self.interface)
        self.screen_manager.add_widget(screen)

        # setting = self.config.get('Settings', 'DownloadPath')
        # print(setting)
        print(plyer.storagepath.get_downloads_dir())
        print(self.screen_manager.current)

        # return SettingsInterface()
        return self.screen_manager

    def build_config(self, config):
        user_downloads_dir=plyer.storagepath.get_downloads_dir()

        config.setdefaults('Settings', {
            'useJapaneseKeyboard': True,
            'boolexample': True,
            'numericexample': 10,
            'optionsexample': 'option2',
            'stringexample': 'some_string',
            'DownloadPath': user_downloads_dir,
            'default_downloader':'manganelo',
            'color_scheme':'Pink',
            'theme_mode':'Dark'})

    def build_settings(self, settings):
        # You can add multiple panels
        settings.add_json_panel('Manga Downloader Settings', self.config, data = settings_json)

    # This method can handle any changes made to the settings
    def on_config_change(self, config, section, key, value):
        print(config, section, key, value, "fuwhrif")

if __name__ == "__main__":
    #SettingsApp().run()
    pass
