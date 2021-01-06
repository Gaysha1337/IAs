from kivymd.app import MDApp
from kivy.clock import Clock

import requests, os, re
from bs4 import BeautifulSoup
from tqdm import tqdm
from functools import partial
import concurrent.futures

from utils import  download_cover_img
    

# Japanese Manga Downloader
class SenManga:
    def __init__(self, query=None):

        # https://rawdevart.com/search/?page=2&title=the
        self.query_url = "https://raw.senmanga.com/search?s={}".format(query.strip().replace(" ","+"))
        self.headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"}
        self.request_error_code = None
        self.popup_msg = None
        self.hasErrorOccured = False
        self.master = MDApp.get_running_app()

        try: 
            #headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"}
            request_obj = requests.get(self.query_url, headers=self.headers)
            self.request_error_code = request_obj.status_code
            soup = BeautifulSoup(request_obj.content,features="lxml")
            manga_divs = soup.select(".series")
            if manga_divs == None or manga_divs == []:
                self.hasErrorOccured = True
                self.popup_msg = f"No manga called {query} was found while searching Sen Manga"
                #print(self.popup_msg)
                manga_divs, self.manga_data = [], {}

            else:                 
                self.manga_choices = [div.find("p").text.strip() for div in manga_divs]
                self.manga_links = [div.find("a").get("href") for div in manga_divs]
                self.manga_covers = [div.find("img").get("src") for div in manga_divs]
                self.manga_data = dict(zip(self.manga_choices, zip(self.manga_links, self.manga_covers)))
                
        except:
            self.popup_msg = "Error: The app can't connect to the site. Check internet connection; Site may be blocked"
            self.hasErrorOccured = True
            print("Error: can't connect to Sen Manga")

    # Root is the running app
    # Links is a tuple contain: A link to the cover image and the download link        
    @staticmethod
    def download_manga(root,tile,title,links):
        title = re.sub(r'[\\/*?:"<>|]',"",title) # Sanitize title name for dir/file creation
        manga_download_link, cover_img_link = links
                
        download_cover_img(cover_img_link, cover_img_link.split("/")[-1])
        #headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"}
        r = requests.get(manga_download_link, headers=SenManga.headers)
        soup = BeautifulSoup(r.content, features="lxml")
        chapter_divs = soup.select(".list")[1]

        chapter_links = [{"link":a.get("href"),"chapter":a.text.strip()} for a in chapter_divs.select(".list .group .element .title a")][::-1]
        #chapter_links = [{"img-link":"https://rawdevart.com" + elem.get("href"), "chapter":elem.get("title")} for elem in soup.select("div.list-group-item a", text=True)][::-1]

        # A progress bar that updates once a chapter is finished downloading
        progress_bar = tqdm(chapter_links, total=len(chapter_links))
        tile.progressbar.max = len(chapter_links)

        for link_dict in chapter_links:
            chapter, link = link_dict.get("chapter"), link_dict.get("link")
            chapter = re.sub(r'[\\/*?:"<>|]',"",chapter) # Sanitize chapter name for dir/file creation

            r_ = requests.get(link, headers=SenManga.headers)
            soup_ = BeautifulSoup(r_.content, features="lxml")
            total_imgs_num = len([i.get("value") for i in soup_.select_one(".page-link select").find_all("option")])

            # TODO: Will this work on android ?
            current_chapter_dir = os.path.join(root.japanese_manga_dir,title,chapter)
            
            # If no chapter directory has been found make one and change to it
            if not os.path.isdir(current_chapter_dir): os.mkdir(current_chapter_dir)
            os.chdir(current_chapter_dir)
            
            # The images found for that specific chapter
            imgs_list = [link.replace("raw.senmanga.com", "delivery.senmanga.com/viewer") + "/" + str(img_num) for img_num in range(1,total_imgs_num + 1) ]

            # Downloads the images from the current chapter iteration using a thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
                #args = [img.get('src'), title, chapter_name, page_num]
                futures = [executor.submit(SenManga.download_img, img_url=img, title=title, chapter_name=chapter) for page_num, img in enumerate(imgs_list)]
                for future in futures:
                    result = future.result()

            # Update the progress bar after one chapter is downloaded 
            progress_bar.update(1)
            Clock.schedule_once(lambda args: SenManga.trigger_call(tile, 1), -1)

        progress_bar.close()
        Clock.schedule_once(lambda *args: tile.reset_progressbar(), 1)     

    @staticmethod
    def download_img(img_url, title, chapter_name):
        with requests.Session() as s:          
            response = s.get(img_url, headers=SenManga.headers, stream=True)
            filename = f"{title} {chapter_name} - {img_url.split('/')[-1]}.jpg"
            filename = re.sub(r'[\\/*?:"<>|]',"",filename) # Sanitize filename for creation
            
            with open(filename, "wb") as f:
                #f.write(response.content)
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            
    @staticmethod
    def trigger_call(tile,val):
        tile.progressbar.value+= val
