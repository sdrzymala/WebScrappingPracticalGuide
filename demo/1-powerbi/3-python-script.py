from bs4 import BeautifulSoup
import requests
import pandas as pd





page_url = r"https://www.alexa.com/topsites/countries/PL"
lst = []




# get page content
page = requests.get(page_url)
soup = BeautifulSoup(page.content, 'html.parser')
all_websites = soup.find_all('div', class_='tr site-listing')





for website in all_websites:

    # get
    website_url = website.find('div', class_='td DescriptionCell').find('p').get_text()
    ranking_no = website.find('div', class_='td').get_text()
    daily_time_on_site = website.find_all('div', class_='td right')[0].get_text()
    daily_pageviews_per_visitor = website.find_all('div', class_='td right')[1].get_text()
    percent_of_traffic_from_search = website.find_all('div', class_='td right')[2].get_text()
    total_sites_linking_in = website.find_all('div', class_='td right')[3].get_text()





    # transform
    website_url = str(website_url).strip()
    ranking_no = str(ranking_no).strip()
    daily_time_on_site = str(daily_time_on_site).strip()
    daily_pageviews_per_visitor = str(daily_pageviews_per_visitor).strip()
    percent_of_traffic_from_search = str(percent_of_traffic_from_search).strip()
    total_sites_linking_in = str(total_sites_linking_in).strip()


    # load
    lst.append([website_url, ranking_no, daily_time_on_site, daily_pageviews_per_visitor, percent_of_traffic_from_search, total_sites_linking_in])





# create data frame
columns_list = ["website_url", "ranking_no", "daily_time_on_site", "daily_pageviews_per_visitor", "percent_of_traffic_from_search" , "total_sites_linking_in"]
df_python = pd.DataFrame(lst, columns=columns_list)

# return
df_python

# print
#print (df_python)
