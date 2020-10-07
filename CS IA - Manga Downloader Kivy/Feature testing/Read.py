import kivy, os
from kivy.app import App
from kivy.uix.label import Label # Text from the user 
from kivy.uix.gridlayout import GridLayout # Used for organizing widgets 
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager # Screen and ScreenManager need to be imported as a pair


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
        self.home_button.bind(on_press=self.home_button_handler)
        self.add_widget(self.home_button)
        
        # Settings Button
        self.settings_button = Button(text="Settings")
        self.settings_button.bind(on_press=self.settings_button_handler)
        self.add_widget(self.settings_button)

    def home_button_handler(self, instance):
        self.master.screenmanager.current = "HomePage"
        
    
    def settings_button_handler(self, instance):
        pass



        