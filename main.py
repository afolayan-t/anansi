import config


def main():
    config.init() # initializing Global Variables

    from crawler import Crawler

    print("This is Tolu's web crawler; Anansi, it crawls the web.")
    initial_link = "http://python.org"

    # crawler_name = input("Please enter the name of your crawler: ")
    # seed_link = input("Please enter the seed link for the crawler: ")
    # num_threads = int(input("Number of Threads: "))
    spiderman = Crawler(name='Anansi', debug=True, save_files=False, record_frequency=True, number_of_threads=2)
    print(f'Loading crawler: {spiderman.name}')
    assert type(initial_link) == str, 'The link most be a string'
    print(f'going to {initial_link} ....')
    spiderman.crawl(initial_link,  max_page_count=10, max_depth_count=5)
    print(spiderman.get_word_frequency()[0:10])


if __name__ == "__main__":
    main()