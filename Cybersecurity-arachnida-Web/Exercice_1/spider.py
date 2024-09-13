#!/usr/bin/env python3

import requests
from fake_useragent import UserAgent
import shutil
from sys import argv
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse

ua = UserAgent()
chrome_uas = ua.chrome
request_headers = {
    'user-agent': chrome_uas
}

def parse_arg(argv):
    recursively_len = None
    path = './data/'
    url = None

    for i in range(1, len(argv)):
        if argv[i] == '-r':
            recursively_len = 5
        elif argv[i] == '-l':
            if i + 1 < len(argv) and argv[i + 1].isdigit() and recursively_len:
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
        if not recursively_len:
            recursively_len = 1
    return recursively_len, path, url

def spider_url(recursively, url, path, urls=[]):
    print(f"{recursively} --> {url}")
    urls = spider_img(url, path, urls)
    try:
        response = requests.get(url, headers=request_headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = urljoin(url, link['href'])
            if href not in urls and urlparse(href).netloc == urlparse(url).netloc:
                urls.append(href)
                if recursively - 1 > 0:
                    spider_url(recursively - 1, href, path)
    except Exception as e:
        print(f"Error: {e} with URL: {url}")
    return urls

def spider_img(url, path, urls=[]):
    # try:
    if 1:
        os.makedirs(path, exist_ok=True)
        response = requests.get(url, headers=request_headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img', src=True) + soup.find_all('a', href=True)
        for img in images:
            if 'src' in img and img['src']:
                img_url = urljoin(url, img['src'])
            elif 'href' in img and img['href']:
                img_url = urljoin(url, img['href'])
            else:
                try:
                    img_url = urljoin(url, img['src'])
                except:
                    continue
            if img_url not in urls and img_url.split('.')[-1].lower() in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                urls.append(img_url)
                filename = os.path.join(path, img_url.split("/")[-1].split("?")[0])
                img_response = requests.get(img_url, stream=True)
                with open(filename, 'wb') as out_file:
                    shutil.copyfileobj(img_response.raw, out_file)
                del img_response
        return urls
    # except Exception as e:
    #     print(f"Error: {e} with URL: {url}")
    return urls

def main():
    recursively_len, path, url = parse_arg(argv)
    print(f"Maximum depth level: {recursively_len}\nPATH: {path}\nURL: {url}")
    t = spider_url(recursively_len, url, path)
    print("\n".join(t))

if __name__ == '__main__':
    main()
