import os, pathlib, json, requests, re

from kivymd.app import MDApp
from kivy.utils import platform # Used to tell if platform is android
from kivymd.toast import toast
import pykakasi # Used for converting Japanese Kana to Romanji



root = MDApp.get_running_app()
# Root is the running app
# Links is a tuple contain: A link to the cover image and the download link
def download_manga(root,title, links):
    #print("in download method in utils; root=",root,", title= ",title, "cover_and_download_links=", links)
    if root.downloader == "manganelo":
        print("in utils download, current downloader is manganelo")
    elif root.downloader == "rawdevart":
        print("in utils download, current downloader is rawdevart")
    

def download_cover_img(img_link, file_name):
    r = requests.get(img_link)
    with open(file_name, "wb") as f:
        f.write(r.content)

def create_root_dir(manga_root_dir):
    # Root folder doesn't need to be sanitized; I hardcoded the name
    home_dir = os.path.expanduser("~/Desktop") if platform == "win" else None
    #manga_root_dir = os.path.join(os.path.expanduser("~/Desktop"), "Manga") if platform == "win" else None

    # Makes a "root" for all downloaded mangas; Makes a folder that keeps all ur downloaded manga
    #manga_root_dir = re.sub(r'[\\/*?:"<>|]',"",manga_root_dir)
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
            filename = os.path.join(d, "DO NOT MOVE THIS FOLDER DIRECTLY, USE THE SETTINGS.txt")
            with open(filename, "w") as f:
                f.write("")
        else:
            print(f"{d} already exists")
# Used to check if the user has moved the root TODO: add platform compatibility
def get_root_dir():
    device_root = os.path.abspath(pathlib.Path(os.path.expanduser("~")).drive)

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

print(convert_from_japanese_text("東京"))

