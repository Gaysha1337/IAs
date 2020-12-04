from kivymd.app import MDApp
from kivy.clock import Clock, mainthread

import requests, os, re
from bs4 import BeautifulSoup
from tqdm import tqdm
import concurrent.futures


if __name__ != "__main__":
    from utils import create_manga_dirs, download_cover_img

# Japanese Manga Downloader
class RawDevArt:
    def __init__(self, query=None):
        # Need to find a way to get manga from all pages
        # https://rawdevart.com/search/?page=2&title=the
        self.query_url = f"https://rawdevart.com/search/?title={query.strip().replace(' ','+')}"
        self.request_error_code = None
        self.popup_msg = None
        self.hasErrorOccured = False
        self.master = MDApp.get_running_app()

        try: 
            request_obj = requests.get(self.query_url)
            self.request_error_code = request_obj.status_code
            soup = BeautifulSoup(request_obj.content,"html.parser")
            manga_divs = soup.select("div.row.mb-3 > div.col-6.col-md-4.col-lg-3.col-xl-2.px-1.mb-2.lister-layout")
            if manga_divs == None:
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


    # Root is the running app
    # Links is a tuple contain: A link to the cover image and the download link        
    @staticmethod
    def download_manga(root,tile,title,links, *args):
        title = re.sub(r'[\\/*?:"<>|]',"",title) # Sanitize title name for dir/file creation
        manga_download_link, cover_img_link = links
        
        #create_manga_dirs(title) # After being called, the user should be in the dir for that manga
                
        download_cover_img(cover_img_link, cover_img_link.split("/")[-1])
        soup = BeautifulSoup(requests.get(manga_download_link).content, features="lxml")

        # Get the chapter images and the title of the chapter
        chapter_links = [{"chapter-imgs-link":"https://rawdevart.com" + elem.get("href"), "chapter":elem.get("title")} for elem in soup.select("div.list-group-item a", text=True)][::-1]

        progress_bar = tqdm(chapter_links, total=len(chapter_links))
        tile.progressbar.max = len(chapter_links)
        
        for index, link_dict in enumerate(chapter_links):
            chapter, img_url = link_dict.get("chapter"), link_dict.get("chapter-imgs-link") 
            chapter = re.sub(r'[\\/*?:"<>|]',"",chapter) # Sanitize chapter name for dir/file creation
            soup_ = BeautifulSoup(requests.get(img_url).content, features="lxml")
            # TODO: Will this work on android ?
            current_chapter_dir = os.path.join(root.japanese_manga_dir,title,chapter)
            #print(os.getcwd(), "cwd")
            # Make the directories for each chapter
            if not os.path.isdir(current_chapter_dir):
                os.mkdir(current_chapter_dir)
            os.chdir(current_chapter_dir)

            imgs_list = soup_.select("div.mb-3 img.img-fluid.not-lazy")

            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
                #args = [img.get('src'), title, chapter_name, page_num]
                futures = [executor.submit(RawDevArt.download_img, img_url=img.get('data-src'), title=title, chapter_name=chapter) for page_num, img in enumerate(imgs_list)]
                for future in futures:
                    result = future.result()
            """        
            for img in imgs_list:
                with requests.Session() as s:          
                    response = s.get(img.get('data-src'), stream=True)
                    filename = f"{title} {chapter} - {img.get('data-src').split('/')[-1]}"
                    
                    total_size_in_bytes, block_size= int(response.headers.get('content-length', 0)), 1024 #1 Kibibyte
                    #progress_bar = tqdm(desc=filename, total=total_size_in_bytes, unit='B', unit_scale=True, unit_divisor=1024)
                    RawDevArt.download_img(img_url=img.get('data-src'), title=title, chapter_name=chapter)
                    with open(filename, "wb") as f:
                        for chunk in response.iter_content(block_size):
                            f.write(chunk)
            """
            progress_bar.update(1)
            Clock.schedule_once(lambda *args: RawDevArt.trigger_call(tile, 1), -1)
        
        progress_bar.close()

    @staticmethod
    def trigger_call(tile,val):
        tile.progressbar.value+= val

    @staticmethod
    def download_img(img_url, title, chapter_name):
        with requests.Session() as s:          
            response = s.get(img_url)
            filename = f"{title} {chapter_name} - {img_url.split('/')[-1]}"
            filename = re.sub(r'[\\/*?:"<>|]',"",filename) # Sanitize filename for creation
                        
            with open(filename, "wb") as f:
                f.write(response.content)

def trash():
    """
    #query = input("Type a manga title (can be a keyword): ")

    #query_url = "https://rawdevart.com/search/?title={}".format(query.strip().replace(" ","+"))

    query_url = "https://rawdevart.com/search/?title=kage+no"
    request_query_html = requests.get(query_url).content

    soup = BeautifulSoup(request_query_html,"html.parser")

    #print(soup.find("div",attrs={"class":".row mb-3"}))

    manga_divs = soup.select("div.row.mb-3 > div.col-6.col-md-4.col-lg-3.col-xl-2.px-1.mb-2.lister-layout")

    query_info = []#[{"title":div.select_one("a.head").text.replace("\n",""), "url":"https://rawdevart.com" + div.select_one("a.head").get("href"), "cover_img":"https://rawdevart.com" + div.select_one("img.img-fluid").get("src")} for div in manga_divs]

    for div in manga_divs:
        q_cover_img = div.select_one("img.img-fluid").get("src")
        q_url = div.select_one("a.head").get("href")
        q_title = div.select_one("a.head").text.replace("\n","")

        query_info.append({"title":q_title, "url":"https://rawdevart.com" +q_url, "cover_img":"https://rawdevart.com" + q_cover_img})

    for i in query_info:
        print(i.get("url"))
        
        chapter_urls = None
    """

if __name__ == "__main__":

    links = ('https://rawdevart.com/comic/kage-no-jitsuryokusha-ni-naritakute-shadow-gaiden/', 'https://rawdevart.com/media/comic/kage-no-jitsuryokusha-ni-naritakute-shadow-gaiden/covers/Kage_no_Jitsuryokusha_ni_Naritakute_Shadow_Gaiden_1.jpg.320x320_q85.jpg')
    #x = RawDevArt("Kage no")
    title, download_link, cover_link = "Kage no Jitsuryokusha ni Naritakute", *links
    print(download_link)
    #x.download_manga(None, title, links)

    r = requests.get(download_link)
    
    base = "https://rawdevart.com"
    x = requests.utils.urlparse(download_link)
    soup = BeautifulSoup(r.content,features="lxml")

    chapter_links = ["https://rawdevart.com" + elem.get("href") for elem in soup.select("div.list-group-item a", text=True)]
    print(chapter_links)
        