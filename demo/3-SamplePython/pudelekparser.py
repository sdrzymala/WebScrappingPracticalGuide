#region import
from pudelekparsertoolkit.toolkit import Toolkit
import argparse
#endregion


#region prepare and get arguments
parser = argparse.ArgumentParser(description='Scrapping Pudelek')
parser.add_argument('--log_path', type=str, help='path to log file', default='myapp.log')
parser.add_argument('--selenium_driver_path', type=str, help='path to selenium executable file', default=r'E:\Tools\selenium_drivers\chromedriver.exe')
parser.add_argument('--db_connectionstring', type=str, help='database connection string', default='DRIVER={ODBC Driver 17 for SQL Server};SERVER=XX.XX.XX.XX;DATABASE=Pudelek;UID=sa;PWD=XX')
parser.add_argument('--run_type', type=str, help='type of run, [al] - articles list, [ad] - articles details', default='ad')
parser.add_argument('--al_start_page', type=str, help='start page to get list of articles', default='1')
parser.add_argument('--al_no_pages', type=str, help='number of pages to get list of articles', default='5')
parser.add_argument('--ad_no_pages', type=str, help='number of pages to get articles details', default='5000')
args = parser.parse_args()

log_file_path = args.log_path
selenium_driver_path = args.selenium_driver_path
db_connectionstring = args.db_connectionstring
run_type = args.run_type
al_start_page = args.al_start_page
al_no_pages = args.al_no_pages
ad_no_pages = args.ad_no_pages
#endregion


#region initialize pudelek parser toolkit

toolkit = Toolkit(log_file_path, db_connectionstring, selenium_driver_path)

if run_type == 'al':
    toolkit.get_articles_urls_and_save_to_db(al_no_pages, al_start_page)
elif run_type == 'ad':
    toolkit.get_articles_content_using_selenium_and_save_to_db(ad_no_pages)
else:
    raise ValueError('Selenium drivers path not provided')
    
#endregion