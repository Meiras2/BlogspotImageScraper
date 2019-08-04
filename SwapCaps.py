from bs4 import BeautifulSoup
import requests
import json
import os
import re
import threading
import urllib.request as req
from urllib.parse import urlparse

class scraper:
    ''' Scraper class to scrap all pictures from different blogs '''

    def __init__(self):
        # Read lines from json file (TODO: Pass filename from commandline)
        with open('sites.json') as file:
            data = json.load(file)
            self.sites = data["sites"]

    def savePicture(self, folder, url):
        a = urlparse(url)
        # Give a proper name (TODO: Do it properly with regular expressions)
        name = os.path.basename(a.path)
        name = name.replace("%2B", " ")
        name = name.replace("%2527", "'")
        name = name.replace("%2523", "#")
        name = name.replace("%27", "'")
        name = name.replace("+", " ")
        # Save it
        req.urlretrieve(url, folder + "/" + name)

    def createDirectory(self, name):
        # Current path + new folder name
        path = os.path.dirname(os.path.abspath(__file__)) + '/' + name
        # If it doesn't exist it will be created
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            print("Folder already exists")
        return path

    def checkHTTP(self, url):
        p = re.compile("^http(s)?:")
        return re.search(p, url) != None

    def checkExt(self, url):
        p = re.compile("[a-zA-Z]+$")
        if re.search(p, url):
            return re.search(p, url).group(0) != "html"
        else:
            return False

    def scrapPage(self, url, folder):
        r = requests.get(url)
        r_html = r.text

        soup = BeautifulSoup(r_html, "html.parser")

        for post in soup.find_all("div", {"class": "post hentry uncustomized-post-template"}):
            # Get picture links
            img_list = []
            for separators in post.find_all("div", {"class": "separator"}):
                for img_link in separators.find_all("a"):
                    if self.checkExt(img_link['href']):
                        if not self.checkHTTP(img_link['href']):
                            img_list.append("https:" + img_link['href'])
                        else:
                            img_list.append(img_link['href'])
            print(img_list)
            for img in img_list:
                self.savePicture(folder, img)
        next_page = soup.find_all("a", {"class": "blog-pager-older-link"})
        if next_page:
            self.scrapPage(next_page[0]['href'], folder)
        else:
            next_page = False
        return next_page

    def scrapSites(self):
        for site in self.sites:
            # Create a folder named after the site, if it doesn't exist
            path = self.createDirectory(site["name"])
            self.scrapPage(site["url"], path)

sc = scraper()
sc.scrapSites()