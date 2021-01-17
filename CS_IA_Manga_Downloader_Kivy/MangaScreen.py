from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.toast.kivytoast.kivytoast import toast

from kivymd.uix.button import MDFlatButton
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.dialog import MDDialog

from kivy.utils import platform
from utils import switch_to_screen, show_confirmation_dialog, ConfirmationDialog

from functools import partial


class MangaScreen(Screen): 
    def __init__(self, prev_screen="Landing Page",**kwargs):
        super().__init__(**kwargs)
        self.master = MDApp.get_running_app()
        self.prev_screen = prev_screen
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
    def on_pre_enter(self, *args, **kwargs):
        self.toolbar = ToolBar()
        self.add_widget(self.toolbar)
        print(self.name)


    # Keyboard methods
    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        #self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        #self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print('The key', keycode, 'have been pressed', ' - text is %r' % text, ' - modifiers are %r' % modifiers, sep="\n")
        #self.current_screen = self.master.screen_manager.get_screen(self.master.screen_manager.current)
        print(self.master.current_screen.name)
        if keycode[1] in ["escape"]:
            if self.master.current_screen.name == "Landing Page":
                if not isinstance(self.master.dialog, ConfirmationDialog): self.master.dialog.dismiss()
                show_confirmation_dialog(
                    title= "Are you sure you want to exit the app?",
                    text= "Warning: The Download for the manga may stop when you attempt to switch apps or shutdown your android device",
                    proceed_callback = self.master.stop
                )
            else: switch_to_screen(self.master.current_screen.prev_screen)
            #switch_to_screen(self.master.current_screen.prev_screen)
        
        # Keyboard shortcuts to go between the images of a chapter
        if keycode[1] in ["right","down", "d", "s"] and self.name == "Manga Reader Carousel": 
            self.master.manga_reader.carousel.load_next()
        
        if keycode[1] in ["left","up", "a", "w"] and self.name == "Manga Reader Carousel": 
            self.master.manga_reader.carousel.load_previous()

            
        # Return True to accept the key. Otherwise, it will be used by the system.
        return True 
    



class ToolBar(MDToolbar):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.master = MDApp.get_running_app()
        #self.current_screen = self.master.current_screen#self.master.screen_manager.get_screen(self.master.screen_manager.current)
        self.title = self.master.title
        self.id = "Toolbar"
        self.pos_hint = {"top":1}
        self.elevation = 10
        self.left_action_items = [["home", lambda x: switch_to_screen("Landing Page")],["cog", lambda x: self.master.open_settings()]]
        self.right_action_items = [["undo", lambda x: switch_to_screen(self.master.current_screen.prev_screen)]]
        
    