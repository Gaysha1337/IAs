import requests, os
from bs4 import BeautifulSoup
from requests import exceptions
from terminaltables import AsciiTable

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

        print(self.query_url)

        try: 
            request_obj = requests.get(self.query_url)
            self.request_error_code = request_obj.status_code
            soup = BeautifulSoup(request_obj.content,"html.parser")

            # Checks to see if the user's manga input was found
            query_search_results = soup.find("div",attrs={"class":"panel-search-story"})

            if query_search_results == None:
                self.hasErrorOccured = True
                self.popup_msg = f"No manga called {query} was found while searching Manganelo"
                print(self.popup_msg)
                query_search_results, self.manga_data = [], {}
            else:
                
                query_div_items = [{"q_name":i.find("a").text,"q_link":i.find("a").get("href")} for i in query_search_results.findAll("h3")]
                for index, img in enumerate(query_search_results.find_all("img")):
                    query_div_items[index].update({"q_cover_img":img.get("src")})

                self.manga_links = [i.find("a").get("href") for i in query_search_results.findAll("h3")] 
                self.manga_choices = [i.find("a").text.replace("\n","") for i in query_search_results.findAll("h3")] # Manga titles
                self.manga_cover_imgs = [i.get("src") for i in query_search_results.find_all("img")]
                self.manga_data = dict(zip(self.manga_choices, zip(self.manga_links, self.manga_cover_imgs)))
                #print(self.manga_data)

                
        except:
            self.popup_msg = "Error: The app can't connect to the site."
            self.hasErrorOccured = True
            #request_obj = UrlRequest(self.query_url, on_failure=lambda x: print("error"))
            print("Error: can't connect to Manganelo")

            
        def get_user_input(self,query):
            pass

    @staticmethod
    def download_manga(manga_title, download_link):
        print("In download method: Title", manga_title, "link:",download_link)

    @staticmethod
    def create_manga_dirs():
        manga_root_dir = os.path.join(os.path.expanduser("~/Desktop"),"Manga")
        current_manga_dir = os.path.join(manga_root_dir,manga_input)

        # Makes a "root" for all downloaded mangas; Makes a folder that keeps all ur downloaded manga
        if not os.path.isdir(manga_root_dir):
            os.mkdir(manga_root_dir)
            print("Manga root made; Current directory {}".format(manga_root_dir))
        else:
            print("You already have a manga root")

        if not os.path.isdir(current_manga_dir):
            os.mkdir(current_manga_dir)
            print("A folder for {} has been made in the manga root directory".format(manga_input.capitalize()))
        else:
            print("You already have a folder for {}, if you would like to redownload this manga, please delete its folder".format(manga_input.capitalize()))
        os.chdir(current_manga_dir)


if __name__ == "__main__":    
    x = MangaNelo("Dark age")
    #print(x.manga_choices)