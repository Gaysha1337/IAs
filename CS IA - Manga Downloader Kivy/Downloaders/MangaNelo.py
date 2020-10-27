from cfscrape import user_agents
import requests, os, re
from collections import OrderedDict
from tqdm import tqdm
from bs4 import BeautifulSoup
from requests import exceptions
from kivy.clock import Clock

# delete this line when publishing
if __name__ != "__main__":
    from utils import create_manga_dirs, download_cover_img, download_manga

# This downloader is for English Manga
class MangaNelo():

    """
    download_link --> str: 
    """
    def __init__(self,query=None ):
        #self.query = query # User input
        self.query = query
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
                print("printing manga data in manganelo class",self.manga_data)
        except:
            self.popup_msg = "Error: The app can't connect to the site. Check internet connection; Site may be blocked"
            self.hasErrorOccured = True
            print("Error: can't connect to Manganelo")

    @staticmethod
    def download_manga(root, tile, title, links):
        title = re.sub(r'[\\/*?:"<>|]',"",title) # Sanitize title name for dir/file creation
        manga_download_link, cover_img_link = links        
        download_cover_img(cover_img_link, cover_img_link.split("/")[-1])

        headers = {
            "referer": "https://chap.manganelo.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        }

        soup = BeautifulSoup(requests.get(manga_download_link).content, features="lxml")
        #print("manga download link: ",manga_download_link, "cover img l", cover_img_link)
        chapter_links = [{"imgs-link":link.get("href"), "chapter":link.text.strip()} for link in soup.select("a.chapter-name.text-nowrap")][::-1]
        progress_bar = tqdm(chapter_links, total=len(chapter_links))
        tile.progressbar.max = len(chapter_links)
        for index, link_dict in enumerate(chapter_links):
            chapter, link = link_dict.get("chapter"), link_dict.get("imgs-link")
            chapter = re.sub(r'[\\/*?:"<>|]',"",chapter) # Sanitize chapter name for dir/file creation

            r_ = requests.get(link, headers=headers)
            soup_ = BeautifulSoup(r_.content, features="lxml")
            current_chapter_dir = os.path.join(root.english_manga_dir,title,chapter)
            #print(os.getcwd(), "cwd")
            if not os.path.isdir(current_chapter_dir):
                os.mkdir(current_chapter_dir)
            os.chdir(current_chapter_dir)

            for img in soup_.select("div.container-chapter-reader img"):
                # The request session is needed to bypass Cloudfare by setting correct cookies
                with requests.Session() as s:
                    response = s.get(img.get("src"), headers=headers)
                    filename = img.get("title") + img.get("src").split("/")[-1]
                    filename = re.sub(r'[\\/*?:"<>|]',"",filename) # Sanitize filename for creation

                    with open(filename, "wb") as f:
                        f.write(response.content)
            
            progress_bar.update(1)
            Clock.schedule_once(lambda args: MangaNelo.trigger_call(tile, 1), -1)

        progress_bar.close()

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
    