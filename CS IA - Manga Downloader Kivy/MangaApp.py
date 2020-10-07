import kivy, os
from kivy.app import App
from kivy.uix.label import Label # Text from the user 
from kivy.uix.gridlayout import GridLayout # Used for organizing widgets 
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager # Screen and ScreenManager need to be imported as a pair

from Homepage import Homepage
from Read import ReadingPage


"""
class ReadingPage(GridLayout):
    def __init__(self, master,**kwargs):
        super().__init__(**kwargs)
        self.master = master 
        self.cols = 1

        # Screen title
        self.add_widget(Label(text="Downloaded Manga: "))

        # TODO: Find and add icons for all 2 buttons

        # Button to click for returning to the homepage
        self.home_button = Button(text="Home")
        self.home_button.bind(on_press=self.home_button_handler())
        self.add_widget(self.home_button)
        
        # Settings Button
        self.settings_button = Button(text="Settings")
        self.settings_button.bind(on_press=self.settings_button_handler)
        self.add_widget(self.settings_button)

    def home_button_handler(self, instance):
        # Change to a page with 
        pass
    
    def settings_button_handler(self, instance):
        pass

class Homepage(GridLayout):
    def __init__(self, master,**kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.cols = 1

        # Screen title
        self.add_widget(Label(text="Manga Downloader"))

        # TODO: Find and add icons for all 3 buttons
        # Button to click for reading manga
        self.read_button = Button(text="Read")
        self.read_button.bind(on_press=self.read_button_handler)
        self.add_widget(self.read_button)

        # Button to click for downloading manga
        self.download_button = Button(text="Download")
        self.download_button.bind(on_press=self.download_button_handler)
        self.add_widget(self.download_button)
        
        # Settings Button
        self.settings_button = Button(text="Settings")
        self.settings_button.bind(on_press=self.settings_button_handler)
        self.add_widget(self.settings_button)

    def read_button_handler(self, instance):
        #self.master.screenmanager.current = "ReadingPage"
        print(self.master.screenmanager.screens)
    
    def download_button_handler(self, instance):
        pass
    def settings_button_handler(self, instance):
        pass
"""
class MangaApp(App):

    def build(self):

        self.screenmanager = ScreenManager()

        # Home page screen
        self.homepage = Homepage(self)
        screen = Screen(name="HomePage")
        screen.add_widget(self.homepage)
        self.screenmanager.add_widget(screen)

        # Reading page screen
        self.reading_page = ReadingPage(self)
        screen = Screen(name = "ReadingPage")
        screen.add_widget(self.reading_page)
        self.screenmanager.add_widget(screen)

        return self.screenmanager



if __name__ == "__main__":
    MangaApp().run()