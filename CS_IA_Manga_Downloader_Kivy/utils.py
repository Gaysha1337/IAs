import os, pathlib, json, requests, re, shutil
import threading

from kivymd.app import MDApp
from kivy.utils import platform # Used to tell if platform is android
from kivymd.toast import toast
import pykakasi # Used for converting Japanese Kana to Romanji

root = MDApp.get_running_app()


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
    # Root folder doesn't need to be sanitized; I hardcoded the name
    home_dir = os.path.expanduser("~/Desktop") if platform == "win" else None
    #manga_root_dir = os.path.join(os.path.expanduser("~/Desktop"), "Manga") if platform == "win" else None

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
            """
            filename = os.path.join(d, "DO NOT MOVE THIS FOLDER DIRECTLY, USE THE SETTINGS.txt")
            with open(filename, "w") as f:
                f.write("")
            """
        else:
            print(f"{d} already exists")

#https://stackoverflow.com/questions/5983320/moving-files-and-dir-even-if-they-already-exist-in-dest
def move_manga_root(src_dir, dest_dir):
    fileList = os.listdir(src_dir)
    for i in fileList:
        src, dest = os.path.join(src_dir, i), os.path.join(dest_dir, i)
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
    title = re.sub(r'[\\/*?:"<>|]',"",title) # Sanitize title name for dir/file creation
    
    english_manga_dir, japanese_manga_dir =  MDApp.get_running_app().english_manga_dir, MDApp.get_running_app().japanese_manga_dir
    
    # Determines whether the manga being downloaded is in english or japanese
    current_manga_dir = os.path.join(english_manga_dir, title) if downloader in ["kissmanga", "manganelo"] else os.path.join(japanese_manga_dir, title)
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

# Used to check if the user has moved the root TODO: add platform compatibility
def get_root_dir():
    device_root = os.path.abspath(pathlib.Path(os.path.expanduser("~")).drive)

if __name__ == "__main__":
    print(convert_from_japanese_text("    東京++++"))

