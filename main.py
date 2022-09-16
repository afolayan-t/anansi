import config


def main():
    config.init() # initializing Global Variables

    from crawler_functions import get_response, get_links, save_page
    from crawler import Crawler

    print("This is Tolu's web crawler; Anansi.")
    initial_link = "http://python.org"

    # crawler_name = input("Please enter the name of your crawler: ")
    # seed_link = input("Please enter the seed link for the crawler: ")
    spiderman = Crawler(name='Anansi', max_page_count=3, debug=True, save_files=False)
    print(f'Loading crawler: {spiderman.name}')
    assert type(initial_link) == str, 'The link most be a string'
    print(f'going to {initial_link} ....')
    spiderman.crawl(initial_link)


if __name__ == "__main__":
    main()