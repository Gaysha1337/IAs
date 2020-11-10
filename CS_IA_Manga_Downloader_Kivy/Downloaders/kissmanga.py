import requests, os, re
from bs4 import BeautifulSoup
from tqdm import tqdm
from functools import partial
from kivy.clock import Clock, mainthread
#from utils import create_manga_dirs, download_cover_img, download_manga
from kivymd.toast import toast
from kivymd.app import MDApp

# English Manga Downloader
class KissManga:
    def __init__(self, query=None):
        # Need to find a way to get manga from all pages
        self.query_url = f"https://kissmanga.org/manga_list?q={query.strip().replace(' ','+')}&action=search"
        self.request_error_code = None
        self.popup_msg = None
        self.hasErrorOccured = False
        self.master = MDApp.get_running_app()

        try: 
            headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"}
            request_obj = requests.get(self.query_url, headers=headers)
            self.request_error_code = request_obj.status_code
            soup = BeautifulSoup(request_obj.content,features="lxml")
            manga_divs = soup.select(".item_movies_link")
            if manga_divs == None:
                self.hasErrorOccured = True
                self.popup_msg = f"No manga called {query} was found while searching Kiss Manga"
                manga_divs, self.manga_data = [], {}

            else:
                # TODO: These vals were copy pasted from senmanga.py, they need to be changed                 
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
        
    # Root is the running app
    # Links is a tuple contain: A link to the cover image and the download link        
    @staticmethod
    def download_manga(root,tile,title,links):
        title = re.sub(r'[\\/*?:"<>|]',"",title) # Sanitize title name for dir/file creation
        manga_download_link, cover_img_link = links
       
        soup = BeautifulSoup(requests.get(manga_download_link).content, features="lxml")
        chapter_links = [{"img-link":"https://rawdevart.com" + elem.get("href"), "chapter":elem.text.strip()} for elem in soup.select(".listing.listing8515.full a", text=True)][::-1]
        chapter_links = [{"chapter-link":"https://kissmanga.org"+ a.get("href"), "chapter-name":" ".join(a.text.strip().split())} for a in soup.select(".listing.listing8515.full a")][::-1]
        #print(len(chapter_links), "len of chapter links")

        progress_bar = tqdm(chapter_links, total=len(chapter_links))
        tile.progressbar.max = len(chapter_links)
        for index, link_dict in enumerate(chapter_links):
            chapter_name, chapter_link = link_dict.get("chapter-name"), link_dict.get("chapter-link")
            chapter_name = re.sub(r'[\\/*?:"<>|]',"",chapter_name) # Sanitize chapter name for dir/file creation
            soup_ = BeautifulSoup(requests.get(chapter_link).content, features="lxml")
            # TODO: Will this work on android ?
            current_chapter_dir = os.path.join(root.english_manga_dir,title,chapter_name)
            #print(os.getcwd(), "cwd")
            
            if not os.path.isdir(current_chapter_dir):
                os.mkdir(current_chapter_dir)
            os.chdir(current_chapter_dir)
            imgs_list = soup_.select("#centerDivVideo img")

            for img in imgs_list:
                with requests.Session() as s:          
                    response = s.get(img.get('src'))
                    filename = f"{title} {chapter_name} - .{img.get('src').split('.')[-1]}"
                                        
                    with open(filename, "wb") as f:
                        f.write(response.content)
            progress_bar.update(1)
            Clock.schedule_once(lambda args: KissManga.trigger_call(tile, 1), -1)
            #break
    
        progress_bar.close()
    @staticmethod
    def trigger_call(tile,val):
        tile.progressbar.value+= val

if __name__ == "__main__":
    query = "gangsta"
    def get_manga_titles():
        
        query_url = f"https://kissmanga.org/manga_list?q={query.strip().replace(' ','+')}&action=search"

        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"}
        r = requests.get(query_url, headers=headers)

        soup = BeautifulSoup(r.content, features="lxml")
        manga_divs = soup.select(".item_movies_link")
        manga_links = ["https://kissmanga.org" + div.get("href") for div in manga_divs]
        manga_choices = [div.text.strip() for div in manga_divs]
        manga_covers = [None for div in manga_divs] # No cover images available
        manga_data = dict(zip(manga_choices, zip(manga_links, manga_covers)))
    
    def download_manga():
        chapters_url = "https://kissmanga.org/manga/read_tokyo_ghoul_manga_online_free4"
        r = requests.get(chapters_url)
        soup = BeautifulSoup(r.content, features="lxml")
        chapter_links = [{"chapter-url":"https://kissmanga.org"+ a.get("href"), "chapter-name":" ".join(a.text.strip().split())} for a in soup.select(".listing.listing8515.full a")][::-1]

        print(chapter_links)

    KissManga("tokyo")
    
