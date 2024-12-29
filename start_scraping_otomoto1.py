from offers_scraper_otomoto import Otomoto_collector

url = "https://www.otomoto.pl/osobowe/"
db_conn_string = ""
machine = 1
scraper = Otomoto_collector(url, db_conn_string, machine)
scraper.start_scraping()