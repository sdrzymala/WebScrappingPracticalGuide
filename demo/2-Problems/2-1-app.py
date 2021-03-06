import os  
from selenium import webdriver  
from selenium.webdriver.chrome.options import Options  
from bs4 import BeautifulSoup
import time

base_url = 'https://www.similarweb.com/top-websites/poland'

chrome_options = Options()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(chrome_options=chrome_options, executable_path="chromedriver")

# go to the url
browser.get(base_url)

# sleep 5 seconds
time.sleep(3) 

# get website stats
allAppsTitles = browser.find_elements_by_xpath("//tbody['topRankingGrid-body']//tr[@class='topRankingGrid-row']")

# print output
for appTile in allAppsTitles:
    websiteRanking = appTile.find_element_by_xpath(".//span[@itemprop='position']")
    websiteName = appTile.find_element_by_xpath(".//span[@class='topRankingGrid-titleName']")
    output = "{} : {}".format(websiteRanking.text ,websiteName.text)
    print (output)


browser.save_screenshot('selenium.png')
browser.quit()
