from kivy.lang import Builder

from kivymd.app import MDApp
from kivy.uix.popup import Popup

KV = '''
#:import Snackbar kivymd.uix.snackbar.Snackbar


Screen:

    MDRaisedButton:
        text: "Create simple snackbar"
        on_release: Snackbar(text="This is a snackbar!").show()
        pos_hint: {"center_x": .5, "center_y": .5}

    
'''


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)


Test().run()