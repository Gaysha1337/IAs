from kivy.app import App
from kivy.uix.behaviors import CoverBehavior
from kivy.uix.image import Image


class CoverImage(CoverBehavior, Image):

    def __init__(self, **kwargs):
        super(CoverImage, self).__init__(**kwargs)
        #texture = self._coreimage.texture
        #self.reference_size = texture.size
        #self.texture = texture
        self.source = "../Icons/Manga Downloader Icon.png"
        self.keep_ratio = True
        self.allow_stretch = True


class MainApp(App):

    def build(self):
        #return CoverImage(source="../Icons/Manga Downloader Icon.png")
        return Image(source="../Icons/Manga Downloader Icon.png")

MainApp().run()