from typing import List
import config
import os, sys
from urllib import parse
from bs4 import BeautifulSoup
from requests import Response


def get_response(link: str) -> Response:
    "calls link and returns byte response."
    resp = config.session.get(link)
    return resp


def get_links(resp, link: str) -> tuple:
    """get out all links in response, both in website links and out of website links"""
    local_links = []
    links = []
    bs = BeautifulSoup(resp.text, 'html.parser') # parsing file for info
    bs_a = bs.find_all('a')
    for a in bs_a: # iterating through <a> tags
        href = a['href']
        if href[0:4] != 'http': # checking if this is a path or a full url
            url_path = f'{link}{href}'
            local_links.append(url_path)
        else:
            url_path = href
            links.append(url_path)

    return (local_links, links)



# TODO: add save logic here https://stackoverflow.com/questions/31205497/how-to-download-a-full-webpage-with-a-python-script
# https://stackabuse.com/parsing-xml-with-beautifulsoup-in-python/

def parse_page(soup:BeautifulSoup, url:str, pagefolder:str, tag: str, inner:str='src') -> BeautifulSoup:
    """Get specified info out of pages and saves."""
    pagefolder = pagefolder
    if not os.path.exists(pagefolder):
        os.mkdir(pagefolder)
    
    pagefolder = pagefolder + f'/{tag}/'
    if not os.path.exists(pagefolder):
        os.mkdir(pagefolder)
    
    for res in soup.findAll(tag):
        try:
            filename = os.path.basename(res[inner])
            fileurl = parse.urljoin(url, res.get(inner))
            # rename to saved file
            # res[inner] may or may not exist
            filepath = os.path.join(pagefolder, filename)
            res[inner] = os.path.join(os.path.basename(pagefolder), filename)
            if not os.path.isfile(filepath): # was not downloaded
                with open(filepath, 'wb') as file:
                    filebin = config.session.get(fileurl)
                    file.write(filebin.content)
        except Exception as exc:
            print(exc, file=sys.stderr)
    return soup


def save_page(resp, foldername:str="", pagefilename:str='page', content:List[tuple]=[]) -> None:
    """Takes in a file and saves it to our data file; ~/misc/data"""
    url = resp.url
    soup = BeautifulSoup(resp.text, features='html.parser')
    pagefolder = f'{foldername}/{pagefilename}_files'
    for con in content:
        tag, inner = con
        soup = parse_page(soup, url, pagefolder, tag, inner)

    url = url.replace('/', '').replace(':', '').replace('https', '').replace('http', '')
    pagefolder = pagefolder + "/pages/"
    if not os.path.exists(pagefolder):
        os.mkdir(pagefolder)

    filepath = os.path.join(pagefolder, url)
    with open(filepath+'.html', 'w') as file:
        file.write(soup.prettify())
    return

