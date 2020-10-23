import requests, os
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
            if manga_divs == None or manga_divs == []:
                self.hasErrorOccured = True
                self.popup_msg = f"No manga called {query} was found while searching Kiss Manga"
                manga_divs, self.manga_data = [], {}

            else:
                # TODO: These vals were copy pasted from senmanga.py, they need to be changed                 
                self.manga_choices = [div.find("p").text.strip() for div in manga_divs]
                self.manga_links = [div.find("a").get("href") for div in manga_divs]
                self.manga_covers = [div.find("img").get("src") for div in manga_divs]
                self.manga_data = dict(zip(self.manga_choices, zip(self.manga_links, self.manga_covers)))
                
        except:
            self.popup_msg = "Error: The app can't connect to Kiss Manga. Check internet connection; Site may be blocked"
            self.hasErrorOccured = True
            print("Error: can't connect to Kiss Manga")


    # Root is the running app
    # Links is a tuple contain: A link to the cover image and the download link        
    @staticmethod
    def download_manga(root,tile,title,links):
        title = re.sub(r'[\\/*?:"<>|]',"",title) # Sanitize title name for dir/file creation
        manga_download_link, cover_img_link = links
       # create_manga_dirs(title) # After being called, the user should be in the dir for that manga
                
        #download_cover_img(cover_img_link, cover_img_link.split("/")[-1])
        soup = BeautifulSoup(requests.get(manga_download_link).content, features="lxml")
        chapter_links = [{"img-link":"https://rawdevart.com" + elem.get("href"), "chapter":elem.get("title")} for elem in soup.select("div.list-group-item a", text=True)][::-1]

        #print(len(chapter_links), "len of chapter links")

        progress_bar = tqdm(chapter_links, total=len(chapter_links))
        tile.progressbar.max = len(chapter_links)
        for index, link_dict in enumerate(chapter_links):
            chapter, img_url = link_dict.get("chapter"), link_dict.get("img-link")
            chapter = re.sub(r'[\\/*?:"<>|]',"",chapter) # Sanitize chapter name for dir/file creation
            soup_ = BeautifulSoup(requests.get(img_url).content, features="lxml")
            # TODO: Will this work on android ?
            current_chapter_dir = os.path.join(root.english_manga_dir,title,chapter)
            #print(os.getcwd(), "cwd")
            
            if not os.path.isdir(current_chapter_dir):
                os.mkdir(current_chapter_dir)
            os.chdir(current_chapter_dir)
            imgs_list = soup_.select("div.mb-3 img.img-fluid.not-lazy")

            for img in imgs_list:
                with requests.Session() as s:          
                    response = s.get(img.get('data-src'), stream=True)
                    filename = f"{title} {chapter} - {img.get('data-src').split('/')[-1]}"
                    
                    total_size_in_bytes, block_size= int(response.headers.get('content-length', 0)), 1024 #1 Kibibyte
                    
                    with open(filename, "wb") as f:
                        for chunk in response.iter_content(block_size):
                            f.write(chunk)
                #progress_bar.close()
            progress_bar.update(1)
            Clock.schedule_once(lambda args: KissManga.trigger_call(tile, index + 1), -1)
            #break
                
            print("remove break near line 106 for full testing")


    @staticmethod
    def trigger_call(tile,val):
        tile.progressbar.value+= val

if __name__ == "__main__":
    query = "gangsta"
    query_url = f"https://kissmanga.org/manga_list?q={query.strip().replace(' ','+')}&action=search"

    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"}
    r = requests.get(query_url, headers=headers)

    soup = BeautifulSoup(r.content, features="lxml")
    manga_divs = soup.select(".item_movies_link")
    manga_links = ["https://kissmanga.org" + div.get("href") for div in manga_divs]
    manga_choices = [div.text.strip() for div in manga_divs]
    manga_covers = [None for div in manga_divs] # No cover images available
    manga_data = dict(zip(manga_choices, zip(manga_links, manga_covers)))
    print(manga_data)

    
