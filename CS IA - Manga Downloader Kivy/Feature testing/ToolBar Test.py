from kivy.lang import Builder

from kivymd.app import MDApp

KV = '''
BoxLayout:
    #orientation: "vertical"

    MDToolbar:
        title: "MDToolbar"
        left_action_items: [["menu", lambda x: print(self)]]

    MDLabel:
        text: "Content"
        halign: "center"
'''


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)


Test().run()