from kivymd.app import MDApp
from kivy.clock import Clock

import requests, os, re, concurrent.futures
from bs4 import BeautifulSoup
from tqdm import tqdm

from utils import  download_cover_img, resource_path
    

# Japanese Manga Downloader
class SenManga:
    headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
        }
    def __init__(self, query=None):
        self.query_url = f"https://raw.senmanga.com/search?s={query.strip().replace(' ','+')}"
        self.popup_msg = None
        self.hasErrorOccured = False
        
        
        try: 
            # Parsing HTML for any manga based on client's input
            request_obj = requests.get(self.query_url, headers=SenManga.headers)
            soup = BeautifulSoup(request_obj.content,features="lxml")
            manga_divs = soup.select(".listupd .item")

            # Error handling if no manga were found
            if manga_divs == None or manga_divs == []:
                self.hasErrorOccured = True
                self.popup_msg = f"No manga called {query} was found while searching Sen Manga"
                manga_divs, self.manga_data = [], {}

            else:       
                self.manga_choices = [div.select_one(".series-title").text.strip() for div in manga_divs]
                self.manga_links = [div.find("a").get("href") for div in manga_divs]
                self.manga_covers = [div.find("img").get("src") for div in manga_divs]
                self.manga_data = dict(zip(self.manga_choices, zip(self.manga_links, self.manga_covers)))
                
        except Exception as e:
            self.popup_msg = "Error: The app can't connect to the site. Check internet connection; Site may be blocked"
            self.hasErrorOccured = True
            print("Error: can't connect to Sen Manga")
     
    @staticmethod
    def download_manga(tile,title,links):
        master = MDApp.get_running_app()
        title = re.sub(r'[\\/*?:"<>|]',"",title) # Sanitize title name for dir/file creation
        
        manga_download_link, cover_img_link = links
        cover_img_filename = os.path.join(master.japanese_manga_dir,title, os.path.basename(cover_img_link))
        download_cover_img(cover_img_link, resource_path(cover_img_filename))       

        #headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"}
        r = requests.get(manga_download_link, headers=SenManga.headers)

        # Parsing HTML for all the chapter links
        soup = BeautifulSoup(r.content, features="lxml")
        chapter_divs = soup.select(".chapter-list > li > a.series")
        chapter_links = [{"link":a.get("href"),"chapter":a.text.strip()} for a in chapter_divs][::-1]

        # A progress bar that updates once a chapter is finished downloading
        progress_bar = tqdm(chapter_links, total=len(chapter_links))
        tile.progressbar.max = len(chapter_links)


        for link_dict in chapter_links:
            chapter, link = link_dict.get("chapter"), link_dict.get("link")
            chapter = re.sub(r'[\\/*?:"<>|]',"",chapter) # Sanitize chapter name for dir/file creation

            current_chapter_dir = os.path.join(master.japanese_manga_dir,title,chapter)
            
            # If no chapter directory has been found make one and change to it
            if not os.path.isdir(current_chapter_dir): os.mkdir(current_chapter_dir)
            os.chdir(current_chapter_dir)
            
            # Parse chapter's HTML for images
            current_chapter_soup = BeautifulSoup(requests.get(link, headers=SenManga.headers).content, features="lxml")
            total_imgs_num = int(current_chapter_soup.select(".page-list option")[-1].get("value"))

            imgs_list = [link.replace("raw.senmanga.com", "raw.senmanga.com/viewer") + "/" + str(img_num + 1) for img_num in range(total_imgs_num) ]
            
            # Downloads the images from the current chapter iteration using a thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
                #args = [img.get('src'), title, chapter_name, page_num]
                futures = [executor.submit(SenManga.download_img, img_url, title, chapter, current_chapter_dir) for img_url in imgs_list]
                for future in futures:
                    result = future.result()

            # Update the progress bar after one chapter is downloaded 
            progress_bar.update(1)
            Clock.schedule_once(lambda args: SenManga.trigger_call(tile, 1), -1)
        # After Downloading all chapters, close and reset the progress bar
        progress_bar.close()
        Clock.schedule_once(lambda *args: tile.reset_progressbar(), 1)     

    @staticmethod
    def download_img(img_url, title, chapter_name, chapter_dir):
        with requests.Session() as s:          
            response = s.get(img_url, headers=SenManga.headers, stream=True)
            filename = f"{title} {chapter_name} - {img_url.split('/')[-1]}.jpg"
            filename = re.sub(r'[\\/*?:"<>|]',"",filename) # Sanitize filename for creation
            
            with open(os.path.join(chapter_dir,filename), "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            
    @staticmethod
    def trigger_call(tile,val):
        tile.progressbar.value+= val


if __name__ == "__main__":
    x = SenManga("kage")