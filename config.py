from distutils.debug import DEBUG
from requests import Session

def init():
    global session
    global DEFAULT_DEPTH
    global DATA_PATH
    global CONTENT_TAGS
    global BANNED_DOMAINS
    global MAX_PAGE_COUNT
    global MAX_DEPTH_COUNT
    global DEBUG


    DEBUG = True

    session = Session()
    DATA_PATH = "/home/tafol20/misc/data/"
    DEFAULT_DEPTH = 10

    MAX_PAGE_COUNT = 10
    MAX_DEPTH_COUNT = 3
    CONTENT_TAGS = [('img', 'src'), ('link', 'href'), ('script', 'src')]  # (tag, inner)
    BANNED_DOMAINS = set() # will add urls to be skipped if necessary.