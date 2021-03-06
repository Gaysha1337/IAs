from kivymd.app import MDApp
from kivy.clock import Clock, mainthread

import requests, os, re, concurrent.futures
from tqdm import tqdm
from bs4 import BeautifulSoup

from utils import download_cover_img
    

# This downloader is for English Manga
class MangaNelo:
    headers = {
        "referer": "https://chap.manganelo.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
    }
    def __init__(self,query=None):
        self.query_url = f"https://m.manganelo.com/search/story/{query.strip().replace(' ','_')}"
        self.popup_msg = None
        self.hasErrorOccured = False
        
        try:
            # Parsing HTML for any manga based on client's input 
            request_obj = requests.get(self.query_url)
            soup = BeautifulSoup(request_obj.content,features="lxml")
            query_search_results = soup.find("div",attrs={"class":"panel-search-story"})
            
            # Checks to see if the user's manga input was found
            if query_search_results == None or query_search_results == []:
                self.hasErrorOccured = True
                self.popup_msg = f"No manga called {query} was found while searching Manganelo"
                query_search_results, self.manga_data = [], {}
            else:
                self.manga_links = [i.find("a").get("href") for i in query_search_results.findAll("h3")] 
                self.manga_choices = [i.find("a").text.replace("\n","") for i in query_search_results.findAll("h3")] # Manga titles
                self.manga_cover_imgs = [i.get("src") for i in query_search_results.find_all("img")]
                self.manga_data = dict(zip(self.manga_choices, zip(self.manga_links, self.manga_cover_imgs)))
        except:
            self.popup_msg = "Error: The app can't connect to the site. Check internet connection; Site may be blocked"
            self.hasErrorOccured = True
            print("Error: can't connect to Manganelo")

    @staticmethod
    def download_manga(tile, title, links, *args):
        master = MDApp.get_running_app()
        title = re.sub(r'[\\/*?:"<>|]',"",title) # Sanitize title name for dir/file creation
        
        manga_download_link, cover_img_link = links        
        download_cover_img(cover_img_link, cover_img_link.split("/")[-1])

        # Parsing HTML for all the chapter links
        soup = BeautifulSoup(requests.get(manga_download_link).content, features="lxml")
        chapter_links = [
            {"imgs-link":link.get("href"), "chapter":link.text.strip()} 
            for link in soup.select("a.chapter-name.text-nowrap")
        ][::-1]
        
        # A progress bar that updates once a chapter is finished downloading
        progress_bar = tqdm(chapter_links, total=len(chapter_links))
        tile.progressbar.max = len(chapter_links)

        # This loop will download all images in each chapter
        for link_dict in chapter_links:
            chapter, link = link_dict.get("chapter"), link_dict.get("imgs-link")
            chapter = re.sub(r'[\\/*?:"<>|]',"",chapter) # Sanitize chapter name for dir/file creation

            current_chapter_dir = os.path.join(master.english_manga_dir,title,chapter)
            
            # If no chapter directory has been found, make one and change to it
            if not os.path.isdir(current_chapter_dir): os.mkdir(current_chapter_dir)
            os.chdir(current_chapter_dir)

            # Parse chapter's HTML for images
            current_chapter_soup = BeautifulSoup(requests.get(link, headers = MangaNelo.headers).content, features="lxml")
            imgs_list = current_chapter_soup.select("div.container-chapter-reader img")

            # Downloads the images from the current chapter iteration using a thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
                #args = [img.get('src'), title, chapter_name, page_num]
                futures = [executor.submit(MangaNelo.download_img, img.get('src'), img.get('title'), current_chapter_dir) for img in imgs_list]
                for future in futures:
                    result = future.result()
           
            # Update the progress bar after one chapter is downloaded 
            progress_bar.update(1)
            Clock.schedule_once(lambda *args: MangaNelo.trigger_call(tile, 1), -1)
        # After Downloading all chapters, close and reset the progress bar
        progress_bar.close()
        Clock.schedule_once(lambda *args: tile.reset_progressbar(), 1) 
        

    @staticmethod
    def download_img(img_url, title, chapter_dir):
        with requests.Session() as s:          
            response = s.get(img_url, headers=MangaNelo.headers, stream=True)
            filename = f"{title} + {img_url.split('/')[-1]}"
            filename = re.sub("Vol\.\d*","",filename) # This regex will remove the word vol to sort them alphabetically
            filename = re.sub(r'[\\/*?:"<>|]',"",filename) # Sanitize filename for creation
            
            with open(os.path.join(chapter_dir, filename), "wb") as f:
                #f.write(response.content)
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            
    #@mainthread
    @staticmethod
    def trigger_call(tile,val):
        tile.progressbar.value+= val
