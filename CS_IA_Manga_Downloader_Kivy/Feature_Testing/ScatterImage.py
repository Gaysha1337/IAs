from kivy.app import App
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.properties import StringProperty
from kivy.lang import Builder
import os
 
img_name = "../Icons/Manga Downloader Icon.png"

KV = """
#:import win kivy.core.window
<Picture@Scatter>:
    do_rotation: False
    do_translation: False
    source: None
    #on_size: self.center = win.Window.center
    scale: 5
    scale_min: 5
    scale_max: 12
    #size: image.size
    size_hint: None, None
    
    center: self.parent.center
    Image:
        id: image
        source: root.source
        keep_ratio: True
        allow_stretch: True
        
RelativeLayout:
    Picture:
        source: "../Icons/Manga Downloader Icon.png"
"""

class MyApp(App):

    def build(self):
        return Builder.load_string(KV)



class SimpleApp(App):
    def build(self):
        f = FloatLayout()
        s = Scatter(do_rotation=False, do_translation=False)
        l = Label(text="Edureka!", font_size=150, pos_hint={"y":.5,"x":.5})
        i = Image(source="../Icons/Manga Downloader Icon.png",keep_ratio=True, allow_stretch=True)
 
        f.add_widget(s)
        s.add_widget(i)
        return f
 
 
if __name__ == "__main__":
    #SimpleApp().run()
    MyApp().run()