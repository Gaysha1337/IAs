import requests, os
from bs4 import BeautifulSoup
from terminaltables import AsciiTable

# Util func
def manganelo_validate_query(query=None):
    """ Returns False if query is none or no results were found"""
    if query == None:
        return False
    else:
        request_query_html = make_request(query)
        soup = BeautifulSoup(request_query_html[0],"html.parser")

        # Checks to see if the user's manga input was found
        query = request_query_html[1]
        query_search_results = soup.find("div",attrs={"class":"panel-search-story"})

        # False if Nothing found; True is a query was found
        if query_search_results == None:
            return False
            #raise ValueError(f"{query} was not found while searching")
        else:
            return True
        

def make_request(query=None):
    if query == None or query == "":
        query = input("Type a manga title (can be a keyword): ")
    
    #query = input("Type a manga title (can be a keyword): ")

    query_url = "https://m.manganelo.com/search/story/{}".format(query.strip().replace(" ","_"))
    request_query = requests.get(query_url)

    if request_query.status_code != 200:
        raise ConnectionError(f"Error code: {request_query.status_code}. The app can't connect to the site.")
    request_query_html = requests.get(query_url).content
    return (request_query_html,query)

def process_html(html, query):
    request_query_html = make_request(query)
    soup = BeautifulSoup(request_query_html[0],"html.parser")

    # Checks to see if the user's manga input was found
    query = request_query_html[1]
    query_search_results = soup.find("div",attrs={"class":"panel-search-story"})

    if query_search_results == None:
        raise ValueError(f"{query} was not found while searching")

    query_div_items = [{"q_name":i.find("a").text,"q_link":i.find("a").get("href")} for i in soup.find("div",attrs={"class":"panel-search-story"}).findAll("h3")]

    manga_links = [q_dict.get("q_link") for q_dict in query_div_items] 
    manga_choices = [q_dict.get("q_name").replace("\n","") for q_dict in query_div_items] # Manga titles

    return (manga_links, manga_choices)

manga_links, manga_choices = process_html(*make_request())

def create_manga_choice_table(manga_choices):
    data = []
    choice_number = 0
    for choice in manga_choices:
        choice_number += 1
        data.append(['Manga Name: ' + choice, 'Manga Number: ' + str(choice_number)])
    table = AsciiTable(data)
    table.inner_heading_row_border = False
    table.title = "Manga Choices: "
    print(table.table)
    return int(input("\nDear User, please type in the number that corresponds to the manga that you wish to download: ").strip())

user_number_choice = create_manga_choice_table(manga_choices)
print(manga_links[user_number_choice - 1]) # prints the url of the user's chosen manga name
manga_input = manga_choices[user_number_choice - 1]


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

url = manga_links[user_number_choice - 1]

def write_meta_data_file():
    meta_data_li_tags = soup.find("ul",attrs={"class":"manga-info-text"}).findChildren("li")
    summary_div = soup.find("div",attrs={"id":"noidungm"})
    split_summary = summary_div.text.strip().split()[1::]
    formatted_summary = "\n"    
    for word in split_summary:
        if "." in word or "," in word or word == split_summary[1]:
            word+="\n"
        formatted_summary += word + " "
    meta_data_list = [tag.text.strip() for tag in meta_data_li_tags]
    for datum in meta_data_list:
        meta_data_list.pop(4)
        meta_data_list.pop(-1)
    meta_data_list[1] = meta_data_list[1].replace("\n","")
    with open("info.txt","w",encoding='utf-8') as f:
        f.write("\n".join(meta_data_list))
        f.write(formatted_summary)

chapter_list_html = requests.get(url).content

# HTML RELATED
soup = BeautifulSoup(chapter_list_html,"html.parser")
chapter_divs = soup.find_all("div",attrs={"class":"row-content-chapter"})

chapter_divs = [a.get("href") for a in soup.select(".row-content-chapter li.a-h > a")]

# CHAPTER RELATED

chapter_links, chapter_names = [], []
for a in soup.select(".row-content-chapter li.a-h > a")[::-1]:
    chapter_links.append(a.get("href"))
    chapter_names.append(a.get("title"))

#write_meta_data_file()

def get_chapter_dicts_list():
    chapter_dicts_list = []
    for index, link in enumerate(chapter_links):
        # HTTP request headers
        headers = {
            "Referer": link,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
            "sec-fetch-dest": "image",
            "sec-fetch-mode": "no-cors",
            "sec-fetch-site": "cross-site"
        }   
        r = requests.get(link, headers=headers)
        current_chapter_soup = BeautifulSoup(r.content,"html.parser")
        
        img_holder_div = current_chapter_soup.find("div",attrs={"class":"container-chapter-reader"})
        img_links = [link.get("src") for link in img_holder_div.find_all("img")]

        #print(chapter_names[index], img_links)
        
        current_chapter_number = chapter_links.index(link) + 1
        print("------------------------- Chapter Link Appended: {} ----------------------------".format(current_chapter_number))
        chapter_info = {"chapter_number":current_chapter_number,"chapter_name":chapter_names[index],"img_links":img_links}
        chapter_dicts_list.append(chapter_info)
    return chapter_dicts_list

chapter_dics = get_chapter_dicts_list()
print(chapter_dics)

def get_downloader_data():
    return manga_input, get_chapter_dicts_list()    


"""  
for img_dict in get_chapter_dicts_list():
    img_chapter = img_dict.get("chapter_number")
    chapter_name = img_dict.get("chapter_name")
    current_chapter_dir = os.path.join(current_manga_dir,str(chapter_name).replace(":"," - "))

    for link in img_dict.get("img_links"):
        current_page_number = img_dict.get("img_links").index(link) + 1
        
        if not os.path.isdir(current_chapter_dir):
            os.mkdir(current_chapter_dir)
        os.chdir(current_chapter_dir)

        img_request = requests.get(link)
        filename = manga_input.capitalize() + " " + str(current_page_number) + ".jpg"

        with open(filename, "wb") as f:
            f.write(img_request.content)
    print("------------- Dowloaded Chapter {}; there are {} pages in this chapter ----------".format(img_chapter,len(img_dict.get("img_links"))))


print("All chapters downloaded")
"""