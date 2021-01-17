from functools import partial
import os, pathlib, json, requests, re, shutil, sys
from kivy.clock import Clock
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
import threading

from kivymd.app import MDApp
from kivy.utils import platform # Used to tell if platform is android
from kivymd.toast import toast
import pykakasi # Used for converting Japanese Kana to Romanji


class PausableThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        self._event = threading.Event()
        if target:
            args = (self,) + args
        super(PausableThread, self).__init__(group, target, name, args, kwargs)

    def is_paused(self):
        return self._event.is_set()

    def pause(self):
        self._event.clear()

    def resume(self):
        self._event.set()

    def wait_if_paused(self):
        print("about to call event.wait()")
        self._event.wait()

class ConfirmationDialog(MDDialog):
    def __init__(self, title, text, proceed_button_callback,**kwargs):
        self.master = MDApp.get_running_app()
        self.title = title
        self.text = text
        self.auto_dismiss = False
        self.proceed_button_callback = proceed_button_callback
        self.buttons =[
            MDFlatButton(text="PROCEED", on_release= lambda *args:Clock.schedule_once(partial(self.proceed_button_callback))),
            MDFlatButton(text="CANCEL", on_release= self.dismiss)
        ]
        # Parent constructor is here to create the buttons; DO NOT MOVE!
        super().__init__(**kwargs)
        
def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)



""" Screen Methods"""

def switch_to_screen(screen_name):
    master = MDApp.get_running_app()
    master.screen_manager.current = screen_name
    master.current_screen = master.screen_manager.get_screen(master.screen_manager.current)
    
    #print(MDApp.get_running_app().current_screen.name, "switch method")

# Kill and reload a screen to show any GUI changes
def kill_screen(screen_name, reload_func, *args):
    master = MDApp.get_running_app()
    if master.screen_manager.has_screen(screen_name):
        # The user can check if the progress of any downloads
        if not master.currently_downloading:
            master.screen_manager.clear_widgets(screens=[master.screen_manager.get_screen(screen_name)])
    reload_func()
    switch_to_screen(screen_name)

def show_confirmation_dialog(title, text, proceed_callback):
    master = MDApp.get_running_app()
    master.dialog = None
    if not master.dialog: 
        master.dialog = ConfirmationDialog(title = title, text = text, proceed_button_callback = proceed_callback)
    master.dialog.open()


""" Downloading Functions """
# Downloads the cover image of a manga
def download_cover_img(img_link, file_name):
    r = requests.get(img_link)
    with open(file_name, "wb") as f:
        print("Download cover image in: ", os.getcwd())
        f.write(r.content)

def download_image(filename, resp):
    with open(filename, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=1024):
            f.write(chunk)

def create_root_dir(manga_root_dir):
    manga_root_dir = resource_path(manga_root_dir)
    
    # Makes a "root" folder to store all your downloaded manga
    if not os.path.isdir(manga_root_dir):
        os.mkdir(manga_root_dir)
        print("Manga root made; Current directory {manga_root_dir}")
        toast("Manga root made; Current directory {manga_root_dir}")
        filename = os.path.join(manga_root_dir, "DO NOT MOVE THE ROOT DIRECTLY, USE THE SETTINGS.txt")

        with open(filename, "w") as f:
            f.write("")
    else:
        print("You already have a manga root")
    return manga_root_dir


def create_language_dirs(language_dirs:list):
    # Folders don't need to be sanitized; I hardcoded the names
    for d in language_dirs:
        if not os.path.isdir(d):
            os.mkdir(d)
            print(f"Made directory for {d}")
            toast(f"Made directory for {d}")
        else:
            print(f"{d} already exists")

#https://stackoverflow.com/questions/5983320/moving-files-and-dir-even-if-they-already-exist-in-dest
def move_manga_root(src_dir, dest_dir):
    fileList = os.listdir(src_dir)
    for i in fileList:
        src, dest = resource_path(os.path.join(src_dir, i)), resource_path(os.path.join(dest_dir, i))
        if os.path.exists(dest):
            if os.path.isdir(dest):
                move_manga_root(src, dest)
                continue
            else:
                os.remove(dest)
        shutil.move(src, dest_dir)

def create_manga_dirs(downloader, title):
    #manga_root_dir = os.path.join(os.path.expanduser("~/Desktop"), "Manga")
    home_dir = os.path.expanduser("~/Desktop") if platform == "win" else None
    master = MDApp.get_running_app()
    title = re.sub(r'[\\/*?:"<>|]',"",title) # Sanitize title name for dir/file creation
    
    english_manga_dir, japanese_manga_dir =  resource_path(master.english_manga_dir), resource_path(master.japanese_manga_dir)
    
    # Determines whether the manga being downloaded is in english or japanese
    current_manga_dir = os.path.join(english_manga_dir, title) if downloader in ["kissmanga", "manganelo"] else os.path.join(japanese_manga_dir, title)
    current_manga_dir = resource_path(current_manga_dir)
    
    #current_manga_dir = re.sub(r'[\\/*?:"<>|]',"",title) # Sanitizes the filename
    print(current_manga_dir, "cur mg dir")

    if not os.path.isdir(current_manga_dir):
        os.mkdir(current_manga_dir)
        print(f"A folder for {title.capitalize()} has been made in the manga root directory")
        #toast("A folder for {title.capitalize()} has been made in the manga root directory")
    else:
        print("You already have a folder for {}, if you would like to redownload this manga, please delete its folder".format(title.capitalize()))
        #toast("You already have a folder for {}, if you would like to redownload this manga, please delete its folder".format(title.capitalize()))
    os.chdir(current_manga_dir)

def convert_from_japanese_text(text):
    kks = pykakasi.kakasi()
    result = kks.convert(text)
    return " ".join([d.get("hepburn") for d in result])

if __name__ == "__main__":
    print(convert_from_japanese_text("    東京++++"))

