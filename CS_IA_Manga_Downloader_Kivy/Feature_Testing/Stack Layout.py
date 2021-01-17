from kivy.lang import Builder
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.button import MDIconButton, MDRectangleFlatIconButton, MDFlatButton, MDRectangleFlatButton
from kivy.uix.scrollview import ScrollView

from kivymd.app import MDApp

KV = '''
MyStackLayout:
'''

class MyStackLayout(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding=("20dp", "20dp", "20dp", "20dp")
        self.pos_hint = {"center_x":.5, "center_y":.5}
        self.stack_layout = MDStackLayout(adaptive_height = True, orientation="lr-tb", spacing=("20dp","20dp"), pos_hint = {"center_x":.5, "center_y":.5})

        for i in range(100):
            self.stack_layout.add_widget(MDRectangleFlatButton(text=str(i)))

        self.add_widget(self.stack_layout)

class Test(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        return Builder.load_string(KV)


Test().run()