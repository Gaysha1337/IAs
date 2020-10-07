"""
General downloader class
- Params:
    - A list with dicts for each chapter (see below)
    - A dict with links to all the pages for each chapter:
        - Name of the chapter (if any, otherwise use numbers) as the first elem
        - links with page numbers
        - 
"""

from manga_nelo import get_downloader_data

class MangaDownloader:
    def __init__(self,title,chapter_dicts: list):
        self.title = title
        self.chapter_dicts = chapter_dicts

        print(self.title, self.chapter_dicts)



if __name__ == "__main__":
    x = MangaDownloader(*get_downloader_data())
