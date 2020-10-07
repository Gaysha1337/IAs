import requests
from bs4 import BeautifulSoup
from terminaltables import AsciiTable

class RawDevArt:
    def __init__(self, query=None):
        #self.query = query
        self.query_url = "https://rawdevart.com/search/?title={}".format(query.strip().replace(" ","+"))
        self.request_error_code = None
        self.popup_msg = None
        self.hasErrorOccured = False
        print(self.query_url)
        try: 
            request_obj = requests.get(self.query_url)
            self.request_error_code = request_obj.status_code
            soup = BeautifulSoup(request_obj.content,"html.parser")
            manga_divs = soup.select("div.row.mb-3 > div.col-6.col-md-4.col-lg-3.col-xl-2.px-1.mb-2.lister-layout")
            if manga_divs == None:
                self.hasErrorOccured = True
                self.popup_msg = f"No manga called {query} was found while searching Raw Dev Art"
                print(self.popup_msg)
                manga_divs, self.manga_data = [], {}

            else:                 
                self.manga_choices = [div.select_one("a.head").text.replace("\n","") for div in manga_divs]
                self.manga_links = ["https://rawdevart.com" + div.select_one("a.head").get("href") for div in manga_divs]
                self.manga_covers = ["https://rawdevart.com" + div.select_one("img.img-fluid").get("src") for div in manga_divs]
                self.manga_data = dict(zip(self.manga_choices, zip(self.manga_links, self.manga_covers)))
                #print(self.manga_data)
                print(self.manga_covers)
                
        except:
            self.popup_msg = "Error: The app can't connect to the site."
            self.hasErrorOccured = True
            print("Error: can't connect to Raw Dev Art")

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
    x = RawDevArt("Kage no")