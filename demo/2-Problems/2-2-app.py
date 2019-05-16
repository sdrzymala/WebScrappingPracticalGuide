import os  
from selenium import webdriver  
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

### "Distil Networks" ###

base_url = 'https://www.similarweb.com/top-websites/poland'
page_load_timeout = 60
chromium_path = r"‪chromedriver.exe"

# https://stackoverflow.com/questions/33225947/can-a-website-detect-when-you-are-using-selenium-with-chromedriver#comment69663876_41220267

#username = 'slawo'
#userProfile = "C:\\Users\\" + username + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default"

chrome_options = Options()
chrome_options.add_argument("--headless")
#chrome_options.add_argument("user-data-dir={}".format(userProfile))
#chrome_options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors", "safebrowsing-disable-download-protection", "safebrowsing-disable-auto-update", "disable-client-side-phishing-detection"])

#chrome_options.add_argument('--disable-gpu')
#chrome_options.add_argument("--disable-extensions")
#chrome_options.add_argument("--log-level=2")
#chrome_options.add_argument("--enable-javascript")
#browser = webdriver.Chrome() # to run without headless mode
browser = webdriver.Chrome(chrome_options=chrome_options, executable_path="chromedriver")
#browser.execute_script("document.body.style.zoom='100'")

# go to the url
browser.get(base_url)

# sleep 5 seconds
time.sleep(3) 

# get website stats
allAppsTitles = browser.find_elements_by_xpath("//tbody['topRankingGrid-body']//tr[@class='topRankingGrid-row']")
browser.save_screenshot('selenium.png')
browser.quit()
