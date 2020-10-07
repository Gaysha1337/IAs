import requests

url = "https://s8.mkklcdnv8.com/mangakakalot/s2/ss923461/chapter_15/2.jpg"

headers = {
    "Referer": "https://chap.manganelo.com/manga-iv123141/chapter-15",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
}

r = requests.get(url, headers=headers)

if r.status_code == 200:
    with open("finna_del_2.jpg", 'wb') as f:
        f.write(r.content)
else:
    print("ERROR")