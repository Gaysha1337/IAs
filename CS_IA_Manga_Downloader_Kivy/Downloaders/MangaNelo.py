from kivy.clock import Clock, mainthread

import requests, os, re
from tqdm import tqdm
from bs4 import BeautifulSoup
import concurrent.futures

from utils import download_cover_img
    

# This downloader is for English Manga
class MangaNelo:
    headers = {
            "referer": "https://chap.manganelo.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        }
    def __init__(self,query=None):
        self.query_url = "https://m.manganelo.com/search/story/{}".format(query.strip().replace(" ","_"))
        self.request_error_code = None
        self.popup_msg = None
        self.hasErrorOccured = False
        
        try: 
            request_obj = requests.get(self.query_url)
            self.request_error_code = request_obj.status_code
            soup = BeautifulSoup(request_obj.content,"html.parser")
            query_search_results = soup.find("div",attrs={"class":"panel-search-story"})
            
            # Checks to see if the user's manga input was found
            if query_search_results == None:
                self.hasErrorOccured = True
                self.popup_msg = f"No manga called {query} was found while searching Manganelo"
                print(self.popup_msg)
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
    def download_manga(root, tile, title, links, *args):
        title = re.sub(r'[\\/*?:"<>|]',"",title) # Sanitize title name for dir/file creation
        manga_download_link, cover_img_link = links        
        download_cover_img(cover_img_link, cover_img_link.split("/")[-1])

        soup = BeautifulSoup(requests.get(manga_download_link).content, features="lxml")
        
        chapter_links = [{"imgs-link":link.get("href"), "chapter":link.text.strip()} for link in soup.select("a.chapter-name.text-nowrap")][::-1]
        
        # A progress bar that updates once a chapter is finished downloading
        progress_bar = tqdm(chapter_links, total=len(chapter_links))
        tile.progressbar.max = len(chapter_links)

        # This loop will download all images in each chapter
        for link_dict in chapter_links:
            chapter, link = link_dict.get("chapter"), link_dict.get("imgs-link")
            chapter = re.sub(r'[\\/*?:"<>|]',"",chapter) # Sanitize chapter name for dir/file creation

            r_ = requests.get(link, headers= MangaNelo.headers)
            soup_ = BeautifulSoup(r_.content, features="lxml")
            current_chapter_dir = os.path.join(root.english_manga_dir,title,chapter)
            

            # If no chapter directory has been found make one and change to it
            if not os.path.isdir(current_chapter_dir): os.mkdir(current_chapter_dir)
            os.chdir(current_chapter_dir)

            # The images found for that specific chapter
            imgs_list = soup_.select("div.container-chapter-reader img")

            # Downloads the images from the current chapter iteration using a thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
                #args = [img.get('src'), title, chapter_name, page_num]
                futures = [executor.submit(MangaNelo.download_img, img.get('src'), img.get('title')) for img in imgs_list]
                for future in futures:
                    result = future.result()
           
            # Update the progress bar after one chapter is downloaded 
            progress_bar.update(1)
            Clock.schedule_once(lambda *args: MangaNelo.trigger_call(tile, 1), -1)

        progress_bar.close()
        Clock.schedule_once(lambda *args: tile.reset_progressbar(), 1) 
        

    @staticmethod
    def download_img(img_url, title):
        with requests.Session() as s:          
            response = s.get(img_url, headers=MangaNelo.headers, stream=True)
            filename = f"{title} + {img_url.split('/')[-1]}"
            filename = re.sub("Vol\.\d*","",filename) # This regex will remove the word vol to sort them alphabetically
            filename = re.sub(r'[\\/*?:"<>|]',"",filename) # Sanitize filename for creation
            
            with open(filename, "wb") as f:
                #f.write(response.content)
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            
    #@mainthread
    @staticmethod
    def trigger_call(tile,val):
        tile.progressbar.value+= val


if __name__ == "__main__":    
    #x = MangaNelo("Dark age")
    #print(x.manga_choices)

    """
    url = "https://chap.manganelo.com/manga-hl88905"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, features="lxml")
    chapter_links = [{"imgs-link":link.get("href"), "chapter":link.text.strip()} for link in soup.select("a.chapter-name.text-nowrap")][::-1]
    #print(chapter_links)
    """
    headers = {
        "referer": "https://chap.manganelo.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
    }
    chapter_17 = "https://chap.manganelo.com/manga-hl88905/chapter-17"
    r = requests.get(chapter_17)
    soup_ = BeautifulSoup(r.content, features="lxml")
    imgs = soup_.select("div.container-chapter-reader img")

    
    for img in imgs:
        with requests.Session() as s:
            response = s.get(img.get("src"), headers=headers)
            filename = img.get("title") + img.get("src").split("/")[-1]
            filename = re.sub(r'[\\/*?:"<>|]',"",filename) # Sanitize filename for creation
            print(filename)

            with open(filename, "wb") as f:
                f.write(response.content)
        break
    