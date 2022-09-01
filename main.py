import config


def main():
    config.init() # initializing Global Variables

    from crawler_functions import get_response, get_links, save_page
    from crawler import Crawler

    print("This is Tolu's web crawler; Anansi.")
    initial_link = "http://python.org"

    spiderman = Crawler(name='spiderman', max_page_count=3)

    assert type(initial_link) == str, 'The link most be a string'
    print(f'going to {initial_link} ....')
    spiderman.crawl(initial_link)
    # resp = get_response(initial_link)
    # local_links, links = get_links(resp, initial_link)
    # print(local_links)
    # print(save_page(resp, content=config.CONTENT_TAGS))


if __name__ == "__main__":
    main()