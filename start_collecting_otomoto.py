from offers_collector_otomoto import Otomoto_collector
# from offers_collector_otomoto_dates import Otomoto_collector
db_conn_string = ""



#Latest
starting_page = "https://www.otomoto.pl/osobowe?search%5Border%5D=created_at_first%3Adesc"
next_pages = "https://www.otomoto.pl/osobowe?search%5Border%5D=created_at_first%3Adesc&page="

# #most expensive
# starting_page = "https://www.otomoto.pl/osobowe?search%5Border%5D=filter_float_price%3Adesc"
# next_pages = "https://www.otomoto.pl/osobowe?search%5Border%5D=filter_float_price%3Adesc&page="

# #cheapest
# next_pages = "https://www.otomoto.pl/osobowe?search%5Border%5D=filter_float_price%3Aasc&page="

test = Otomoto_collector(starting_page, next_pages, db_conn_string, 2, 1)
test.collect()