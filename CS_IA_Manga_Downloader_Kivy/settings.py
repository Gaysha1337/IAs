import json, plyer
from kivymd.app import MDApp

from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton

from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivymd.uix.dialog import MDDialog

# Used to create custom settings
from kivy.uix.settings import Settings
from kivy.uix.settings import SettingsWithSpinner, SettingsWithSidebar, InterfaceWithSidebar
from kivy.uix.settings import SettingItem
from kivy.uix.settings import SettingOptions
from kivy.uix.settings import SettingSpacer

class AppSettings:

    """
    {'type': 'bool',
    'title': 'Manga Reading Direction',
    'desc': 'Turn on to scroll vertically while reading. Turn off to swipe horizontally for reading',
    'section': 'Settings',
    'key': 'manga_reading_direction'
    },
    """

    """
    {'type': 'bool',
    'title': 'Manga Reading Swipe Direction for page turning',
    'desc': 'Turn on to use the Japanese way of reading manga: Left to Right, while swiping; default is: Right to Left.',
    'section': 'Settings',
    'key': 'manga_swiping_direction'
    },
    """
    
    json_settings = json.dumps([
        {'type': 'title', 'title': 'Color Scheme and Theme Settings'},

        {'type': 'scrolloptions',
        'title': 'Theme',
        'desc': 'Dark theme or Light theme',
        'section': 'Settings',
        'key': 'theme_mode',
        'options': ['Dark', 'Light']
        },

        {'type': 'scrolloptions',
        'title': 'Color scheme',
        'desc': 'This settings affects the color of: Text, borders... but not the theme(light or dark)',
        'section': 'Settings',
        'key': 'color_scheme',
        'options': ['Red', 'Pink', 'Purple', 'DeepPurple', 'Indigo', 'Blue', 'LightBlue', 'Cyan', 'Teal', 'Green', 'LightGreen', 'Lime', 'Yellow', 'Amber', 'Orange', 'DeepOrange', 'Brown', 'Gray', 'BlueGray']
        },

        {'type': 'title','title': 'Download Settings'},

        {'type': 'scrolloptions',
        'title': 'Default Manga Site',
        'desc': 'The default site that will be used to download manga',
        'section': 'Settings',
        'key': 'default_downloader',
        'options': ["manganelo", "kissmanga", "rawdevart", "senmanga"]
        },

        {'type': 'path',
        'title': 'Download Folder Path',
        'desc': "All downloaded manga will be found in this folder. It will have 2 sub folders for English and Japanese manga",
        'section': 'Settings',
        'key': 'download_path'
        },

        {'type': 'title','title': 'Manga Reader Settings'},

        {'type': 'scrolloptions',
        'title': 'Manga Reading Direction',
        'desc': 'Turn on to scroll vertically while reading. Turn off to swipe horizontally for reading',
        'section': 'Settings',
        'key': 'manga_reading_direction',
        'options' : ["Scroll vertically", "Swipe Horizontally"],
        },

        {'type': 'scrolloptions',
        'title': 'Manga Reading Swipe Direction for page turning',
        'desc': 'The Japanese way of reading manga is: Left to Right. The English way is: Right to Left.',
        'section': 'Settings',
        'key': 'manga_swiping_direction',
        'options':["Left to Right (Japanese style)", "Right to Left (English style)"],
        },

        {'type':'title', 'title':'Misc.'},
        
        {"type": "buttons",
        "title": "Reset Settings",
        "desc": "Reset the settings to their default values",
        "section": "Settings",
        "key": "configchangebuttons",
        "buttons":[{"title":"Reset Settings","id":"reset_settings_btn"}]
        },
    ])

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
                btn = ToggleButton(text=option, state=state, group=uid, size=(popup.width, dp(55)), size_hint=(None, None))
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

    class SettingButtons(SettingItem):
        def __init__(self, **kwargs):
            self.register_event_type('on_release')
            # For Python3 compatibility we need to drop the buttons keyword when calling super.
            kw = kwargs.copy()
            kw.pop('buttons', None)
            super(SettingItem, self).__init__(**kw)
            for aButton in kwargs["buttons"]:
                oButton=Button(text=aButton['title'], font_size= '15sp')
                oButton.ID=aButton['id']
                self.add_widget(oButton)
                oButton.bind (on_release=self.On_ButtonPressed)
        def set_value(self, section, key, value):
            # set_value normally reads the configparser values and runs on an error
            # to do nothing here
            return
        def On_ButtonPressed(self,instance):
            self.panel.settings.dispatch('on_config_change',self.panel.config, self.section, self.key, instance.ID)
    class ScrollableSettings(SettingsWithSidebar):
        def __init__(self, *args, **kwargs):
            super().__init__(**kwargs)
            self.content_panel = self.interface.children[0]
            #self.content_panel.effect_cls = "ScrollEffect"
            #self.content_panel.scroll_type = ["bars", "content"]
            self.content_panel.bar_width = "10dp"
            self.register_type('scrolloptions', AppSettings.SettingScrollOptions)
            self.register_type('buttons', AppSettings.SettingButtons)

            print("settings interface csl", self.interface.children[1].children[1])
            print("interface content", self.interface.children[0].scroll_type)

if __name__ == "__main__":
    #SettingsApp().run()
    pass
