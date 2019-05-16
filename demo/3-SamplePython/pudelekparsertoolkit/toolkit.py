#region import

#internal
from .helpermethods import clean_text

# selenium and related
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import urllib

# databe related
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import func
import pyodbc

# logic utils
import time
import datetime
from dateutil import parser
import re
from random import randint

# app utils
import sys
import os
import traceback
import logging
from functools import wraps

#endregion


def timeit(method):

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


class Toolkit:


    @timeit
    def __init__(self, log_file_path: str, db_connectionstring: str, selenium_driver_path: str):

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
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")
        #self.browser = webdriver.Chrome(executable_path=self.chromium_path) # to run without headless mode
        self.browser = webdriver.Chrome(executable_path=selenium_driver_path, chrome_options=chrome_options)
        self.browser.set_page_load_timeout(180)
        self.browser.execute_script("document.body.style.zoom='100'")
        self.browser.set_window_size(1366, 768)
        self.browser.maximize_window()
        self.browser_max_wait_delay = 180
        time.sleep(5) # let him initialize...
        self.base_url = r"https://www.pudelek.pl/artykuly/"
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

        
    @timeit
    def dispose(self):
        self.browser.quit()


    @timeit
    def get_articles_urls_and_save_to_db(self, numberOfPagesToParse : int, startPageNumber : int):

        for i in range(int(startPageNumber), int(startPageNumber)+int(numberOfPagesToParse) + 1):
            articles = []




            #region get article urls
            try:
                current_url = self.base_url + str(i) + "/"
                self.browser.get(current_url)
                articles = self.browser.find_elements_by_xpath("//div[@class='news-all']//div[@class='results__entry ' or @class='results__entry results__entry--pudelekx']//h3[@class='entry__title']//a")
            except Exception as e:
                logging.exception(e, exc_info=True)
            #endregion





            for article in articles:

                #region check and assign type to article
                current_article_url = article.get_attribute("href")
                article_type = None
                if current_article_url.lower().startswith("https://www.pudelek.pl/artykul/"):
                    article_type = 'artykul'
                elif current_article_url.lower().startswith("https://tv.pudelek.pl/video/"):
                    article_type = 'video'
                elif current_article_url.lower().startswith("http://pudelekx.pl/"):
                    article_type = 'x'
                else:
                    article_type = 'inny'
                #endregion





                #region save article to database
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

            # sleep a bit to avoid beeing blocked
            time.sleep(randint(1,9))





        self.dispose()




    @timeit
    def get_articles_content_using_selenium_and_save_to_db(self, numberOfArticlesToDownload : int):

        # get articles urls from database 
        articles_to_download = self.session.query(self.Articles).order_by(func.newid()).filter_by(article_is_downloaded = False).limit(numberOfArticlesToDownload).all()

        for article in articles_to_download:
            
            #region download article details
            if article.article_type == 'artykul':
                self.get_single_article_content_basic_article_using_selenium_and_save_to_db(article.article_url, article.article_id)
            elif article.article_type == 'video':
                self.get_single_article_content_basic_video_using_selenium_and_save_to_db(article.article_url, article.article_id)
            elif article.article_type == 'x':
               self.get_single_article_content_basic_x_using_selenium_and_save_to_db(article.article_url, article.article_id)
            else:
                logging.warning("Incorrect article type. Provided type: {}, url: {}, id: {}".format(article.article_type, article.article_url, article.article_id))
            #endregion

            # sleep a bit to avoid beeing blocked
            time.sleep(randint(1,3))

        self.dispose()


    @timeit
    def get_single_article_content_basic_x_using_selenium_and_save_to_db(self, url : str, current_article_id):

        #region prepare variables
        article_title = None
        article_created_at = None
        article_author = None
        article_content = None
        article_number_of_comments = None
        article_number_of_likes = None
        article_number_of_images = None
        article_number_of_bolded_text = None
        article_has_slideshow = None
        article_has_video = False
        tags = []
        relatedArticles = []
        comments = []
        #endregion

        # go to the article url
        self.browser.get(url)





        #region accept webiste policy
        try:
            accept_policy = list([i for i in self.browser.find_elements_by_xpath("//button") if "p" in i.get_attribute("textContent").strip().lower()])[0]
            accept_policy.click()
        except Exception as e:
            # the popup window may not exists, no need to worry if element is not found
            #logging.exception(e, exc_info=True)
            pass
        #endregion
     




        #region get title
        try:            
            _article_title = self.browser.find_element_by_xpath("//div[@id='item']//h1[@class='item-title']")
            article_title = clean_text(str(_article_title.get_attribute("innerText")))
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion





        #region get author
        try:
            _article_author = self.browser.find_element_by_xpath("//div[@class='item-details']//a")
            article_author = clean_text(str(_article_author.get_attribute("innerText")))
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion





        #region get creation datetime
        try:
            _article_created_at = self.browser.find_elements_by_xpath("//head//meta[@property='og:published_at']")[0]
            article_created_at = parser.parse(_article_created_at.get_attribute("content"), "")
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion





        #region get number of comments
        try:
            _article_number_of_comments_candidate = self.browser.find_elements_by_xpath("//head//meta[@property='og:comments_count']")[0]
            _article_number_of_comments = _article_number_of_comments_candidate.get_attribute("content")
            article_number_of_comments = int(clean_text(str(_article_number_of_comments)))
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion





        #region get number of facebook likes
        try:

            # find iframe with given name
            detailFrame = self.browser.find_element_by_xpath("//div[@class='item-details']//iframe[@title='fb:like Facebook Social Plugin']")

            # open selected iframe
            self.browser.switch_to.frame(detailFrame)

            # the iframe code in this case is a bit "encrypted"
            # get all texts from all spans
            # try to parse each element
            # get the first one that contain number
            _article_number_of_likes_candidate = self.browser.find_element_by_xpath("//*")
            _article_number_of_likes = _article_number_of_likes_candidate.get_attribute("innerText") 
            article_number_of_likes = int(re.findall(r'\d+', _article_number_of_likes)[0])

            # switch to main window and main frame
            self.browser.switch_to.default_content()

        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion





        #region get number of bolded texts
        try:
            _article_number_of_bolded_text = self.browser.find_elements_by_xpath("//div[@class='single-entry-text bbtext' or @class='single-article-text' or @class='article']//p")
            article_number_of_bolded_text = len(_article_number_of_bolded_text)
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion
 




        #region get number of images

        #region get number of images (article content)
        _number_of_images = 0
        try:
            _number_of_images = len(self.browser.find_elements_by_xpath("//div[@class='image-container']//img"))
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion

        #region get number of images (slideshow)
        article_has_slideshow = False
        _images_in_slideshow = 0
        try:
            _slideshow = self.browser.find_element_by_xpath("//div[@data-utm_campaign='slideshow']//span[@class='slideshow-current']")
            _images_in_slideshow = int(_slideshow.get_attribute("innerText").split("/")[1])
            article_has_slideshow = True
        except Exception as e:
            #logging.exception(e, exc_info=True)
            pass
        #endregion

        # total number of images in website
        article_number_of_images = _number_of_images or 0 + _images_in_slideshow or 0
        #endregion





        #region get article text
        try:
            all_article_texts = self.browser.find_elements_by_xpath("//div[@class='item-content']//h2[@class='item-description']")
            _article_content = ""

            for text in all_article_texts:
                current_text = text.get_attribute("innerText")
                if (len(current_text) > 0):
                    _article_content += current_text + " "
            
            if len(_article_content) > 0:
                article_content = clean_text(_article_content)

        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion
        




        #region get tags
        try:
            _tags = self.browser.find_elements_by_xpath("//div[@class='item-content']//div[@class='tags']//a")
            
            for _tag in _tags:
                tag = self.Tags(article_id = current_article_id, tag_text = clean_text(_tag.get_attribute("innerText")), tag_url = _tag.get_attribute("href"))
                tags.append(tag)

        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion
        




        #region get comments
        try:
            _comments = self.browser.find_elements_by_xpath("//div[@class='comments-top']//div[@class='comment']")
            
            for _comment in _comments:
                #region get single comment
                try:
                    
                    #region get basic comment info
                    _comment_author = _comment.find_element_by_xpath(".//span[@class='comment-author']")
                    _comment_created_at = _comment.find_element_by_xpath(".//span[@class='comment-date']")
                    comment_message = clean_text(_comment.get_attribute("innerText"))
                    _comment_thumbs_up = _comment.find_element_by_xpath(".//span[@class='yesCount']")
                    _comment_thumbs_down = _comment.find_element_by_xpath(".//span[@class='noCount']")
                    _comment_is_highlited = True
                    #endregion

                    #region get comment message
                    # get entire comment message
                    try:
                        _comment_info = _comment.find_element_by_xpath(".//div[@class='comment-info']")
                        _comment_info = clean_text(_comment_info.get_attribute("innerText"))
                        comment_message = clean_text(comment_message.replace(_comment_info, ''))
                    except Exception as e:
                        logging.exception(e, exc_info=True)

                    # remove any comment info from message
                    try:
                        _comment_options = _comment.find_element_by_xpath(".//div[@class='comment-options']")
                        _comment_options = clean_text(_comment_options.get_attribute("innerText"))
                        comment_message = clean_text(comment_message.replace(_comment_options, ''))
                    except Exception as e:
                        logging.exception(e, exc_info=True)

                    # remove any quotes from comment message
                    try:
                        _comment_message_quote = _comment.find_element_by_xpath(".//div[@class='quote']")
                        _comment_message_quote = clean_text(_comment_message_quote.get_attribute("innerText"))
                        comment_message = clean_text(comment_message.replace(_comment_message_quote, ''))
                    except Exception as e:
                        #logging.exception(e, exc_info=True)
                        pass

                    #endregion  

                    #region add comment to list   
                    comment = self.Comments(
                            article_id = current_article_id, 
                            comment_author = clean_text(_comment_author.get_attribute("innerText")),
                            comment_created_at = datetime.datetime.strptime(clean_text(_comment_created_at.get_attribute("innerText")), "%d %m %y %H %M"),
                            comment_message = comment_message,
                            comment_thumbs_up = clean_text(_comment_thumbs_up.get_attribute("innerText")),
                            comment_thumbs_down = clean_text(_comment_thumbs_down.get_attribute("innerText")),
                            comment_is_highlited = _comment_is_highlited
                        )
                    comments.append(comment)
                    #endregion

                except Exception as e:
                    logging.exception(e, exc_info=True)
                #endregion
        
        except Exception as e:
            logging.exception(e, exc_info=True)

        #endregion





        #region get related articles list
        try:
            _related_article_candidates = self.browser.find_elements_by_xpath("//div[@class='single-entry-text bbtext']//p//a")
            
            for _related_article_candidate in _related_article_candidates:
                relatedArticle = self.RelatedArticles(article_id = current_article_id, related_article_text = clean_text(_related_article_candidate.get_attribute("innerText")), related_article_url = _related_article_candidate.get_attribute("href"))
                relatedArticles.append(relatedArticle)

        except Exception as e:
            logging.exception(e, exc_info=True)
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
                                    "article_number_of_likes" : article_number_of_likes,
                                    "article_number_of_images" : article_number_of_images,
                                    "article_has_slideshow" : article_has_slideshow,
                                    "article_has_video" : article_has_video,
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






    @timeit
    def get_single_article_content_basic_article_using_selenium_and_save_to_db(self, url : str, current_article_id):

        #region prepare variables
        article_title = None
        article_created_at = None
        article_author = None
        article_content = None
        article_number_of_comments = None
        article_number_of_likes = None
        article_number_of_images = None
        article_number_of_bolded_text = None
        article_has_slideshow = None
        article_has_video = False
        tags = []
        relatedArticles = []
        comments = []
        #endregion

        # go to the article url
        self.browser.get(url)

        #region accept website policy
        try:
            accept_policy = list([i for i in self.browser.find_elements_by_xpath("//button") if "p" in i.get_attribute("textContent").strip().lower()])[0]
            accept_policy.click()
        except Exception as e:
            #logging.exception(e, exc_info=True)
            pass
        #endregion
     
        #region get title
        try:
            _article_title = self.browser.find_element_by_xpath("//div[@class='single-entry__header' or @class='single-article-header' or contains(@class, 'show_result')]//h1")
            article_title = clean_text(str(_article_title.get_attribute("innerText")))
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion

        #region get author
        try:
            _article_author = self.browser.find_element_by_xpath("//div[@class='single-entry__footer' or @class='article__footer' or @class='slideshow__footer']//span[@class='author' or @class='article__author']").get_attribute("innerText")
            article_author = clean_text(str(_article_author))
        except Exception as e:
            #logging.exception(e, exc_info=True)
            pass
        #endregion

        #region get creation datetime
        try:
            _article_created_at = self.browser.find_elements_by_xpath("//head//meta[@property='og:published_at']")[0]
            article_created_at = parser.parse(_article_created_at.get_attribute("content"), "")
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion

        #region get number of comments        
        try:
            _article_number_of_comments_candidate = self.browser.find_elements_by_xpath("//head//meta[@property='og:comments_count']")[0]
            _article_number_of_comments = _article_number_of_comments_candidate.get_attribute("content")
            article_number_of_comments = int(clean_text(str(_article_number_of_comments)))
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion

        #region get number of facebook likes
        try:

            # find iframe with given name
            detailFrame = self.browser.find_element_by_xpath("//div[@class='single-entry__header']//iframe[@title='fb:like Facebook Social Plugin']")

            # open selected iframe
            self.browser.switch_to.frame(detailFrame)

            # the iframe code in this case is a bit "encrypted"
            # get all texts from all spans
            # try to parse each element
            # get the first one that contain number
            _article_number_of_likes_candidate = self.browser.find_element_by_xpath("//*")
            _article_number_of_likes = _article_number_of_likes_candidate.get_attribute("innerText") 
            article_number_of_likes = int(re.findall(r'\d+', _article_number_of_likes)[0])

            # switch to main window and main frame
            self.browser.switch_to.default_content()

        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion       

        #region get number of bolded texts
        try:
            _article_number_of_bolded_text = self.browser.find_elements_by_xpath("//div[@class='single-entry-text bbtext' or @class='single-article-text' or @class='article']//p")
            article_number_of_bolded_text = len(_article_number_of_bolded_text)
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion
 
        #region get number of images

        #region get number of images (article)
        _number_of_images = 0
        try:
            _number_of_images = len(self.browser.find_elements_by_xpath("//div[@class='single-entry-text bbtext' or @class='single-article-text' or @class='article']//img"))
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion

        #region get number of images (slideshow)
        article_has_slideshow = False
        _images_in_slideshow = 0
        try:
            _slideshow = self.browser.find_element_by_xpath("//div[@data-utm_campaign='slideshow']//span[@class='slideshow-current']")
            _images_in_slideshow = int(_slideshow.get_attribute("innerText").split("/")[1])
            article_has_slideshow = True
        except Exception as e:
            #logging.exception(e, exc_info=True)
            pass
        #endregion

        article_number_of_images = _number_of_images or 0 + _images_in_slideshow or 0
        #endregion    

        #region get article text
        try:
            
            all_article_texts = self.browser.find_elements_by_xpath("//div[@class='single-entry-text bbtext' or @class='single-article-text' or @class='article__text text-box' or @class='article']//p")
            _article_content = ""

            for text in all_article_texts:
                current_text = text.get_attribute("innerText")

                if (len(current_text) > 0):
                    _article_content += current_text + " "
            
            if len(_article_content) > 0:
                article_content = clean_text(_article_content)

        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion

        #region get tags        
        try:
            _tags = self.browser.find_elements_by_xpath("//div[@class='single-entry__header']//span[@class='inline-tags']//a")
            for _tag in _tags:
                tag = self.Tags(article_id = current_article_id, tag_text = clean_text(_tag.get_attribute("innerText")), tag_url = _tag.get_attribute("href"))
                tags.append(tag)
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion

        #region get comments
        try:
            _comments = self.browser.find_elements_by_xpath("//div[@class='comments-popular']//div[@class='comment']")
            
            for _comment in _comments:
                #region get single comment
                try:

                    #region get basic comment info
                    _comment_author = _comment.find_element_by_xpath(".//span[@class='comment-author']")
                    _comment_created_at = _comment.find_element_by_xpath(".//span[@class='comment-date']")
                    _comment_message = _comment.find_element_by_xpath(".//div[@class='comment-text']")
                    comment_message = clean_text(_comment_message.get_attribute("innerText"))
                    _comment_thumbs_up = _comment.find_element_by_xpath(".//span[@class='plus']")
                    _comment_thumbs_down = _comment.find_element_by_xpath(".//span[@class='minus']")
                    _comment_is_highlited = True
                    #endregion

                    #region get comment message
                    try:
                        _comment_message_quote = _comment.find_element_by_xpath(".//div[@class='comment-text']//blockquote")
                        _comment_message_quote = clean_text(_comment_message_quote.get_attribute("innerText"))
                        comment_message = clean_text(comment_message.replace(_comment_message_quote, ''))
                    except Exception as e:
                        #logging.exception(e, exc_info=True)
                        pass
                    #endregion
                       
                    #region add comment to list
                    comment = self.Comments(
                            article_id = current_article_id, 
                            comment_author = clean_text(_comment_author.get_attribute("innerText")),
                            comment_created_at = datetime.datetime.strptime(clean_text(_comment_created_at.get_attribute("innerText")), "%d %m %Y %H %M"),
                            comment_message = comment_message,
                            comment_thumbs_up = clean_text(_comment_thumbs_up.get_attribute("innerText")),
                            comment_thumbs_down = clean_text(_comment_thumbs_down.get_attribute("innerText")),
                            comment_is_highlited = _comment_is_highlited
                        )
                    comments.append(comment)
                    #endregion

                except Exception as e:
                    logging.exception(e, exc_info=True)
                #endregion

        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion

        #region get related articles list
        try:
            _related_article_candidates = self.browser.find_elements_by_xpath("//div[@class='single-entry-text bbtext']//p//a")
            
            for _related_article_candidate in _related_article_candidates:
                relatedArticle = self.RelatedArticles(article_id = current_article_id, related_article_text = clean_text(_related_article_candidate.get_attribute("innerText")), related_article_url = _related_article_candidate.get_attribute("href"))
                relatedArticles.append(relatedArticle)

        except Exception as e:
            logging.exception(e, exc_info=True)
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
                                    "article_number_of_likes" : article_number_of_likes,
                                    "article_number_of_images" : article_number_of_images,
                                    "article_has_slideshow" : article_has_slideshow,
                                    "article_has_video" : article_has_video,
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

   
    @timeit
    def get_single_article_content_basic_video_using_selenium_and_save_to_db(self, url : str, current_article_id):

        #region prepare variables
        article_title = None
        article_created_at = None
        article_author = None
        article_content = None
        article_number_of_comments = None
        article_number_of_likes = None
        article_number_of_images = None
        article_number_of_bolded_text = None
        article_has_slideshow = None
        article_has_video = True
        tags = []
        relatedArticles = []
        comments = []
        #endregion

        # go to the article url
        self.browser.get(url)

        #region accept website policy
        try:
            accept_policy = list([i for i in self.browser.find_elements_by_xpath("//button") if "p" in i.get_attribute("textContent").strip().lower()])[0]
            accept_policy.click()
        except Exception as e:
            pass
        #endregion

        #region get title
        try:
            _article_title = self.browser.find_element_by_xpath("//div[@class='single-entry__header' or @class='single-article-header' or contains(@class, 'show_result')]//h1")
            article_title = clean_text(str(_article_title.get_attribute("innerText")))
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion

        #region get author
        try:
            _article_author = self.browser.find_element_by_xpath("//div[@class='single-article-footer']//p[@class='single-article-author']").get_attribute("innerText")
            article_author = clean_text(str(_article_author))
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion

        #region get creation datetime
        try:            
            _article_created_at = self.browser.find_elements_by_xpath("//head//meta[@property='og:published_at']")[0]
            article_created_at = parser.parse(_article_created_at.get_attribute("content"), "")
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion

        #region get number of comments        
        try:
            _article_number_of_comments_candidate = self.browser.find_elements_by_xpath("//head//meta[@property='og:comments_count']")[0]
            _article_number_of_comments = _article_number_of_comments_candidate.get_attribute("content")
            article_number_of_comments = int(clean_text(str(_article_number_of_comments)))
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion

        #region get number of facebook likes
        try:

            # find iframe with given name
            detailFrame = self.browser.find_element_by_xpath("//div[@class='single-article-footer']//iframe[@title='fb:like Facebook Social Plugin']")

            # open selected iframe
            self.browser.switch_to.frame(detailFrame)

            # the iframe code in this case is a bit "encrypted"
            # get all texts from all spans
            # try to parse each element
            # get the first one that contain number
            _article_number_of_likes_candidate = self.browser.find_element_by_xpath("//*")
            _article_number_of_likes = _article_number_of_likes_candidate.get_attribute("innerText") 
            article_number_of_likes = int(re.findall(r'\d+', _article_number_of_likes)[0])

            # switch to main window and main frame
            self.browser.switch_to.default_content()

        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion

        #region get number of bolded texts
        try:
            _article_number_of_bolded_text = self.browser.find_elements_by_xpath("//div[@class='single-entry-text bbtext' or @class='single-article-text' or @class='article']//p")
            article_number_of_bolded_text = len(_article_number_of_bolded_text)
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion
 
        #region get number of images
        _number_of_images = 0
        try:
            _number_of_images = len(self.browser.find_elements_by_xpath("//div[@class='single-entry-text bbtext' or @class='single-article-text' or @class='article']//img"))
            _number_of_video_thumbs = len(self.browser.find_elements_by_xpath("//div[@class='article__video-wrap']//img"))
        except Exception as e:
            logging.exception(e, exc_info=True)

        article_has_slideshow = False
        article_number_of_images = (_number_of_images or 0) - (_number_of_video_thumbs or 0)
        #endregion
            
        #region get article text
        try:
            all_article_texts = self.browser.find_elements_by_xpath("//div[@class='single-entry-text bbtext' or @class='single-article-text' or @class='article__text text-box' or @class='article']//p")
            _article_content = ""

            for text in all_article_texts:
                current_text = text.get_attribute("innerText")

                if (len(current_text) > 0):
                    _article_content += current_text + " "
            
            if len(_article_content) > 0:
                article_content = clean_text(_article_content)

        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion
        
        #region get tags
        try:
            _tags = self.browser.find_elements_by_xpath("//div[@class='single-article']//p[@class='single-article-tags']//a")
            for _tag in _tags:
                tag = self.Tags(article_id = current_article_id, tag_text = clean_text(_tag.get_attribute("innerText")), tag_url = _tag.get_attribute("href"))
                tags.append(tag)
        except Exception as e:
            logging.exception(e, exc_info=True)
        #endregion

        #region get comments
        try:
            _comments = self.browser.find_elements_by_xpath("//div[@class='comments-popular']//div[@class='comment comment-even' or @class='comment comment-odd']")
            
            for _comment in _comments:
                #region get single comment                
                try:

                    #region get basic comment info
                    _comment_author = _comment.find_element_by_xpath(".//span[@class='comment-author']")
                    _comment_created_at = _comment.find_element_by_xpath(".//span[@class='comment-date']")
                    _comment_message = _comment.find_element_by_xpath(".//div[@class='comment-text']")
                    comment_message = clean_text(_comment_message.get_attribute("innerText"))
                    _comment_thumbs_up = _comment.find_element_by_xpath(".//a[@class='plus']")
                    _comment_thumbs_down = _comment.find_element_by_xpath(".//a[@class='minus']")
                    _comment_is_highlited = True
                    #endregion

                    #region get comment message
                    try:
                        _comment_message_quote = _comment.find_element_by_xpath(".//div[@class='comment-text']//blockquote")
                        _comment_message_quote = clean_text(_comment_message_quote.get_attribute("innerText"))
                        comment_message = clean_text(comment_message.replace(_comment_message_quote, ''))
                    except Exception as e:
                        #logging.exception(e, exc_info=True)
                        pass
                    #endregion
                       
                    #region add comment to list
                    comment = self.Comments(
                            article_id = current_article_id, 
                            comment_author = clean_text(_comment_author.get_attribute("innerText")),
                            comment_created_at = datetime.datetime.strptime(clean_text(_comment_created_at.get_attribute("innerText")), "%d %m %Y %H %M"),
                            comment_message = comment_message,
                            comment_thumbs_up = clean_text(_comment_thumbs_up.get_attribute("innerText")),
                            comment_thumbs_down = clean_text(_comment_thumbs_down.get_attribute("innerText")),
                            comment_is_highlited = _comment_is_highlited
                        )
                    comments.append(comment)
                    #endregion

                except Exception as e:
                    logging.exception(e, exc_info=True)
                    
                #endregion
        except Exception as e:
            logging.exception(e, exc_info=True)
            
        #endregion

        #region get related articles list
        try:
            _related_article_candidates = self.browser.find_elements_by_xpath("//div[@class='single-entry-text bbtext']//p//a")
            
            for _related_article_candidate in _related_article_candidates:
                relatedArticle = self.RelatedArticles(article_id = current_article_id, related_article_text = clean_text(_related_article_candidate.get_attribute("innerText")), related_article_url = _related_article_candidate.get_attribute("href"))
                relatedArticles.append(relatedArticle)

        except Exception as e:
            logging.exception(e, exc_info=True)
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
                                    "article_number_of_likes" : article_number_of_likes,
                                    "article_number_of_images" : article_number_of_images,
                                    "article_has_slideshow" : article_has_slideshow,
                                    "article_has_video" : article_has_video,
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
       

