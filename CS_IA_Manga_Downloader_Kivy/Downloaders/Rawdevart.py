from kivymd.app import MDApp
from kivy.clock import Clock, mainthread

import requests, os, re, concurrent.futures
from bs4 import BeautifulSoup
from tqdm import tqdm

from utils import download_cover_img, resource_path

# Japanese Manga Downloader
class RawDevArt:
    def __init__(self, query=None):
        self.query_url = f"https://rawdevart.com/search/?title={query.strip().replace(' ','+')}"
        self.popup_msg = None
        self.hasErrorOccured = False
        
        try: 
            # Parsing HTML for any manga based on client's input
            request_obj = requests.get(self.query_url)
            soup = BeautifulSoup(request_obj.content,"html.parser")
            manga_divs = soup.select("div.row.mb-3 > div.col-6.col-md-4.col-lg-3.col-xl-2.px-1.mb-2.lister-layout")
            
            # Error handling if no manga were found
            if manga_divs == None or manga_divs == []:
                self.hasErrorOccured = True
                self.popup_msg = f"No manga called {query} was found while searching Raw Dev Art"
                manga_divs, self.manga_data = [], {}

            else:                 
                self.manga_choices = [div.select_one("a.head").text.replace("\n","") for div in manga_divs]
                self.manga_links = ["https://rawdevart.com" + div.select_one("a.head").get("href") for div in manga_divs]
                self.manga_covers = ["https://rawdevart.com" + div.select_one("img.img-fluid").get("src") for div in manga_divs]
                self.manga_data = dict(zip(self.manga_choices, zip(self.manga_links, self.manga_covers)))
                
        except:
            self.popup_msg = "Error: The app can't connect to the site. Check internet connection; Site may be blocked"
            self.hasErrorOccured = True
            print("Error: can't connect to Raw Dev Art")
                
    @staticmethod
    def download_manga(tile, title, links, *args):
        master = MDApp.get_running_app()
        title = re.sub(r'[\\/*?:"<>|]',"",title) # Sanitize title name for dir/file creation
        
        manga_download_link, cover_img_link = links
        #cover_img_filename = os.path.join(master.japanese_manga_dir,title, cover_img_link.split("/")[-1])
        cover_img_filename = os.path.join(master.japanese_manga_dir,title, os.path.basename(cover_img_link))
        download_cover_img(cover_img_link, resource_path(cover_img_filename))
        print("cover image link: ", cover_img_link, "basename: ", os.path.basename(cover_img_link))               
        

        soup = BeautifulSoup(requests.get(manga_download_link).content, features="lxml")

        # Get the chapter images and the title of the chapter
        chapter_links = [
            {"chapter-imgs-link":"https://rawdevart.com" + elem.get("href"), "chapter":elem.get("title")} 
            for elem in soup.select("div.list-group-item a", text=True)
        ][::-1]

        # A progress bar that updates once a chapter is finished downloading
        progress_bar = tqdm(chapter_links, total=len(chapter_links))
        tile.progressbar.max = len(chapter_links)
        
        # This loop will download all images in each chapter
        for link_dict in chapter_links:
            chapter, img_url = link_dict.get("chapter"), link_dict.get("chapter-imgs-link") 
            chapter = re.sub(r'[\\/*?:"<>|]',"",chapter) # Sanitize chapter name for dir/file creation
            
            current_chapter_dir = os.path.join(master.japanese_manga_dir,title,chapter)
            
            # If no chapter directory has been found make one and change to it
            if not os.path.isdir(current_chapter_dir): os.mkdir(current_chapter_dir)
            os.chdir(current_chapter_dir)

            # The images found for that specific chapter
            current_chapter_soup = BeautifulSoup(requests.get(img_url).content, features="lxml")
            imgs_list = current_chapter_soup.select("div.mb-3 img.img-fluid.not-lazy")

            # Downloads the images from the current chapter iteration using a thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
                #args = [img.get('src'), title, chapter_name, page_num]
                futures = [
                    executor.submit(RawDevArt.download_img, img.get('data-src'), title, chapter, current_chapter_dir) 
                    for img in imgs_list
                ]
                for future in futures:
                    result = future.result()
            # Update the progress bar after one chapter is downloaded 
            progress_bar.update(1)
            Clock.schedule_once(lambda *args: RawDevArt.trigger_call(tile, 1), -1)
        # After Downloading all chapters, close and reset the progress bar
        progress_bar.close()
        Clock.schedule_once(lambda *args: tile.reset_progressbar(), 1) 
        
    @staticmethod
    def trigger_call(tile,val):
        tile.progressbar.value += val

    @staticmethod
    def download_img(img_url, title, chapter_name, chapter_dir):
        with requests.Session() as s:          
            response = s.get(img_url, stream=True)
            filename = f"{title} {chapter_name} - {img_url.split('/')[-1]}"
            filename = re.sub(r'[\\/*?:"<>|]',"",filename) # Sanitize filename for creation
            
            with open(os.path.join(chapter_dir, filename), "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)