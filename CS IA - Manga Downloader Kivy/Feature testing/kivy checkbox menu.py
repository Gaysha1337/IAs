from kivymd.app import MDApp
from kivymd.uix.label import MDIcon
from kivymd.uix.menu import MDDropdownMenu, RightContent
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivymd.uix.button import MDRaisedButton
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.toast import toast


class MangaSiteMenuSelector:
    class MangaCheckBox(MDCheckbox):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.active = False
            self.group = "group"
            self.check_btn = MDCheckbox(pos_hint={'center_x': .5, 'center_y': .5}, size=("48dp","48dp"), size_hint =(None, None))
            #self.add_widget(self.check_btn) # This line adds an extra checkbox, I am keeping here for reflection reason

    class RightContentCls(RightContent):
        def __init__(self, checkbox_site, **kwargs):
            super().__init__(**kwargs)
            self.checkbox_site = checkbox_site
            self.check_btn = MangaCheckBox()
            self.check_btn.bind(active = self.checked)
            self.add_widget(self.check_btn)

        def checked(self,checkbox, value):
            if value:
                toast(f"Manga will be searched on the site: {checkbox.parent.checkbox_site}")
            
    class TESTSCREEN(RelativeLayout):
        def __init__(self, master, **kwargs):
            super().__init__(**kwargs)
            self.master = master

            icons = iter(["../manga_nelo_icon.png", "../rawdevart_logo.png", "../kissmanga_logo.png", "../manga_nelo_icon.png"])
            menu_items = [{"right_content_cls":RightContentCls(site),"icon":next(icons),"text": site} for site in ["manganelo", "rawart", "kissmanga", "idk"]]
            self.btn = MDRaisedButton(text="press me", pos_hint={"center_x": .5, "center_y": .5})
            self.btn.bind(on_press=lambda x:self.menu.open())
            
            self.menu = MDDropdownMenu(caller=self.btn,items=menu_items,width_mult=4)
            self.menu.bind(on_release=self.menu_callback)
            self.add_widget(self.btn)
            
        # Had to install dev version for callback to work
        def menu_callback(self, instance_menu, instance_menu_item):
            for i in instance_menu_item.children:
                for j in i.children:
                    for k in j.children:
                        print(k, type(k))
                        if isinstance(k, MangaCheckBox):
                            if not k.active: 
                                k.active = True
                            else:
                                k.active = False

class MangaCheckBox(MDCheckbox):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.active = False
        self.group = "group"
        self.check_btn = MDCheckbox(pos_hint={'center_x': .5, 'center_y': .5}, size=("48dp","48dp"), size_hint =(None, None))
        #self.add_widget(self.check_btn) # This line adds an extra checkbox, I am keeping here for reflection reason

class RightContentCls(RightContent):
    def __init__(self, checkbox_site, **kwargs):
        super().__init__(**kwargs)
        self.checkbox_site = checkbox_site
        self.check_btn = MangaCheckBox()
        self.check_btn.bind(active = self.checked)
        self.add_widget(self.check_btn)

    def checked(self,checkbox, value):
        toast(f"Manga will be searched on the site: {checkbox.parent.checkbox_site}")
        
class TESTSCREEN(BoxLayout):
    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master

        icons = iter(["../manga_nelo_icon.png", "../rawdevart_logo.png", "../kissmanga_logo.png", "../manga_nelo_icon.png"])
        menu_items = [{"right_content_cls":RightContentCls(site),"icon":next(icons),"text": site} for site in ["manganelo", "rawart", "kissmanga", "idk"]]
        self.btn = MDRaisedButton(text="press me", pos_hint={"center_x": .5, "center_y": .5})
        self.btn.bind(on_press=lambda x:self.menu.open())
        
        self.menu = MDDropdownMenu(caller=self.btn,items=menu_items,width_mult=4)
        self.menu.bind(on_release=self.menu_callback)
        self.add_widget(self.btn)
        
    # Had to install dev version for callback to work
    def menu_callback(self, instance_menu, instance_menu_item):
        #print(instance_menu, instance_menu_item.text)
        for i in instance_menu_item.children:
            for j in i.children:
                for k in j.children:
                    print(k, type(k))
                    if isinstance(k, MangaCheckBox):
                        if not k.active: 
                            k.active = True
                            toast(f"Manga will be searched on the site: {instance_menu_item.text}")
                        else:
                            k.active = False
                    

class Test(MDApp):
    """
    def build(self):
        self.t = TESTSCREEN(self)
        screen = Screen(name="t")
        screen.add_widget(self.t)
        return screen
    """

    def build(self):
        self.mangamenu = MangaSiteMenuSelector()
        self.men = self.mangamenu.TESTSCREEN(self)
        screen = Screen(name="t")
        screen.add_widget(self.men)
        return screen
    
Test().run()