from kivymd.app import MDApp
from kivy.clock import Clock, mainthread

import requests, os, re
from bs4 import BeautifulSoup
from tqdm import tqdm
from functools import partial
import concurrent.futures


if __name__ != "__main__":
    from utils import create_manga_dirs, download_cover_img

# Japanese Manga Downloader
class SenManga:
    def __init__(self, query=None):

        # Need to find a way to get manga from all pages
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
        #create_manga_dirs(title) # After being called, the user should be in the dir for that manga
                
        #download_cover_img(cover_img_link, cover_img_link.split("/")[-1])
        #headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"}
        r = requests.get(manga_download_link, headers=SenManga.headers)
        soup = BeautifulSoup(r.content, features="lxml")
        chapter_divs = soup.select(".list")[1]

        chapter_links = [{"link":a.get("href"),"chapter":a.text.strip()} for a in chapter_divs.select(".list .group .element .title a")][::-1]
        #chapter_links = [{"img-link":"https://rawdevart.com" + elem.get("href"), "chapter":elem.get("title")} for elem in soup.select("div.list-group-item a", text=True)][::-1]

        progress_bar = tqdm(chapter_links, total=len(chapter_links))
        tile.progressbar.max = len(chapter_links)

        for index, link_dict in enumerate(chapter_links):
            chapter, link = link_dict.get("chapter"), link_dict.get("link")
            chapter = re.sub(r'[\\/*?:"<>|]',"",chapter) # Sanitize chapter name for dir/file creation

            r_ = requests.get(link, headers=headers)
            soup_ = BeautifulSoup(r_.content, features="lxml")
            total_imgs_num = len([i.get("value") for i in soup_.select_one(".page-link select").find_all("option")])

            # TODO: Will this work on android ?
            current_chapter_dir = os.path.join(root.japanese_manga_dir,title,chapter)
            
            if not os.path.isdir(current_chapter_dir):
                os.mkdir(current_chapter_dir)
            os.chdir(current_chapter_dir)
            imgs_list = [link.replace("raw.senmanga.com", "delivery.senmanga.com/viewer") + "/" + str(img_num) for img_num in range(1,total_imgs_num + 1) ]

            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
                #args = [img.get('src'), title, chapter_name, page_num]
                futures = [executor.submit(SenManga.download_img, img_url=img, title=title, chapter_name=chapter) for page_num, img in enumerate(imgs_list)]
                for future in futures:
                    result = future.result()
            """
            for img in imgs_list:
                with requests.Session() as s:
                    response = s.get(img, headers=headers)
                    filename = title + chapter + img.split("/")[-1] + ".jpg"
                    with open(filename, "wb") as f:
                        f.write(response.content)
            """    
            # TODO: Is the right way to update the progress bar
            progress_bar.update(1)
            Clock.schedule_once(lambda args: SenManga.trigger_call(tile, 1), -1)

        progress_bar.close()    

    @staticmethod
    def download_img(img_url, title, chapter_name):
        with requests.Session() as s:          
            response = s.get(img_url, headers=SenManga.headers)
            filename = f"{title} {chapter_name} - {img_url.split('/')[-1]}.jpg"
            filename = re.sub(r'[\\/*?:"<>|]',"",filename) # Sanitize filename for creation
                        
            with open(filename, "wb") as f:
                f.write(response.content)
    
    #@mainthread
    @staticmethod
    def trigger_call(tile,val):
        tile.progressbar.value+= val

if __name__ == "__main__":
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"}

    def get_manga_from_input():
        query = "mirai"
        query_url = f"https://raw.senmanga.com/search?s={query.replace(' ', '+')}"
        print(query_url)

        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"}
        r = requests.get(query_url, headers=headers)

        soup = BeautifulSoup(r.content, features="lxml")
        manga_divs = soup.select(".series")
        manga_choices = [div.find("p").text.strip() for div in manga_divs]
        manga_links = [div.find("a").get("href") for div in manga_divs]
        manga_covers = [div.find("img").get("src") for div in manga_divs]
        manga_data = dict(zip(manga_choices, zip(manga_links, manga_covers)))
        print(manga_data)

    def main(error_link=True):
        url_nc = "https://raw.senmanga.com/2-Dome-no-Koi-wa-Usotsuki"
        url_hc = "https://raw.senmanga.com/Black_Bird"

        url = url_nc if error_link == True else url_hc

        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"}
        r = requests.get(url, headers=headers)

        soup = BeautifulSoup(r.content, features="lxml")
        chapter_divs = soup.select(".list")[1]
        chapter_list = [{"link":a.get("href"),"chapter":a.text.strip()} for a in chapter_divs.select(".list .group .element .title a")][::-1]
        
        for chapter_dict in chapter_list:
            #print(chapter_dict, type(chapter_dict))
            
            link, name = chapter_dict.get("link"), chapter_dict.get("chapter")
            r = requests.get(link, headers=headers)
            soup = BeautifulSoup(r.content,features="lxml")
            total_imgs_num = len([i.get("value") for i in soup.select_one(".page-link select").find_all("option")])
            print(f"Made dir: Black_Bird/{name} in root")
            
            img_list = [link.replace("raw.senmanga.com", "delivery.senmanga.com/viewer") + "/" + str(img_num) for img_num in range(1,total_imgs_num + 1) ]
            for index, img in enumerate(img_list):
                print(img)
                r_ = requests.get(img, headers=headers)
                filename = title + name + img.split("/")[-1] + ".jpg"
                with open(filename, "wb") as f:
                    f.write(r_.content)
                #soup_ = BeautifulSoup(r.content, features="lxml")
                #img_link = soup.find_all("img")
                #img_link = soup_.select_one("img#picture").get("src")
                #print(img_link)
                
            break
            
    main(False)
    #get_manga_from_input()