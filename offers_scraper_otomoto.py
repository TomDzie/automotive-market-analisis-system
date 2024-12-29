from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import logging
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime, timezone, timedelta
from selenium.webdriver.support import expected_conditions as EC
import re
import requests
import pyodbc

logging.basicConfig(
    level=logging.ERROR,  # Ustawia poziom logowania na ERROR
    filename='errors.log',  # Nazwa pliku logów
    filemode='a',  # Tryb zapisu do pliku ('a' - dopisuje do pliku, 'w' - nadpisuje plik)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Format logów
)

class Otomoto_collector:
    def __init__(self, url, database, scraping_machines, starting_page = 1):

        self.url = url
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

        self.f1 = lambda x: int(re.sub("[^0-9]", "", x))  # replace all non numeric characters



    def add_to_db(self, data_dict):
        # try:
        with pyodbc.connect(self.database) as conn:
            with conn.cursor() as cursor:

                # Przygotuj listę kolumn i wartości
                filtered_data = {k: v for k, v in data_dict.items() if v is not None}
                columns = ', '.join([k.replace(" ", "_") for k in filtered_data.keys()])
                placeholders = ', '.join(['?'] * len(filtered_data))
                
                values = tuple(filtered_data.values())

                
                # Zbuduj zapytanie SQL
                sql_query = f"INSERT INTO Car_Offers ({columns}) VALUES ({placeholders})"
                print(sql_query)
                print(values)
                # Wykonaj zapytanie
                cursor.execute(sql_query, values)
                conn.commit()
        
                print("Dane zostały dodane do bazy.")
        # except Exception as e:
        #     logging.error(f"Error while monitoring Database {e}")

    def get_flask(self):
        BASE_URL = 'http://127.0.0.1:5000/queue/'
        url = f"{BASE_URL}{self.scraping_machines}"
        try:
            response = requests.delete(url)
        except Exception as e:
            logging.error(f"Error while connecting to flask {e}")

        if response: return response.json()['data']
        else: return None
        

    def convert_date(self, date_str):
        # Tworzymy słownik z polskimi miesiącami i ich numeracją
        months = {
            "stycznia": "01", "lutego": "02", "marca": "03", "kwietnia": "04",
            "maja": "05", "czerwca": "06", "lipca": "07", "sierpnia": "08",
            "września": "09", "października": "10", "listopada": "11", "grudnia": "12"
        }
        
        # Dzielimy tekst na części
        parts = date_str.split()
        day = parts[0]
        month = months[parts[1]]
        year = parts[2]

        sql_date = f"{year}-{month}-{day.zfill(2)}"
        
        return sql_date



    def name_conventer(self, data_dict):
        if data_dict["Add Date"] != None:
            data_dict["Add Date"] = self.convert_date(data_dict["Add Date"])

        if data_dict["Used"] != None:
            if "ywany" in data_dict["Used"]: data_dict["Used"] = 1 
            elif data_dict["Used"] != None: data_dict["Used"] = 0

        if data_dict["Accident free"] != None:
            if "Tak" in data_dict["Accident free"]: data_dict["Accident free"] = 1 
            elif data_dict["Accident free"] != None: data_dict["Accident free"] = 0

        if data_dict["Damaged"] != None:
            if "Tak" in data_dict["Damaged"]: data_dict["Damaged"] = 1 
            elif data_dict["Damaged"] != None: data_dict["Damaged"] = 0

        if data_dict["Leasing"] != None:
            if "Tak" in data_dict["Leasing"]: data_dict["Leasing"] = 1 
            elif data_dict["Leasing"] != None: data_dict["Leasing"] = 0

        if data_dict["Registered"] != None:
            if "Tak" in data_dict["Registered"]: data_dict["Registered"] = 1 
            elif data_dict["Registered"] != None: data_dict["Registered"] = 0

        translate_dict = {
            "Manualna": "Manual",
            "Automatyczna": "Automatic",
            "Na przednie koła": "Front wheel",
            "Na tylnie koła": "Rear wheel",
            "stały": "Full AWD",
            "dołączany ręcznie": "Manual AWD",
            "dołączany automatycznie": "Automatic AWD",
            "Benzyna": "Gas",
            "Osoba prywatna": "Private",
            "profesjonalny" : "Company",
            "Benzyna+LPG": "Gas+LPG",

        }
        for i in data_dict:
            for j in translate_dict:
                if j in str(data_dict[i]):
                    data_dict[i] = translate_dict[j]
        gmt_plus_1 = datetime.now(timezone.utc) + timedelta(hours=1)
        current_date = gmt_plus_1.strftime('%Y-%m-%d')
        if data_dict["Add Date"] !=None:
            date1 = datetime.strptime(data_dict["Add Date"], "%Y-%m-%d")
            date2 = datetime.strptime(current_date, "%Y-%m-%d")
            diffirence = date2-date1
            data_dict["Days Online"] = diffirence.days
        data_dict["Scrape Date"] = current_date
        return data_dict
    

    def scrape_offer(self, driver, url, id, cookie):
        offer_data_dict = {
            "description": None,
            "Add Date": None,
            "Make": None,
            "Price": None,
            "Version": None,
            "Model Name": None,
            "Generation": None,
            "Production Year": None,
            "Mileage": None,
            "Capacity": None,
            "Fuel Tyep": None,
            "Power": None,
            "Transmision": None,
            "Drivetrain": None,
            "Door Count": None,
            "Color": None,
            "Accident free": None,
            "Damaged": None,
            "ID": id,
            "VIN": None,
            "Country of Origin": None,
            "Body type": None,
            "Leasing": None,
            "Location": None,
            "Seller Name": None,
            "Seller Type": None,
            "Used": None,
            "Registered": None,
            "Platform": "Otomoto",
            "First Owner": None,
            "Days Online": None,
            "Scrape Date": None,
            "URL": url,

            }
        try:
            driver.get(f"{url}")
            # cookie accept click
            if cookie:
                try:
                    # driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
                    WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))).click()
                except Exception as e:
                    logging.error(f"Error while clicking cookie accept button: {e}")              
            

            #VIN cover click
            try:
                driver.find_element(By.CSS_SELECTOR, ".ooa-1hkppo4.e6ymdfe2").click() #VIN
                #VIN finder
                try:
                    vin = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".e6ymdfe0.ooa-1pe3502.er34gjf0"))
                )
                    # vin  = driver.find_element(By.CSS_SELECTOR, ".e6ymdfe0.ooa-1pe3502.er34gjf0").text
                    offer_data_dict["VIN"] = vin.text

                except Exception as e:
                    logging.error(f"Error while reading VIN cover element: {e}")
            except Exception as e:
                logging.error(f"Error while clicking VIN cover element: {e}")
            

            

            #description finder
            try:
                offer_description  = driver.find_element(By.CSS_SELECTOR, ".ooa-c9zdil").text 
                offer_data_dict["description"] = offer_description
            except Exception as e:
                logging.error(f"Error while reading offer description: {e}")
        
            #main details finder
            try:
                main_details_section = driver.find_element(By.CSS_SELECTOR, "div[data-testid='main-details-section']")
                children = main_details_section.find_elements(By.XPATH, "./*")
                #Wyświetlenie tagów każdego z dzieci
                print("------------------------------------------------------ main details -----------------------------------------------------------------")
                for child in children:
                    paragraphs = child.find_elements(By.TAG_NAME, "p")
                    if paragraphs:  # Sprawdź, czy istnieją paragrafy
                        if  "Przeb" in paragraphs[-2].text:
                            offer_data_dict["Mileage"] = int(self.f1(paragraphs[-1].text))
                        elif "paliw" in paragraphs[-2].text:
                            offer_data_dict["Fuel Type"] = paragraphs[-1].text
                        elif "krzyni" in paragraphs[-2].text:
                            offer_data_dict["Transmision"] = paragraphs[-1].text
                        elif "nadwo" in paragraphs[-2].text:
                            offer_data_dict["Body type"] = paragraphs[-1].text
                        elif "Pojem" in paragraphs[-2].text:
                            offer_data_dict["Capacity"] = int(self.f1(paragraphs[-1].text))
                        elif "Moc" in paragraphs[-2].text:
                            offer_data_dict["Power"] = int(self.f1(paragraphs[-1].text))

            except Exception as e:
                logging.error(f"Error while reading main details: {e}")


            #basic information finder
            try:
                basic_information_section = driver.find_element(By.CSS_SELECTOR, "div[data-testid='content-basic-information-section']")
                children = basic_information_section.find_elements(By.XPATH, "./*")
                # Wyświetlenie tagów każdego z dzieci
                print("------------------------------------------------------ basic_information_section -----------------------------------------------------------------")
                for child in children[1:-1]:
                    paragraphs = child.find_elements(By.TAG_NAME, "p")
                    if paragraphs:  # Sprawdź, czy istnieją paragrafy
                        if  "produkcj" in paragraphs[-2].text:
                            offer_data_dict["Production Year"] = int(self.f1(paragraphs[-1].text))
                        elif "pojazdu" in paragraphs[-2].text:
                            offer_data_dict["Model Name"] = paragraphs[-1].text
                        elif "drzwi" in paragraphs[-2].text:
                            offer_data_dict["Door Count"] = paragraphs[-1].text
                        elif "Kolor" in paragraphs[-2].text:
                            offer_data_dict["Color"] = paragraphs[-1].text
                        elif "Wersja" in paragraphs[-2].text:
                            offer_data_dict["Version"] = paragraphs[-1].text
                        elif "Generacja" in paragraphs[-2].text:
                            offer_data_dict["Generation"] = paragraphs[-1].text

            except Exception as e:
                logging.error(f"Error while reading basic_information_section: {e}")

            
            #specification clicker
            try:
                driver.find_element(By.ID, "content-technical-specs-section__toggle").click()
                # specification finder
                try:
                    specification_section = driver.find_element(By.ID, "content-technical-specs-section__collapse")
                    children = specification_section.find_elements(By.XPATH, "./*")
                    # Wyświetlenie tagów każdego z dzieci
                    for child in children:
                        paragraphs = child.find_elements(By.TAG_NAME, "p")
                        if paragraphs:  # Sprawdź, czy istnieją paragrafy
                            if  "Nap" in paragraphs[-2].text:
                                offer_data_dict["Drivetrain"] = paragraphs[-1].text

                except Exception as e:
                    logging.error(f"Error while reading specification_section: {e}")
            except Exception as e:
                logging.error(f"Error while clicking spec: {e}")


            #condition and history clicker
            try:
                driver.find_element(By.ID, "content-condition-history-section__toggle").click()
                # condition and history finder
                try:
                    condition_and_history = driver.find_element(By.ID, "content-condition-history-section__collapse")
                    children = condition_and_history.find_elements(By.XPATH, "./*")
                    # # Wyświetlenie tagów każdego z dzieci
                    print("------------------------------------------------------ condition and history -----------------------------------------------------------------")
                    for child in children:
                        paragraphs = child.find_elements(By.TAG_NAME, "p")
                        if paragraphs:  # Sprawdź, czy istnieją paragrafy
                            if  "Stan" in paragraphs[-2].text:
                                offer_data_dict["Used"] = paragraphs[-1].text
                            elif "wypadkowy" in paragraphs[-2].text:
                                offer_data_dict["Accident free"] = paragraphs[-1].text
                            elif "pochodzenia" in paragraphs[-2].text:
                                offer_data_dict["Country of Origin"] = paragraphs[-1].text
                            elif "rejestrowany" in paragraphs[-2].text:
                                offer_data_dict["Registered"] = paragraphs[-1].text
                            elif "szkodzony" in paragraphs[-2].text:
                                offer_data_dict["Damaged"] = paragraphs[-1].text
                except Exception as e:
                    logging.error(f"Error while reading condition_and_history: {e}")
            except Exception as e:
                logging.error(f"Error while clicking condition and history: {e}")




            #financing clicker
            try:
                driver.find_element(By.ID, "content-financial-information-section__toggle").click()
                # financing finder
                try:
                    financing = driver.find_element(By.ID, "content-financial-information-section__collapse")
                    children = financing.find_elements(By.XPATH, "./*")
                    # Wyświetlenie tagów każdego z dzieci
                    print("------------------------------------------------------ financing -----------------------------------------------------------------")
                    for child in children:
                        paragraphs = child.find_elements(By.TAG_NAME, "p")
                        if paragraphs:  # Sprawdź, czy istnieją paragrafy
                            if  "Stan" in paragraphs[-2].text:
                                offer_data_dict["Used"] = paragraphs[-1].text
                except Exception as e:
                    logging.error(f"Error while reading financing: {e}")
            except Exception as e:
                # logging.error(f"Error while clicking financing: {e}")
                pass

            #seller name finder 
            try:
                seller_name = driver.find_element(By.CSS_SELECTOR, ".ooa-10egq61.ern8z621").text
                offer_data_dict["Seller Name"] = seller_name
            except Exception as e:
                logging.error(f"Error while reading seller name: {e}")
            

            #seller info
            try:
                seller_info = driver.find_element(By.CSS_SELECTOR, ".ooa-em9in.eme06u0").text
                seller_info = seller_info.split(" ")
                offer_data_dict["Seller Type"] = seller_info[0] + " " + seller_info[1]
            except Exception as e:
                logging.error(f"Error while reading seller info: {e}")
            

            #seller destination
            try:
                seller_destination = driver.find_element(By.CSS_SELECTOR, "div[data-testid='aside-seller-info']")
                seller_destination = seller_destination.find_element(By.CSS_SELECTOR, ".e1m6rqv1.ooa-lygf4m").text
                offer_data_dict["Location"] = seller_destination
                # print(seller_destination)
            except Exception as e:
                logging.error(f"Error while reading seller destinatnion: {e}")

            

            #date added
            try:
                date_added = driver.find_element(By.CSS_SELECTOR, ".e1jwj3576.ooa-193mje5").text
                offer_data_dict["Add Date"] = date_added
            except Exception as e:
                logging.error(f"Error while reading date added: {e}")

            #Price
            try:
                price = driver.find_element(By.CSS_SELECTOR, ".offer-price__number.evnmei44.ooa-1kdys7g.er34gjf0").text
                if "," in price:
                    price_table = price.split(",")
                    price = price_table[0]
                offer_data_dict["Price"] = int(self.f1(price))
            except Exception as e:
                logging.error(f"Error while reading price: {e}")

            #Make
            try:
                make = driver.find_elements(By.CSS_SELECTOR, ".ooa-yicfw5")
                offer_data_dict["Make"] = make[1].text
            except Exception as e:
                logging.error(f"Error while reading make: {e}")
            

        except Exception as e:
            logging.error(f"Error occurred during connecting: {e}")

        return offer_data_dict
    

    def start_scraping(self):
        cookie_flag = True
        loop_counter = 1
        while True:
            try:
                url_batch = self.get_flask()
            except Exception as e:
                print(e)
                time.sleep(5)
                continue
            if url_batch == None:
                print("no data to download from Flask server")
                time.sleep(5)
                continue
            for i in url_batch:
                scraped_data = self.scrape_offer(self.driver, i[1], i[0], cookie_flag)
                clean_data = self.name_conventer(scraped_data)
                self.add_to_db(clean_data)
                print(f"Scraped offer nr: {loop_counter}")
                cookie_flag =False
                loop_counter +=1

        
