from selenium import webdriver
from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timezone, timedelta
import requests
import pyodbc
from itertools import cycle
import time


class Otomoto_collector:
    def __init__(self, url, url_next, database, scraping_machines, starting_page = 1):

        self.url = url
        self.url_next = url_next
        self.database = database
        self.scraping_machines = scraping_machines
        self.starting_page = starting_page
        self.options = Options()
        self.options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2,
                                            "profile.managed_default_content_settings.stylesheets": 2,                                            
                                                    })
        self.options.add_argument("--log-level=3")
        self.options.add_argument("--disable-webrtc")
        self.options.add_argument("--no-first-run")
        self.options.add_argument("--no-service-autorun")
        self.options.add_argument("--blink-settings=imagesEnabled=false")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        # options.add_argument("--window-size=1920,1080")
        self.options.add_argument("window-size=1200,800")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--headless")

        self.driver = webdriver.Chrome(options=self.options)
        self.driver.implicitly_wait(1)


    def config_logs(self):
        # logger config
        logging.basicConfig(filename="scraping_errors.log", 
                        level=logging.ERROR, 
                        format="%(asctime)s - %(levelname)s - %(message)s")


    def monitor_db(self, offers_list):
        conn_str = self.database
        gmt_plus_1 = datetime.now(timezone.utc) + timedelta(hours=1)
        current_date = gmt_plus_1.strftime('%Y-%m-%d')

        offers_list_row, _ = zip(*offers_list)
        try:
            with pyodbc.connect(conn_str) as conn:
                with conn.cursor() as cursor:
                    query = "SELECT ID FROM Car_Offers WHERE id IN ({})".format(','.join('?' * len(offers_list_row)))                    
                    cursor.execute(query, offers_list_row)
                    query_output = cursor.fetchall()
                    
                    offers_in_db = [row[0] for row in query_output] #offers existing in db

                    filtered_offers_list = []
                    for i in offers_list:
                        if str(i[0]) not in offers_in_db: filtered_offers_list.append(i)

                    if offers_in_db:
                        update_query = "UPDATE Car_Offers SET Last_Time_Seen = ? WHERE id IN ({})".format(','.join('?' * len(offers_in_db)))
                        cursor.execute(update_query, [current_date] + offers_in_db)
                        conn.commit()
                    return filtered_offers_list
                    
        except Exception as e:
            logging.error(f"Error while monitoring Database {e}")




    def collect(self):
        try:
            self.driver.get(self.url) #get to starting page

            self.driver.find_element(By.ID, "onetrust-accept-btn-handler").click() #cookie accept

            self.pages = int(self.driver.find_elements(By.CSS_SELECTOR, ".ooa-g4wbjr.e1y5xfcl0")[-1].text) #number of all avalible pages

            offers = self.driver.find_elements(By.CSS_SELECTOR, ".ooa-1yux8sr.e15xeixv0") #get all offers from page .ooa-yca59n.epwfahw0 

            offers_list = []
            for i in offers:
                offers_list.append([i.get_attribute("data-id"), i.find_element(By.CSS_SELECTOR, "a").get_attribute("href")])
            print(self.pages)
        except Exception as e:
            logging.error(f"Error while reading first page: {e}")

        if len(offers_list) >0:
            try:
                offers_to_send = self.monitor_db(offers_list)
            except Exception as e:
                logging.error(f"error while monitoring first page offers {e}")
            
            try: 
                self.send_to_flask(offers_to_send, self.scraping_machines)
            except Exception as e:
                logging.error(f"error while sending to first page offers to flask {e}")
        if self.starting_page > 1: page_counter = self.starting_page
        else:
            page_counter = 1

        while True:
            offers_list = []
            try:
                print(f"Page now: {page_counter},       {self.url_next}{page_counter}")
                self.driver.get(f"{self.url_next}{page_counter}")
                
                page_counter+=1

                offers = self.driver.find_elements(By.CSS_SELECTOR, ".ooa-1yux8sr.e15xeixv0")  #get all offers from page

                for i in offers:
                    offers_list.append([int(i.get_attribute("data-id")), i.find_element(By.CSS_SELECTOR, "a").get_attribute("href")])

                if len(offers_list) >0:
                    try:
                        offers_to_send = self.monitor_db(offers_list)
                        print(offers_to_send)
                        if len(offers_to_send) ==0: continue
                        self.send_to_flask(offers_to_send, self.scraping_machines)
                    except Exception as e:
                        logging.error(f"error while monitoring {page_counter} page offers {e}")

                if page_counter >= self.pages: break
            except Exception as e:
                print(e)


    @staticmethod
    def allocate_offers(offers_list, machine_count): # function for allocating data equaly
        machines = [[] for _ in range(machine_count)]
        cycle_ = cycle(machines)

        for element in offers_list:
            next(cycle_).append(element)
        return machines
    


    def send_to_flask(self, data, machines):
        allocated_data = self.allocate_offers(data, machines)
        BASE_URL = 'http://127.0.0.1:5000/queue/'
        for i in range(1, machines+1):
            response = requests.post(f"{BASE_URL}{i}", json=allocated_data[i-1])
    
        
            
