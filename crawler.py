import os, sys
from datetime import datetime
from threading import Thread, Lock, local
import config
from collections import deque
from crawler_functions import get_links, get_response, parse_page, save_page, parse_plain_text


class Crawler:
    """
    This is the main web crawler class that controls the over time 
    crawling of websites. Including the file queue, file saving, and
    higher management of the web crawling process. I also want to use 
    this to manage analytics and data. 
    """
    # class variable
    num_crawlers = 0

    #TODO: implement page depth algo
    """In order to implement depth, we need to be able to keep track of the depth of our function. 
    I.e. how far we've gone down a path of links. meaning that we need to count how many links get 
    added to our q. example: We have 5 links on a page, put this into a q, once we've counted these 
    links passed, we know we have gone down in depth. If we want we can define a max number of pages
    to be.
    
    """

    def __init__(self, name:str="", max_page_count:int=config.MAX_PAGE_COUNT, file_path:str=config.DATA_PATH, number_of_threads=0, save_files:bool=False, record_frequency:bool=False, verbose:bool=False, debug:bool=False):
        """initialize url queue, visited url quueue, depth, etc"""
        self.name = name if name else f'crawler_{self.__class__.num_crawlers}'
        self.to_visit = deque()
        self.local_to_visit = deque()
        self.visited = set() # hash the link name if it is in the list, don't visit again.
        self.max_page_count = max_page_count if type(max_page_count) == int else config.MAX_PAGE_COUNT
        self.file_path = file_path if type(file_path) == str else config.DATA_PATH

        self.depth_counter = 0
        # crawler options
        self.debug = debug
        self.verbose = verbose if type(verbose) == bool else False
        self.save_files = save_files
        self.record_frequency = record_frequency
        if self.record_frequency: self.frequency_map = dict()

        # threading variables
        self.max_threads = number_of_threads
        self.active_threads = list()
        
        # increment global crawler variable.
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
            if self.debug:
                print('in take job')
                print(exc, file=sys.stderr)
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
        page_count = 0
        date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")

        folder_name = f"{self.name}_{date}"
        if not os.path.exists(config.DATA_PATH+f'{folder_name}'):
            folder_name = config.DATA_PATH+f'{folder_name}'
            os.mkdir(folder_name)

        while (len(self.to_visit) != 0 or len(self.local_to_visit) != 0) and page_count < self.max_page_count:
            if len(self.local_to_visit) != 0: link = self.local_to_visit.popleft()
            else: self.to_visit.popleft()
            self.index(link, folder_name)
            page_count += 1
        
        # once crawl end condition is reached, return and stop process.
        return


    def index(self, link:str, folder_name:str) -> bool:
        """grabs links and other info out of files and saves them, to specified file paths."""
        # index links to add to queue
        try:
            assert self.filter(link), 'file was rejected from indexing'
            resp = get_response(link)
            mod_link = link.replace('/', '').replace(':', '').replace('https', '').replace('http', '')
            local_links, foreign_links = get_links(resp, link)
            if self.save_files: save_page(resp, foldername=folder_name, pagefilename=mod_link, content=config.CONTENT_TAGS, debug=self.debug)
            if self.record_frequency:
                plain_text = parse_plain_text(resp) # convert from response to plain text for html page.
                self.index_frequency(plain_text) # add words from plain text into frequency_map.
            # indexing completed, finsih with this link 
            self.visited.add(link)
            self.to_visit.extend(foreign_links)
            self.local_to_visit.extend(local_links)
            return True
        except Exception as exc:
            if self.debug:
                print('in index')
                print(exc, file=sys.stderr)
            return False
    

    def filter(self, link:str) -> bool:
        """Filtering out files that have been seen before, in this crawl"""
        if link in self.visited or link in config.BANNED_DOMAINS:
            return False
        return True

    
    def index_frequency(self, text:str) -> None: # O(# of words)
        """"""
        text_list = text.split(' ') # splitting text by spaces into a list of strings.
        for word in text_list:
            if word in self.frequency_map: self.frequency_map[word] += 1
            else: self.frequency_map[word] = 1
        return


    def get_word_frequency(self) -> list:
        """Returns list of all words in frequency, in descending order."""
        freq_list = sorted(self.frequency_map.items(), key=lambda x:-1*x[1]) # ~O(nlogn)
        return freq_list
        
