import requests, os, re, concurrent.futures
from bs4 import BeautifulSoup
from tqdm import tqdm

from kivy.clock import Clock
from kivymd.toast import toast
from kivymd.app import MDApp

from utils import download_cover_img, download_image

# English Manga Downloader
class KissManga:
    def __init__(self, query=None):
        # Need to find a way to get manga from all pages
        self.master = MDApp.get_running_app()

        self.query_url = f"https://kissmanga.org/manga_list?q={query.strip().replace(' ','+')}&action=search"
        #self.request_error_code = None
        self.popup_msg = None
        self.hasErrorOccured = False
        

        try: 
            headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"}
            request_obj = requests.get(self.query_url, headers=headers)
            #self.request_error_code = request_obj.status_code
            soup = BeautifulSoup(request_obj.content,features="lxml")
            manga_divs = soup.select(".item_movies_link")
            if manga_divs == None or manga_divs == []:
                self.hasErrorOccured = True
                self.popup_msg = f"No manga called {query} was found while searching Kiss Manga"
                manga_divs, self.manga_data = [], {}

            else:               
                self.manga_choices = [a.text.strip() for a in manga_divs]
                self.manga_links = ["https://kissmanga.org" + a.get("href") for a in manga_divs]
                self.manga_covers = [KissManga.get_cover_img(a) for a in self.manga_links]
                self.manga_data = dict(zip(self.manga_choices, zip(self.manga_links, self.manga_covers)))
            
        except:
            self.popup_msg = "Error: The app can't connect to Kiss Manga. Check internet connection; Site may be blocked"
            self.hasErrorOccured = True
            print("Error: can't connect to Kiss Manga")

    @staticmethod
    def get_cover_img(url):
        return "https://kissmanga.org" + BeautifulSoup(requests.get(url).content, features="lxml").select_one("div.a_center img").get("src")
          
    @staticmethod
    def download_manga(root,tile,title,links, *args):
        title = re.sub(r'[\\/*?:"<>|]',"",title) # Sanitize title name for dir/file creation
        manga_download_link, cover_img_link = links
        download_cover_img(cover_img_link, cover_img_link.split("/")[-1])
        soup = BeautifulSoup(requests.get(manga_download_link).content, features="lxml")
        chapter_links = [{"chapter-link":"https://kissmanga.org"+ a.get("href"), "chapter-name":" ".join(a.text.strip().split())} for a in soup.select(".listing.listing8515.full a")][::-1]
        
        # A progress bar that updates once a chapter is finished downloading
        progress_bar = tqdm(chapter_links, total=len(chapter_links))
        tile.progressbar.max = len(chapter_links)

        # This loop will download all images in each chapter
        for link_dict in chapter_links:
            chapter_name, chapter_link = link_dict.get("chapter-name"), link_dict.get("chapter-link")
            chapter_name = re.sub(r'[\\/*?:"<>|]',"",chapter_name) # Sanitize chapter name for dir/file creation
            soup_ = BeautifulSoup(requests.get(chapter_link).content, features="lxml")
            
            current_chapter_dir = os.path.join(root.english_manga_dir,title,chapter_name)
            
            # If no chapter directory has been found make one and change to it
            if not os.path.isdir(current_chapter_dir): os.mkdir(current_chapter_dir)
            os.chdir(current_chapter_dir)

            imgs_list = soup_.select("#centerDivVideo img")

            # Downloads the images from the current chapter iteration using a thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
                futures = [executor.submit(KissManga.download_img, img.get('src'), title, chapter_name, page_num) for page_num, img in enumerate(imgs_list)]
                for future in futures:
                    result = future.result()

            # Update the progress bar after one chapter is downloaded           
            progress_bar.update(1)
            Clock.schedule_once(lambda args: KissManga.trigger_call(tile, 1), -1)
        # After Downloading all chapters, close and reset the progress bar
        progress_bar.close()
        Clock.schedule_once(lambda *args: tile.reset_progressbar(), 1) 
        
    
    #@mainthread
    @staticmethod
    def trigger_call(tile,val):
        tile.progressbar.value+= val

    @staticmethod
    def download_img(img_url, title, chapter_name, page_num):
        with requests.Session() as s:          
            response = s.get(img_url, stream=True)
            filename = f"{title} {chapter_name} - {page_num + 1} .{img_url.split('.')[-1]}"
            # This regex will remove the word vol to sort them alphabetically
            filename = re.sub("Vol\.\d*","",filename)
            filename = re.sub(r'[\\/*?:"<>|]',"",filename) # Sanitize filename for creation
            
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk) 

