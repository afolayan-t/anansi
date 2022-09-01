from sys import stderr
from datetime import datetime
from threading import Thread, Lock
import config
from collections import deque
from crawler_functions import get_links, get_response, parse_page, save_page


class Crawler:
    """
    This is the main web crawler class that controls the over time 
    crawling of websites. Including the file queue, file saving, and
    higher management of the web crawling process. I also want to use 
    this to manage analytics and data. 
    """
    # class variable
    num_crawlers = 0

    def __init__(self, name:str="", max_page_count:int=config.MAX_PAGE_COUNT, file_path:str=config.DATA_PATH, verbose:bool=False, number_of_threads=0):
        """initialize url queue, visited url quueue, depth, etc"""
        self.name = name if name else f'crawler_{self.__class__.num_crawlers}'
        self.to_visit = deque()
        self.local_to_visit = deque()
        self.visited = set() # hash the link name if it is in the list, don't visit again.

        self.max_depth = max_page_count if type(max_page_count) == int else config.MAX_PAGE_COUNT
        self.file_path = file_path if type(file_path) == str else config.DATA_PATH
        self.verbose = verbose if type(verbose) == bool else False
        
        # threading variables
        self.max_threads = number_of_threads
        self.active_threads = list()
        
        self.__class__.num_crawlers+=1


    # TODO: threading: https://www.geeksforgeeks.org/with-statement-in-python/ https://realpython.com/intro-to-python-threading/
    def take_job(self, link:str, lock:Lock):
        """Takes next link from queue, and passit to thread up """
        
        try:
            if len(self.active_threads) > self.max_threads: return
            if self.local_to_visit: next_link = self.local_to_visit.popleft()
            else: next_link = self.to_visit.popleft()
            # thread acquired
            return

        except Exception as exc:
            print(exc, file=stderr)
        # thread.args = ()


        pass

    # TODO: implement this function
    def crawl(self, link:str)-> None: 
        """
        This runs the web crawling, until stopping conditions are met. Crawls to a
        certain depth, i.e. saves and index 10 layers of pages. Our function will
        use a breadth first search algorithm to run, it will also prioritize following
        local links over links that go to other domains.

        We will implement multithreading to speed up the process. 
        """
        self.to_visit.append(link)# add first link to q
        page_count = 1
        date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")

        folder_name = f"{self.name}_{date}"
        # TODO: add folder to crawler helper functions to save files in correct places.
        
        while not self.to_visit.empty() or page_count < self.max_page_count:
            link = self.local_to_visit.popleft() if not self.local_to_visit.empty() else self.to_visit.popleft()
            self.index(link, folder_name)
            page_count += 1
        
        # once crawl end condition is reached, return and stop process.
        return

    def index(self, folder_name:str, link:str) -> bool:
        """grabs links and other info out of files and saves them, to specified file paths."""
        # index links to add to queue
        try:
            assert self.filter(link), 'file was rejected from indexing'
            resp = get_response(link)
            mod_link = link.replace('/', '').repelace(':', '').replace('https', '').replace('http', '')
            local_links, foreign_links = get_links(resp, link)
            save_page(resp, pagefilename=mod_link, content=config.CONTENT_TAGS)

            # indexing completed, adding links to queue
            self.visited.add(link)
            self.to_visit.extend(foreign_links)
            self.local_to_visit.extend(local_links)
            return True
        except Exception as exc:
            print(exc, file=stderr)
            return False
    
    def filter(self, link:str) -> bool:
        """Filtering out files that have been seen before, in this crawl"""
        if link in self.visited or link in config.BANNED_DOMAINS:
            return False
        return True
        
