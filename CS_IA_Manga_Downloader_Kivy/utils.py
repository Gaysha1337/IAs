#from MangaScreen import MangaScreen
from functools import partial
from glob import glob
import os, pathlib, json, requests, re, shutil, sys
from kivy.clock import Clock
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.logger import Logger
import threading

from kivymd.app import MDApp
from kivy.utils import platform # Used to tell if platform is android
from kivymd.toast import toast
import pykakasi # Used for converting Japanese Kana to Romanji

class ConfirmationDialog(MDDialog):
    def __init__(self, title, text, proceed_button_callback, **kwargs):
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

def show_confirmation_dialog(title, text, proceed_callback, cancel_callback = MDDialog.dismiss):
    master = MDApp.get_running_app()
    master.dialog = None
    if not master.dialog: 
        master.dialog = ConfirmationDialog(title=title, text=text, proceed_button_callback=proceed_callback)
    master.dialog.open()
    return master.dialog


def display_message(msg):
    toast(text=msg)
    print(msg)

def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

""" Screen Methods"""
def create_screen(name, prev_screen, content, *args, **kwargs):
    from MangaScreen import MangaScreen
    screen = MangaScreen(name=name, prev_screen=prev_screen)
    screen.add_widget(content)
    MDApp.get_running_app().screen_manager.add_widget(screen)

def switch_to_screen(screen_name, *args):
    master = MDApp.get_running_app()
    master.screen_manager.current = screen_name
    master.current_screen = master.screen_manager.get_screen(master.screen_manager.current)
    

# Kill and reload a screen to show any GUI changes
def kill_screen(screen_name, reload_func, *args):
    master = MDApp.get_running_app()
    if master.screen_manager.has_screen(screen_name):
        if not(master.currently_downloading and screen_name == "Manga Showcase"):
            master.screen_manager.clear_widgets(screens=[master.screen_manager.get_screen(screen_name)])
            Clock.schedule_once(partial(reload_func))
    else: 
        Clock.schedule_once(partial(reload_func))
    Clock.schedule_once(partial(switch_to_screen, screen_name))



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
        #display_message(f"Manga root made in {manga_root_dir}")
        filename = os.path.join(manga_root_dir, "DO NOT MOVE THE ROOT DIRECTLY, USE THE SETTINGS.txt")

        with open(filename, "w") as f:
            f.write("")
    else:
        print("You already have a manga root")
    return resource_path(manga_root_dir)


def create_language_dirs(language_dirs:list):
    # Folders don't need to be sanitized; I hardcoded the names
    for d in language_dirs:
        if not os.path.isdir(d):
            os.mkdir(d)
            display_message("Manga root folder Created and folders for english and japanese manga have been made")
        else:
            print(f"{d} already exists")

#https://stackoverflow.com/questions/5983320/moving-files-and-dir-even-if-they-already-exist-in-dest

# Recursive function to move all manga from `src_dir` to `dest_dir`
def move_manga_root(src_dir, dest_dir):
    #fileList = os.listdir(src_dir)
    manga_root_dir_contents = ['Raw Japanese Manga', 'English Manga', 'logs','DO NOT MOVE THE ROOT DIRECTLY, USE THE SETTINGS.txt']
    fileList = [path for path in os.listdir(src_dir) if path in manga_root_dir_contents]
    
    for i in fileList:
        src, dest = resource_path(os.path.join(src_dir, i)), resource_path(os.path.join(dest_dir, i))
        #print("src: ", src, "dest", dest, sep="\n")
        if os.path.exists(dest):
            if os.path.isdir(dest):
                move_manga_root(src, dest)
                continue
            else:
                os.remove(dest)
        shutil.move(src, dest_dir)
    

def create_manga_dirs(downloader, title):    
    master = MDApp.get_running_app()
    title = re.sub(r'[\\/*?:"<>|]',"",title) # Sanitize title name for dir/file creation
    
    english_manga_dir, japanese_manga_dir =  resource_path(master.english_manga_dir), resource_path(master.japanese_manga_dir)
    
    # Determines whether the manga being downloaded is in english or japanese
    current_manga_dir = os.path.join(english_manga_dir, title) if downloader in ["kissmanga", "manganelo"] else os.path.join(japanese_manga_dir, title)
    current_manga_dir = resource_path(current_manga_dir)
    # Production code
    
    if not os.path.isdir(current_manga_dir):
        os.mkdir(current_manga_dir)
        display_message(f"A folder for {title.capitalize()} has been made")
    else:
        display_message(f"You already have a folder for {title.capitalize()}, it will be downloaded once again")
        #shutil.rmtree(current_manga_dir)
    #os.mkdir(current_manga_dir)
    os.chdir(current_manga_dir)
    
    # Debug code
    """
    if os.path.isdir(current_manga_dir):
        #os.mkdir(current_manga_dir)
        #shutil.rmtree(current_manga_dir)
        display_message(f"[Debug Mode]: If a manga is downloaded it will be deleted")
        #display_message(f"A folder for {title.capitalize()} has been made in {}")
    #else:
        #display_message(f"You already have a folder for {title.capitalize()}, it will be downloaded once again")
        #shutil.rmtree(current_manga_dir)
    os.mkdir(current_manga_dir)
    os.chdir(current_manga_dir)
    """
    #display_message(f"A folder for {title.capitalize()} has been made in {current_manga_dir}")


# Text input conversion
def convert_from_japanese_text(text):
    kks = pykakasi.kakasi()
    kks.setMode("H","a") # Hiragana to ascii, default: no conversion
    kks.setMode("K","a") # Katakana to ascii, default: no conversion
    kks.setMode("J","a") # Japanese to ascii, default: no conversion
    kks.setMode("r","Hepburn") # default: use Hepburn Roman table
    kks.setMode("s", True) # add space, default: no separator

    conv = kks.getConverter()
    return conv.do(text)
    """
    try:
        conv = kks.getConverter()
        return conv.do(text)
    except KeyError:
        return text
    """
    #return " ".join([d.get("hepburn") for d in kks.convert(text)])


if __name__ == "__main__":

    #l = input("type anything") #"可愛い"
    #print(convert_from_japanese_text(l))

    src = "/home/dimitriy/.config/mangadownloader/Manga"
    dest = "/home/dimitriy/.config/mangadownloader"
    move_manga_root(src, dest)

    

