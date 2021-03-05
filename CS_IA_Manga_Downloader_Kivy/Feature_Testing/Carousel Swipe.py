from kivy.uix.carousel import Carousel
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.lang import Builder

Builder.load_string('''
<Page>:
    label_id: label_id
    Label:
        id: label_id
        text: str(id(root))

#<NewCarousel>
    #on_current_slide: print(args[1].label_id.text, root.current_slide)
''')
i = 0
class NewCarousel(Carousel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)



class Page(BoxLayout):
    pass

class TestApp(App):
    def build(self):
        root = NewCarousel()
        root.bind(on_current_slide = self.ree)
        for x in range(10):
            root.add_widget(Page())
        return root

    def ree(self, inst): print("reee")

if __name__ == '__main__':
    TestApp().run()