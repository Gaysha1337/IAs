import requests, csv
from bs4 import BeautifulSoup
import pandas as pd

url = "https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Japan"

soup = BeautifulSoup(requests.get(url).content, "lxml")

tbody = soup.select_one("#mw-content-text > div > div.barbox.tright > div > table").find_all("tr")

f = open("IA Data.csv","w", newline="", encoding="utf-8")
writer = csv.writer(f, delimiter=";")

for row in tbody[1:-1]:
    cols = row.findChildren(recursive=False)
    del cols[1] # Gets rid of the empty col
    cols = [elem.text.strip() for elem in cols]    
    writer.writerow(cols)
    #print(cols)


