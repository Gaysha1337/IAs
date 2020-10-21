
from bs4 import BeautifulSoup

html = '''
<p class="labels">
  <span>Item1</span>
  <span>Item2</span>
  <time class="time">
    <span>I dont want to get this span</span>
  </time>
</p>'''

soup = BeautifulSoup(html, features="lxml")

labels = soup.find("p",class_="labels")
x = labels.find_all("span", recursive=False)

print(x)