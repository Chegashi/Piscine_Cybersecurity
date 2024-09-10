#!/usr/bin/env python3

from sys import argv
import httplib2
from bs4 import BeautifulSoup, SoupStrainer
import urllib.request
import os
from urllib.parse import urljoin, urlparse

def parse_arg(argv):
    recursively_len = 1
    path = './'
    url = None

    for i in range(1, len(argv)):
        if argv[i] == '-r':
            recursively_len = 5
        elif argv[i] == '-l':
            if i + 1 < len(argv) and argv[i + 1].isdigit():
                recursively_len = int(argv[i + 1])
                i += 1
            else:
                print("Invalid argument for -l")
                exit(1)
        elif argv[i] == '-p':
            if i + 1 < len(argv):
                path = argv[i + 1]
                i += 1
            else:
                print("Invalid argument for -p")
                exit(1)
        elif i == (len(argv) - 1):
            if argv[i].startswith('http://') or argv[i].startswith('https://'):
                url = argv[i]
            else:
                print("Invalid URL")
                exit(1)
    if not url:
        print("Error: URL is missing")
        exit(1)
    return recursively_len, path, url

def spider_url(recursively, url, path, urls=[]):
    print(f"{recursively} --> {url}")
    try:
        urls = spider_img(url, path, urls)
        http = httplib2.Http()
        status, response = http.request(url)
        for link in BeautifulSoup(response, 'html.parser', parse_only=SoupStrainer('a')):
            if link.has_attr('href'):
                href = urljoin(url, link['href'])
                if href not in urls and urlparse(href).netloc == urlparse(url).netloc:
                    urls.append(href)
                    if recursively - 1 > 0:
                        spider_url(recursively - 1, href, path)
    except Exception as e:
        print(f"Error: {e} with URL: {url}")
    return urls

def spider_img(url, path, urls=[]):
    try:
        os.makedirs(path, exist_ok=True)
        http = httplib2.Http()
        status, response = http.request(url)
        for img in BeautifulSoup(response, 'html.parser', parse_only=SoupStrainer('img')):

            if img.has_attr('src'):
                href = urljoin(url, img['src'])
                if href not in urls and href.split('.')[-1] in [' jpg', 'jpeg','png', 'gif', 'bmp']:
                    urls.append(href)
                    filename = os.path.join(path, href.split("/")[-1].split("?")[0])
                    urllib.request.urlretrieve(href, filename)
        return urls
    except Exception as e:
        print(f"Error: {e} with URL: {url}")
    return urls

def main():
    recursively_len, path, url = parse_arg(argv)
    print(f"Maximum depth level: {recursively_len}\nPATH: {path}\nURL: {url}")
    t = spider_url(recursively_len, url, path)
    print("\n".join(t))

if __name__ == '__main__':
    main()
