from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.toast.kivytoast.kivytoast import toast

from kivymd.uix.button import MDFlatButton, MDIconButton
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
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')# Window.bind(on_key_down=self._on_keyboard_down)

        #if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use to change the keyboard layout.
            #pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
    def on_pre_enter(self, *args, **kwargs):
        self.add_widget(ToolBar())


    # Keyboard methods
    # print('The key', keycode, 'have been pressed', ' - text is %r' % text, ' - modifiers are %r' % modifiers, sep="\n")
    def _keyboard_closed(self):
        print('My keyboard have been closed!',self.name)

        # Hides the keyboard when a button is pressed on android, except for the input page
        if self.name != "Manga Input Page":
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None

    # self, keyboard, keycode, text, modifiers, *args
    # self, instance, keycode, scancode, text, modifiers
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers, *args):
        print(self, keyboard, keycode, text, modifiers, *args)

        
        if keycode[1] in ["escape", 27]:
            if self.master.current_screen.name == "Landing Page":
                if not isinstance(self.master.dialog, ConfirmationDialog): 
                    self.master.on_request_close()
                    self.master.dialog = None
            else: 
                switch_to_screen(self.master.current_screen.prev_screen)
            
            return True

        # Keyboard shortcuts to go between the images of a chapter
        if self.name == "Manga Reader Carousel" and platform != "android":
            if keycode[1] in ["right","down", "d", "s"]: 
                self.master.manga_reader.next_btn.trigger_action(0)
                return True

            if keycode[1] in ["left","up", "a", "w"]:
                self.master.manga_reader.prev_btn.trigger_action(0)
                return True
                
        # Return True to accept the key. Otherwise, it will be used by the system.
        #return True 
        return False
        
    
class ToolBar(MDToolbar):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.master = MDApp.get_running_app()
        self.title = self.master.title
        self.id = "Toolbar"
        self.pos_hint = {"top":1}
        self.elevation = 10
        self.left_action_items = [["home", lambda x: switch_to_screen("Landing Page")],["cog", lambda x: self.master.open_settings()]]
        self.right_action_items = [["undo", lambda x: switch_to_screen(self.master.current_screen.prev_screen)]]
        
    