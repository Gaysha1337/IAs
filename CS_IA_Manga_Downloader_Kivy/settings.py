import json, os

from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton

from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivymd.uix.dialog import MDDialog

# Used to create custom settings
from kivy.uix.settings import Settings, SettingsWithSidebar ,SettingItem, SettingOptions, SettingSpacer, SettingPath

from utils import resource_path

"""
This Class acts as a container for the classes of the custom settings widgets I created 
"""
class AppSettings:  
    with open(resource_path("settings.json"),"r+",encoding="utf-8") as f:
        json_settings = json.dumps(json.load(f))
        
    class ScrollableSettings(SettingsWithSidebar):
        def __init__(self, *args, **kwargs):
            super().__init__(**kwargs)
            self.settings_types = [
                ('scrolloptions',AppSettings.SettingScrollOptions), ('buttons', AppSettings.SettingButtons), 
                ('better_settings_path', AppSettings.BetterSettingsPath)
            ]
            for type_ in self.settings_types:
                self.register_type(*type_)

    class BetterSettingsPath(SettingPath):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.show_hidden = True
        
        def _validate(self, instance):
            self._dismiss()
            value = self.textinput.selection
            if not value:
                return
            self.value = resource_path(os.path.realpath(value[0]))

    class SettingScrollOptions(SettingOptions):
        def _create_popup(self, instance):
            content, scrollview = GridLayout(cols=1, spacing='5dp'), ScrollView(do_scroll_x=False)
            scrollcontent = GridLayout(cols=1,  spacing='5dp', size_hint=(None, None))
            scrollcontent.bind(minimum_height=scrollcontent.setter('height'))
            self.popup = popup = Popup(content=content, title=self.title, size_hint=(0.5, 0.9),  auto_dismiss=False)
            
            popup.open() # popup is opened to get the metrics
            content.add_widget(SettingSpacer()) # Add some space on top
            
            for option in self.options:
                state = 'down' if option == self.value else 'normal'
                scrollcontent.add_widget(ToggleButton(text=option, state=state, group=str(self.uid), size=(popup.width, dp(55)), size_hint=(None, None), on_release=self._set_option))#btn)

            scrollview.add_widget(scrollcontent)
            cancel_btn = Button(text='Cancel', size=(popup.width, dp(50)), size_hint=(0.9, None), on_release=popup.dismiss)

            for widget in [scrollview, SettingSpacer(), cancel_btn]:
                content.add_widget(widget)

    class SettingButtons(SettingItem):
        def __init__(self, **kwargs):
            # For Python3 compatibility we need to drop the buttons keyword when calling super.
            kw = kwargs.copy()
            kw.pop('buttons', None)
            super(SettingItem, self).__init__(**kw)
            
            for aButton in kwargs["buttons"]:
                oButton=Button(text=aButton['title'], font_size= '15sp', on_release=self.on_button_press)
                oButton.ID=aButton['id']
                self.add_widget(oButton)
        
        def set_value(self, section, key, value):
            # set_value normally reads the configparser values and runs on an error (to do nothing here)
            return
        
        def on_button_press(self,instance):
            self.panel.settings.dispatch('on_config_change',self.panel.config, self.section, self.key, instance.ID)
