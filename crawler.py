import os, sys, time, re, json, csv
from datetime import datetime
from collections import deque

# local
import config
from crawler_functions import get_links, get_response, save_page, parse_plain_text

class Crawler:
    """
    This is the main web crawler class that controls the over time 
    crawling of websites. Including the file queue, file saving, and
    higher management of the web crawling process. I also want to use 
    this to manage analytics and data. 
    """
    # class variable
    num_crawlers = 0

    def __init__(self, name:str="", file_path:str=config.DATA_PATH, save_files:bool=False, record_frequency:bool=False, verbose:bool=False, debug:bool=False):
        """initialize url queue, visited url queue, depth, etc"""
        self.name = name if name else f'crawler_{self.__class__.num_crawlers}'
        self.to_visit = deque()
        self.visited = set() # hash the link name if it is in the list, don't visit again.
        self.max_page_count = config.MAX_PAGE_COUNT
        self.file_path = file_path if type(file_path) == str else config.DATA_PATH

        self.depth_counter = 0

        # crawler options
        self.debug = debug
        self.verbose = verbose if type(verbose) == bool else False
        self.save_files = save_files
        self.record_frequency = record_frequency
        if self.record_frequency: self.frequency_map = dict()
        
        # increment global crawler variable.
        self.__class__.num_crawlers+=1

    def __repr__(self):
        return self.name


    def progress(max_depth: int) -> None:
        pass
        

    def crawl(self, link:str, max_page_count:int=config.MAX_PAGE_COUNT, max_depth_count:int=config.MAX_DEPTH_COUNT, link_sampler=None) -> None: 
        """
        This runs the web crawling, until stopping conditions are met. Crawls to a
        certain depth, i.e. saves and index 10 layers of pages. Our function will
        use a breadth first search algorithm to run, it will also prioritize following
        local links over links that go to other domains.

        We will implement multithreading to speed up the process. 
        """

        self.to_visit.append(link) # add first link to q
        date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")

        self.links_processed = 0

        self.local_to_visit_current = deque()
        self.local_to_visit_next  = deque()

        self.page_count = max_page_count
        self.depth_count = max_depth_count

        folder_name = f"{self.name}_{date}"
        if not os.path.exists(config.DATA_PATH+f'{folder_name}'):
            folder_name = config.DATA_PATH+f'{folder_name}'
            os.mkdir(folder_name)

        count = 0
        while self.depth_count >= 0:
            page_count = max_page_count
            print("processing page links")
            while page_count >= 0:
                print(f'page {page_count}')
                if self.local_to_visit_current: 
                    link = self.local_to_visit_current.popleft()
                elif self.to_visit: 
                    link = self.to_visit.popleft()
                else: continue
                print(link)
                
                self.index(link, folder_name)
                page_count -= 1
                count += 1
            
            self.local_to_visit_current = self.local_to_visit_next
            self.local_to_visit_next = deque()
            self.depth_count -= 1
        
        # once crawl end condition is reached, return and stop process.
        return


    def index(self, link:str, folder_name:str) -> bool:
        """grabs links and other info out of files and saves them, to specified file paths."""
        # index links to add to queue
        try:
            assert self.filter(link), f'link was rejected from indexing: {link}'
            resp = get_response(link)
            print("got to resp", resp)
            mod_link = link.replace('/', '').replace(':', '').replace('https', '').replace('http', '')
            local_links, foreign_links = get_links(resp, link)
            if self.save_files: save_page(resp, foldername=folder_name, pagefilename=mod_link, content=config.CONTENT_TAGS, debug=self.debug)
            if self.record_frequency:
                plain_text = parse_plain_text(resp) # convert from response to plain text for html page.
                self.index_frequency(plain_text) # add words from plain text into frequency_map.
            self.links_processed += 1

            # indexing completed, finish with this link 
            self.visited.add(link)
            self.to_visit.extend(foreign_links)
            self.local_to_visit_next.extend(local_links)
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
    

    @staticmethod
    def sanitize_word(word: str):
        sanitized = re.sub('[^A-Za-z0-9]+', '', word)
        return sanitized


    # TODO: make a nlp to detect text language
    # TODO: make a nlp to extract nouns?
    def index_frequency(self, text:str) -> None: # O(# of words)
        """"""
        text_list = text.split(' ') # splitting text by spaces into a list of strings.
        for word in text_list:
            sanitized_word = self.sanitize_word(word)
            if sanitized_word == '': continue
            if sanitized_word in self.frequency_map: self.frequency_map[sanitized_word] += 1
            else: self.frequency_map[sanitized_word] = 1
        return


    def get_word_frequency(self) -> list:
        """Returns list of all words in frequency, in descending order."""
        freq_list = sorted(self.frequency_map.items(), key=lambda x:-1*x[1]) # ~O(nlogn)
        return freq_list


    # TODO: test json and csv methods
    def get_frequency_json(self):
        return json.dumps(self.frequency_map)

    def save_frequency_json(self, folder:str="json"):
        try:
            with open(folder+"", "w") as  f:
                json.dumps(self.get_frequency_json(), f)
        except IOError:
            print("I/O error")
        

    def save_frequency_csv(self, folder:str="csv"):
        csv_columns = ['word', 'count']
        try:
            with open(folder+"", 'w') as f:
                writer = csv.DictWriter(f, fieldnames=csv_columns)
                writer.writeheader()
                for data in self.frequency_map:
                    writer.writerow(data)

        except IOError:
            print("I/O error")
