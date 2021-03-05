from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.settings import Settings
from kivy.clock import Clock
from kivymd.toast.kivytoast.kivytoast import toast

from kivymd.uix.button import MDFlatButton, MDIconButton
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField

from kivy.utils import platform
from utils import switch_to_screen, show_confirmation_dialog, ConfirmationDialog

from functools import partial


class MangaScreen(Screen): 
    def __init__(self, prev_screen="Landing Page",**kwargs):
        super().__init__(**kwargs)
        self.master = MDApp.get_running_app()
        self.prev_screen = prev_screen

                        
    def on_pre_enter(self, *args, **kwargs):
        self.add_widget(ToolBar())
        if self.name == "Manga Input Page":# or (self.name == "Manga Reader Carousel" and platform != "android"):
            self.config_keyboard()
            Window.unbind(on_key_down=self.master._on_keyboard_down)
            self.master.manga_search_page.input_bar.focus = True
            

    def on_leave(self, *args):
        if self.name == "Manga Input Page": #or (self.name == "Manga Reader Carousel" and platform != "android"):
            self._keyboard_closed()
            Window.bind(on_key_down=self.master._on_keyboard_down)
        
    # Keyboard methods
    def config_keyboard(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
    
    """    
        if platform == "android":
            from pyjnius import autoclass
            from android.runnable import run_on_ui_thread
            import android
            
            
            @run_on_ui_thread
            def set_android_keyboard_state(state = "hide"):
                WindowManager = autoclass('android.view.WindowManager')
                python_activity = autoclass('org.kivy.android.PythonActivity').mActivity
                window = python_activity.getWindow()
                new_state = WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN if state == "hide" else WindowManager.LayoutParams.SOFT_INPUT_STATE_VISIBLE
                window.setSoftInputMode(new_state)
            
            if self.name != "Manga Input Page":
                set_android_keyboard_state("hide")
            else: 
                set_android_keyboard_state("show")
    """
            
    def _keyboard_closed(self):
        print('My keyboard have been closed! Class: Manga Screen',self.name)
        if self._keyboard != None:
            self._keyboard.unbind(on_key_down=self.master._on_keyboard_down)
            self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers, *args):
        print("manga screen on keyboard meth",self, keyboard, keycode, text, modifiers, *args)
        
        if keycode[1] in ["escape", 27]:
            settings_open = self.master.close_settings()

            if isinstance(self.master._app_settings, Settings): 
                self.master.close_settings()
                self.master.destroy_settings()
            if not settings_open: 
                switch_to_screen(self.master.current_screen.prev_screen)
        # Return True to accept the key. Otherwise, it will be used by the system.
        return True
    
class ToolBar(MDToolbar):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.master = MDApp.get_running_app()
        self.title = self.master.title
        self.id = "Toolbar"
        self.pos_hint = {"top":1}
        self.left_action_items = [["home", lambda x: switch_to_screen("Landing Page")],["cog", lambda x: self.master.open_settings()]]
        self.right_action_items = [["undo", lambda x: switch_to_screen(self.master.current_screen.prev_screen)]]
        
    