#!/usr/bin/env python3

from sys import argv
import httplib2
from bs4 import BeautifulSoup, SoupStrainer


# class spider_parser:
#     def __init__(self, argv):
#         pass
        
def parse_arg(argv):
    recursively_len = 1
    path = './'
    url = None

    for i in range(1, len(argv)):
        if argv[i] == '-r':
            recursively_len = 5
        elif argv[i] == '-l':
            # print(i + 1 < len(argv),  argv[i + 1].isdigit())
            if i + 1 < len(argv) and argv[i + 1].isdigit():
                recursively_len = int(argv[i + 1])
                i += 1
            else:
                print("Invalid argument for -l")
                exit(1)
        elif argv[i] == '-p':
            if i + 1 < len(argv):
                path = argv[i + 1]
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

def spider(recursively : int, url: str, path:str, urls=[]):
    # for i in  range (recursively, 0, -1):
    print(f"{recursively} --> {url}")
    try:
        http = httplib2.Http()
        status, response = http.request(url)
        for link in BeautifulSoup(response, 'html.parser', parse_only=SoupStrainer('a')):
            if link.has_attr('href'):
                href = link['href']
                if href.startswith('/') or href.startswith('#'):
                    href = url + href
                urls.append(href)
                if recursively - 1 > 0:
                    spider(recursively -1, href, path)
    except Exception as e:
        print(f"Error: {e} with {href} ")
    return urls
        
                
def main():
    pass

if __name__ == '__main__':
    recursively_len, path, url = parse_arg(argv)
    print(f"maximum depth level : {recursively_len}\nPATH: {path}\n URL: {url}")
    t = spider(recursively_len, url, path)
    print("\n".join(t))


