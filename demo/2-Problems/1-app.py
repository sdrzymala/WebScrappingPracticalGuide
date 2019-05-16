import requests
from bs4 import BeautifulSoup

base_url = 'https://www.similarweb.com/top-websites/poland'
request_page = requests.get(base_url)
soup = BeautifulSoup(request_page.text, 'html.parser')

response_text = soup.get_text(separator=' ')

print (response_text)
