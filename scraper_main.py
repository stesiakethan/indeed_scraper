from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import datetime

class IndeedScraper:
    
    
    options = webdriver.ChromeOptions()
    #Makes browser look less sus to anti-bot
    options.add_argument('--disable-blink-features=AutomationControlled')
    #Uncomment to keep browser open after execution
    #options.add_experimental_option("detach", True)
    
    driver = webdriver.Chrome(options=options,service=Service(ChromeDriverManager().install()))
    
    def __init__(self, st_job_title, st_location):
        self.st_job_title = st_job_title
        self.st_location = st_location
    
    #Types in the search bar and submits
    def job_search(self):
        self.driver.get("https://www.indeed.com/")  
        time.sleep(2)
        input_job_title = self.driver.find_element(By.ID,"text-input-what")
        input_location = self.driver.find_element(By.ID,"text-input-where")
        search_button = self.driver.find_element(By.CLASS_NAME,"yosegi-InlineWhatWhere-primaryButton")
        input_job_title.send_keys(self.st_job_title)
        input_location.send_keys(Keys.CONTROL, "a"); input_location.send_keys(Keys.DELETE)
        input_location.send_keys(self.st_location)
        self.driver.execute_script("arguments[0].click();", search_button)

    #Scrolls into view of and clicks on the next page button
    def next_page(self):
        np_button = self.driver.find_element(By.CSS_SELECTOR,"[aria-label='Next Page']")
        self.driver.execute_script("arguments[0].scrollIntoView();", np_button)
        self.driver.execute_script("arguments[0].click();", np_button)

    #Scraping function
    def get_job_cards(self,traverse=1):
        self.job_search()
        time.sleep(2)
        parsed_job_cards = []
        
        for i in range(traverse):
            job_card_container = self.driver.find_element(By.ID,"mosaic-provider-jobcards")
            job_cards = job_card_container.find_elements(By.CLASS_NAME,"job_seen_beacon")

            #Used to get values with xpath when multiple with the same xpath exist. Xpath index starts at 1, not 0. 
            xpath_index_counter = 1

            
            for job in job_cards:
                
                try:
                    job_title = job.find_element(By.TAG_NAME,"h2").text
                except:
                    job_title = None
                    
                try:
                    job_link = (job.find_element(By.TAG_NAME,"h2")).find_element(By.TAG_NAME,"a").get_attribute("href")
                except:
                    job_link = None
               
                try:
                    company_name = job.find_element(By.XPATH, "(//span[@data-testid='company-name'])[" + str(xpath_index_counter) + "]").text
                except:
                    company_name = None
                    
                try:
                    listing_location = job.find_element(By.XPATH, "(//div[@data-testid='text-location'])[" + str(xpath_index_counter) + "]").text
                except:
                    listing_location = None
                
                try:
                    date_posted = job.find_element(By.XPATH, "(//span[@data-testid='myJobsStateDate'])[" + str(xpath_index_counter) + "]").text
                    #This value often has a newline character that needs to be removed
                    if '\n' in date_posted:
                        date_posted = date_posted.split('\n', 1)[1]
                except:
                    date_posted = None
                    
                
                dic = {"job title":job_title,
                    "date posted":date_posted,
                    "location":listing_location,
                    "link":job_link,
                    "company":{"name":company_name}
                    }
                parsed_job_cards.append(dic)

                xpath_index_counter = xpath_index_counter + 1

            xpath_index_counter = 1

            try:   
                self.next_page()
            except:
                json_dict = {f"listings":parsed_job_cards}
                return json_dict
            time.sleep(1)

        
        json_dict = {f"listings":parsed_job_cards}
        return json_dict

    #Gets one specific value from the job cards, for testing
    def get_value(self,k,traverse=1):
        values = []
        for i in (self.get_job_cards(traverse=traverse)):
            values.append(i[k])
        return values

    #Handles other functions and does the scraping, then outputs to JSON file
    def main(self, traverse=1, output_format="JSON" ):
        json_string = json.dumps(self.get_job_cards(traverse=traverse), indent=2)
        print(json_string)
        with open(f"data/{self.st_job_title} listings near {self.st_location}.json", "w") as f:
            f.write(json_string)

search1 = IndeedScraper("Truck Driver","Pennsylvania")
search1.main(traverse=2)





