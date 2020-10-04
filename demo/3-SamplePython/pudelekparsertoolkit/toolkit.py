#region import

# logic and app utils
import time
import datetime
from dateutil import parser
import re
from random import randint
import urllib
from contextlib import contextmanager
import sys
import os
import traceback
import logging
from functools import wraps

#internal
from .helpermethods import clean_text

# selenium and related
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options  
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

# database related
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import func
import pyodbc

#endregion


#region decorators
def timeit(method):
    """
    Decorator. Measure the time of the method's execution and get the exceptions. Save the output to the log file.
    
    Parameters:
       * method - any method
    """
    def timed(*args, **kw):

        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            logging.info("{}({}) | [{:%Y-%m-%d %H:%M:%S} - {:%Y-%m-%d %H:%M:%S}] | {:2.2f} ms".format(
                                                    method.__name__, 
                                                    ", ".join([str(x) for x in args[1:]]).strip(), 
                                                    datetime.datetime.fromtimestamp(te),
                                                    datetime.datetime.fromtimestamp(ts),
                                                    (te - ts) * 1000)
                                                )

        return result
    return timed
#endregion


class Toolkit:


    @timeit
    def __init__(self, log_file_path: str, db_connectionstring: str, selenium_driver_path: str):
        """
        Initialize Toolkit

        Parameters:
           * log_file_path: str - path to the log file
           * db_connectionstring: str - connection to the database
           * selenium_driver_path: str - path to the selenium driver exe file
        """

        #region configure logging
        logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=log_file_path,
                    filemode='a')
        #endregion

        #region adjust when running from docker
        if os.environ.get('IS_RUNNING_FROM_DOCKER') == 'Yes':
            selenium_driver_path = r'/app/chromedriver'
        #endregion

        #region configure selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--log-level=2")
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")
        d = DesiredCapabilities.CHROME
        d['goog:loggingPrefs'] = { 'performance':'ALL' }
        self.browser = webdriver.Chrome(desired_capabilities=d,executable_path=selenium_driver_path, chrome_options=chrome_options)
        self.browser.set_page_load_timeout(180)
        self.browser.execute_script("document.body.style.zoom='100'")
        self.browser.set_window_size(1366, 768)
        self.browser.maximize_window()
        self.browser_max_wait_delay = 180
        time.sleep(5) # let him initialize...
        self.base_url = r"https://www.pudelek.pl/archiwum/"
        #endregion

        #region setup and prepare db
        params = urllib.parse.quote_plus(db_connectionstring)
        Base = automap_base()
        engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))
        Base.prepare(engine, reflect=True)
        self.Articles = Base.classes.Articles
        self.Comments = Base.classes.Comments
        self.Tags = Base.classes.Tags
        self.RelatedArticles = Base.classes.RelatedArticles
        self.session = Session(engine)
        #endregion

        #region other variables
        self.are_cookies_accepted = 0
        #endregion


    @timeit
    def dispose(self):
        """
        Close selenium browser
        """
        self.browser.quit()


    @timeit
    def accept_cookies(self):
        """
        Accept cookies when entering the website.
        Once entering the website the "accept cookies" popup will appear.
        Click on the "accept" button to accept the cookies
        """
        try:
            element = self.browser.find_element_by_xpath("//button[contains(text(),'AKCEPTUJĘ I\xa0PRZECHODZĘ DO\xa0SERWISU')]")
            element.click()
            self.are_cookies_accepted = 1
            time.sleep(5)
        except:
            pass
  

    @timeit
    def wait_till_page_will_be_fully_loaded(self):
        """
        Wait till entire page will be loaded.
        There is a lot of dynamic content on the website. Therefore to be able to get all of the details,
        we need to wait till all of those content will be loaded. In order to do that we will check once
        all of the network traffic (all of the internal request) will finish.
        """

        # save screenshoot before - just for demo purpose
        self.browser.find_element_by_xpath("//div[@id='page_content']").screenshot("./misc/before.png")
        
        # scroll to the very bottom to the page, incrementally
        total_height = int(self.browser.execute_script("return document.body.scrollHeight"))
        for i in range(1, total_height, 5):
            self.browser.execute_script("window.scrollTo(0, {});".format(i))

        number_of_current_requests = -1
        while number_of_current_requests != 0:
            # after reading the logs will be cleaned 
            # once the number of request will be equal to 0
            # that will means that the loading is finished*
            # naive, but in that case it should be enough
            number_of_current_requests = len(self.browser.get_log('performance'))
            time.sleep(5)

        # save screenshot after - just for demo purpose
        self.browser.find_element_by_xpath("//div[@id='page_content']").screenshot("./misc/after.png")


    @timeit
    def get_articles_urls_and_save_to_db(self, numberOfPagesToParse : int, startPageNumber : int):
        """
        Navigate to the "archive" page. The page contains the list of all articles grouped by day.
        Iterate through each day and get all links avalaible. At the end save all links to database.

        Parameters:
           * numberOfPagesToParse : int - number of pages (days) to get artlicles from
           * startPageNumber : int - number of pages to skip when getting the list of articles
        """

        for i in range(int(startPageNumber), int(startPageNumber)+int(numberOfPagesToParse) + 1):
            
            # create container for all articles that were discovered
            articles = []

            #region get article urls
            try:

                # prepare current archive page url
                number_of_days_to_deduct = i * (-1)
                current_date = datetime.date.today() + datetime.timedelta(days=number_of_days_to_deduct)
                current_date_as_string = str(current_date.strftime('%Y-%m-%d'))
                current_url = self.base_url + current_date_as_string
                
                # navigate to the current archive page url
                self.browser.get(current_url)
    
                # when the website will open for the first time 
                # the popup to accept cookis will apear
                # accept cookies if the windows will appear
                if self.are_cookies_accepted == 0:
                    self.are_cookies_accepted()
                
                # get all articles urls from current archive page url
                articles_present = EC.presence_of_element_located((By.XPATH, "//div[@id='page_content']//ul[@class='v8y7lv-2 feKzvo']//li//div[@class='sc-1y9p6z6-0 bxgzCh']//a"))
                WebDriverWait(self.browser, 10).until(articles_present)
                articles = self.browser.find_elements_by_xpath("//div[@id='page_content']//ul[@class='v8y7lv-2 feKzvo']//li//div[@class='sc-1y9p6z6-0 bxgzCh']//a")

            except Exception as e:
                logging.exception(e, exc_info=True)
            #endregion


            for article in articles:
                
                # get details about current article
                current_article_url = article.get_attribute("href")
                current_article_title = article.get_attribute("innerText")
                
                #region check and assign type to article
                article_type = None
                if 'foto' in current_article_title.lower() or 'zdjęcia' in current_article_title.lower():
                    article_type = 'foto'
                elif 'video' in current_article_title.lower() or 'wideo' in current_article_title.lower():
                    article_type = 'wideo'
                else:
                    article_type = 'artykuł'
                #endregion


                #region save article details to database (only if not already added)
                if self.session.query(self.Articles).filter_by(article_url=current_article_url).count() == 0:
                    try:
                        self.session.add(
                            self.Articles(
                                article_url=current_article_url,
                                article_type=article_type,
                                article_is_downloaded = False,
                                article_inserted_at = datetime.datetime.now()
                            )
                        )
                        self.session.commit()
                    except Exception as e:
                        logging.exception(e, exc_info=True)
                #endregion

            # report current url
            print (str(i) + ") " + current_url + " : " + str(len(articles)))

            # sleep a bit to avoid beeing blocked
            time.sleep(randint(1,9))

        # once done, close the browser
        self.dispose()


    @timeit
    def get_articles_content_using_selenium_and_save_to_db(self, numberOfArticlesToDownload : int):
        """
        Get given number of articles from database and invoke the method to parse them.

        Parameters:
           * numberOfArticlesToDownload : int - number of articles that will be taken from database
        """

        # get articles urls from database 
        articles_to_download = self.session.query(self.Articles).order_by(func.newid()).filter_by(article_is_downloaded = False).limit(numberOfArticlesToDownload).all()

        for article in articles_to_download:
            
            # region download article details
            self.get_single_article_content_basic_article_using_selenium_and_save_to_db(article.article_url, article.article_id)
            # sleep a bit to avoid beeing blocked
            time.sleep(randint(1,9))

        # once all of the articles are parsed close the chrome browser        
        self.dispose()


    @timeit
    def get_single_article_content_basic_article_using_selenium_and_save_to_db(self, url : str, current_article_id):


        #region prepare variables
        article_title = None
        article_created_at = None
        article_author = None
        article_content = None
        article_number_of_comments = None
        article_number_of_images = None
        article_number_of_bolded_text = None
        article_has_slideshow = None
        article_number_of_videos = False
        article_number_of_instagram_posts = None
        tags = []
        relatedArticles = []
        comments = []
        #endregion


        #region load page

        # report current url
        print (url)

        # go to the article url
        self.browser.get(url)
        time.sleep(5)

        if self.are_cookies_accepted == 0:
            self.accept_cookies()
        self.wait_till_page_will_be_fully_loaded()

        #endregion
                
     
        #region get title
        try:
            _article_title = self.browser.find_element_by_xpath("//div[@id='page_content']//h1[@class='sc-7hqr3i-0 am69kv-0 haMoKs']")
            article_title = clean_text(str(_article_title.get_attribute("innerText")))
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion


        #region get author
        try:
            _article_author = self.browser.find_element_by_xpath("//div[@id='page_content']//div[@class='sc-7hqr3i-0 am69kv-0 bFJBwl']")
            article_author = clean_text(str(_article_author.get_attribute("innerText")))
        except Exception as e:
            #logging.exception(e, exc_info=True)
            pass
        #endregion


        #region get creation datetime
        try:
            _article_created_at = self.browser.find_element_by_xpath("//div[@id='page_content']//div[@class='sc-7hqr3i-0 eEjJeK']//time")
            article_created_at = parser.parse(_article_created_at.get_attribute("datetime"), "")
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion


        #region get number of comments
        try:
            article_number_of_comments = 0
            _article_number_of_comments_candidates = self.browser.find_elements_by_xpath("//div[@id='page_content']//div[@data-st-area='st-gallery-reactions']//div[@class='sc-7hqr3i-0 am69kv-0 dnvMrW']")
            for element in _article_number_of_comments_candidates:
                current_element_text = clean_text(str(element.get_attribute("innerText")))
                if current_element_text.isdigit():
                    article_number_of_comments = current_element_text
                    break
       
            article_number_of_comments = article_number_of_comments
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion
      

        #region get number of bolded texts
        try:
            _article_number_of_bolded_text = self.browser.find_elements_by_xpath("//div[@id='page_content']//p//strong")
            article_number_of_bolded_text = len(_article_number_of_bolded_text)
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion
 

        #region get number of insgram posts
        article_number_of_instagram_posts = 0
        try:
            article_number_of_instagram_posts = int(len(self.browser.find_elements_by_xpath("//div[@id='page_content']//iframe[@class='instagram-media instagram-media-rendered']")))
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion


        #region get number of images
        _number_of_images = 0
        try:
            _number_of_images = int(len(self.browser.find_elements_by_xpath("//div[@id='page_content']//img[@class='rdkre0-3 dEVfZa']")))
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion


        #region get number of images
        article_number_of_videos = 0
        try:
            article_videos_internal = self.browser.find_elements_by_xpath("//div[@id='page_content']//div[contains(@id, 'video-player')]")
            article_videos_youtube = self.browser.find_elements_by_xpath("//div[@id='page_content']//iframe[contains(@id, 'ytplayer')]")
            article_number_of_videos = len(article_videos_internal) + len(article_videos_youtube)
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion


        #region get number of images (slideshow)
        article_has_slideshow = False
        _images_in_slideshow = 0
        try:
            slideshows = self.browser.find_elements_by_xpath("//div[@id='page_content']//div[@data-st-area='st-gallery']//div[@data-st-area='st-slideshow-next']")

            if len(slideshows) > 0:
                _element_with_images_in_slideshow = self.browser.find_element_by_xpath("//div[@id='page_content']//div[@data-st-area='st-gallery']//div[@class='sc-7hqr3i-0 am69kv-0 sc-1ckcopg-1 liYuuq']")
                _number_of_images_in_slideshow = _element_with_images_in_slideshow.get_attribute("innerText").split(" ")[-1]
                _images_in_slideshow = int(clean_text(str(_number_of_images_in_slideshow)))
                article_has_slideshow = True

        except Exception as e:
            #logging.exception(e, exc_info=True)
            pass
        #endregion


        #region calculate total number of images
        if article_has_slideshow:
            article_number_of_images = _number_of_images + _images_in_slideshow - 1
        else:
            article_number_of_images = _number_of_images
        #endregion


        #region get article text
        try:
            
            all_article_texts = self.browser.find_elements_by_xpath("//div[@id='page_content']//p")
            current_text = ""

            for text in all_article_texts:
                current_text = current_text + text.get_attribute("innerText")
            
            _article_content = clean_text(current_text)
            article_content = _article_content

        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion


        #region get tags
        # example: https://www.pudelek.pl/katarzyna-cichopek-i-maciej-kurzajewski-nowymi-prowadzacymi-pytania-na-sniadanie-6546201597991552a
        try:
            expand_tags_button = self.browser.find_element_by_xpath("//div[@id='page_content']//div[@class='nxa582-0 jrLjTw']")
            expand_tags_button.click()
        except Exception as e:
            pass

        try:
            _tags = self.browser.find_elements_by_xpath("//div[@id='page_content']//div[@class='sc-1ud45e6-0 dIjMrh' or @class='sc-7hqr3i-0 jzn8k8-0 ejqGJA']//a")
            for _tag in _tags:
                current_tag_text = clean_text(_tag.get_attribute("innerText"))
                current_tag_url = _tag.get_attribute("href")
                tag = self.Tags(
                                article_id = current_article_id, 
                                tag_text = current_tag_text, 
                                tag_url = current_tag_url
                            )
                tags.append(tag)
        except Exception as e:
            logging.exception(e, exc_info=True)

        #endregion


        #region get comments
        try:
            
            # get total number of comment's pages
            _comments_pages = self.browser.find_elements_by_xpath("//button[@class='sc-7hqr3i-0 am69kv-0 sc-1e1snaj-1 bNqHWI r7tdk8-4 isiAgP']")
            max_comment_page = max([int(clean_text(comment_page.get_attribute("innerText"))) for comment_page in _comments_pages])

            #region get comments from all pages

            comment_page_i = 1
            while comment_page_i <= max_comment_page:

                #region expand all comments
                _expand_commants_buttons = self.browser.find_elements_by_xpath("//div[@id='page_content']//button[@class='sc-7hqr3i-0 am69kv-0 sc-10vtn1w-0 y3ijg6-0 pLtoi']")
                for expand_commants_buttons in _expand_commants_buttons:
                    try:
                        expand_commants_buttons.click()
                    except Exception as e:
                        pass
                time.sleep(5)
                #endregion
   
                #region get and parse comments
                # get all comments
                _comments = self.browser.find_elements_by_xpath("//div[@id='page_content']//div[@class='sc-7hqr3i-0 gFcGdM']")

                # get all comments details
                for _comment in _comments:
                    #region get single comment

                    try:

                        _comment_highlighted = len(_comment.find_elements_by_xpath(".//div[@class='sc-7hqr3i-0 f5f5sk-1 kvmdow']"))
                        comment_is_highlited = False

                        if _comment_highlighted > 0:
                            comment_is_highlited = True

                        #region get basic comment info
                        _comment_author = _comment.find_element_by_xpath(".//div[@class='sc-7hqr3i-0 am69kv-0 kAOVpF']")
                        _comment_message = _comment.find_element_by_xpath(".//div[@class='sc-7hqr3i-0 am69kv-0 q1w81m-0 LsrOO']")
                        _comment_thumbs_up = _comment.find_element_by_xpath(".//button[@data-st-area='comment-up']")
                        _comment_thumbs_down = _comment.find_element_by_xpath(".//button[@data-st-area='comment-down']")

                        comment_author = clean_text(_comment_author.get_attribute("innerText"))
                        comment_message = clean_text(_comment_message.get_attribute("innerText"))
                        comment_thumbs_up = clean_text(_comment_thumbs_up.get_attribute("innerText"))
                        comment_thumbs_down = clean_text(_comment_thumbs_down.get_attribute("innerText"))
                        #endregion

                        #region add comment to list
                        if len([x for x in comments \
                                        if x.article_id == current_article_id \
                                        and x.comment_author == comment_author \
                                        and x.comment_message == comment_message \
                                        and x.comment_thumbs_up == comment_thumbs_up \
                                        and x.comment_thumbs_down == comment_thumbs_down]) == 0:

                            comment = self.Comments(
                                    article_id = current_article_id, 
                                    comment_author = comment_author,
                                    comment_message = comment_message,
                                    comment_thumbs_up = comment_thumbs_up,
                                    comment_thumbs_down = comment_thumbs_down,
                                    comment_is_highlited = comment_is_highlited
                                )
                            comments.append(comment)

                        #endregion

                    except Exception as e:
                        logging.exception(e, exc_info=True)
                    #endregion

                #endregion
                
                #region navigate to the next comment page
                comment_page_i = comment_page_i + 1
                if comment_page_i != max_comment_page:
                    next_comments_page = WebDriverWait(self.browser, 120).until(EC.presence_of_element_located((By.XPATH, "//button[@class='sc-7hqr3i-0 am69kv-0 sc-1e1snaj-1 bNqHWI r7tdk8-4 isiAgP' and contains(text()," + str(comment_page_i) + ")]")))                
                    next_comments_page.click()
                    time.sleep(5)
                else:
                    break
                #endregion
                
            #endregion

        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion


        #region get related articles list
        try:
            _related_article_candidates = self.browser.find_elements_by_xpath("//div[@id='page_content']//p//a")
            
            for _related_article_candidate in _related_article_candidates:
                related_article_text = clean_text(_related_article_candidate.get_attribute("innerText"))
                related_article_url = _related_article_candidate.get_attribute("href")
                relatedArticle = self.RelatedArticles(
                                        article_id = current_article_id, 
                                        related_article_text = related_article_text, 
                                        related_article_url = related_article_url
                                )
                relatedArticles.append(relatedArticle)

        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion


        #region get number of facebook likes
        # try:

        #     # find iframe with given name
        #     detailFrame = self.browser.find_element_by_xpath("//div[@class='single-entry__header']//iframe[@title='fb:like Facebook Social Plugin']")

        #     # open selected iframe
        #     self.browser.switch_to.frame(detailFrame)

        #     # the iframe code in this case is a bit "encrypted"
        #     # get all texts from all spans
        #     # try to parse each element
        #     # get the first one that contain number
        #     _article_number_of_likes_candidate = self.browser.find_element_by_xpath("//*")
        #     _article_number_of_likes = _article_number_of_likes_candidate.get_attribute("innerText") 
        #     article_number_of_likes = int(re.findall(r'\d+', _article_number_of_likes)[0])

        #     # switch to main window and main frame
        #     self.browser.switch_to.default_content()

        # except Exception as e:
        #     logging.exception(e, exc_info=True)
        #endregion       


        #region save article details to database
        try:
            # save basic article details to database
            self.session.query(self.Articles).filter(self.Articles.article_id == current_article_id).update(
                                {
                                    "article_title" : article_title,
                                    "article_created_at" : article_created_at,
                                    "article_author" : article_author,
                                    "article_content" : article_content,
                                    "article_number_of_comments" : article_number_of_comments,
                                    "article_number_of_images" : article_number_of_images,
                                    "article_has_slideshow" : article_has_slideshow,
                                    "article_number_of_videos" : article_number_of_videos,
                                    "article_number_of_instagram_posts" : article_number_of_instagram_posts,
                                    "article_number_of_bolded_text" : article_number_of_bolded_text,
                                    "article_is_downloaded" : True,
                                    "article_updated_at" : datetime.datetime.now()
                                }
                            )
            self.session.commit()

            # save tags to database
            self.session.bulk_save_objects(tags)
            self.session.commit()

            # save related articles to database
            self.session.bulk_save_objects(relatedArticles)
            self.session.commit()

            # save comments to database
            self.session.bulk_save_objects(comments)
            self.session.commit()

        except Exception as e:
            logging.exception(e, exc_info=True)
        
        #endregion

