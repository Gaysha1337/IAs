from kivy.lang import Builder

from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu, RightContent
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.toast import toast

KV = '''
<RightContentCls>
    
    MDCheckbox:
        size_hint: None, None
        size: "48dp", "48dp"
        pos_hint: {'center_x': .5, 'center_y': .5}
        on_active: print(self.state)
    
Screen:
    MDRaisedButton:
        id: button
        text: "PRESS ME"
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: app.menu.open()    
'''

#Builder.load_string(KV)

class RightContentCls(RightContent):
    pass

class TESTSCREEN(BoxLayout):
    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master

        icons = iter(["../manga_nelo_icon.png", "../rawdevart_logo.png"])
        menu_items = [{"right_content_cls":RightContentCls(),"icon":next(icons),"text": i} for i in ["manganelo", "rawart"]]
        self.btn = MDRaisedButton(text="press me", pos_hint={"center_x": .5, "center_y": .5})
        self.btn.bind(on_press=lambda x:self.menu.open())
        
        self.menu = MDDropdownMenu(caller=self.btn,items=menu_items,width_mult=4)
        self.menu.bind(on_release=self.menu_callback)
        self.add_widget(self.btn)
        
    # Had to install dev version for callback to work
    def menu_callback(self, instance_menu, instance_menu_item):
        print(instance_menu, instance_menu_item.text)
        toast(f"Manga will be searched on the site: {instance_menu_item.text}")

class Test(MDApp):
    
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        self.screen = Builder.load_string(KV)
        icons = iter(["../manga_nelo_icon.png", "../rawdevart_logo.png"])
        menu_items = [{"right_content_cls": RightContentCls(),"icon":next(icons),"text": i} for i in ["manganelo", "rawart"]]
        
        self.menu = MDDropdownMenu(
            caller=self.screen.ids.button, items=menu_items, width_mult=4
        )
        self.menu.bind(on_release=self.menu_callback)

    def menu_callback(self, instance_menu, instance_menu_item):
        #instance_menu.dismiss()
        print(instance_menu_item)

    def build(self):
        return self.screen
    """
    def build(self):
        self.t = TESTSCREEN(self)
        screen = Screen(name="t")
        screen.add_widget(self.t)
        return screen
    """


Test().run()