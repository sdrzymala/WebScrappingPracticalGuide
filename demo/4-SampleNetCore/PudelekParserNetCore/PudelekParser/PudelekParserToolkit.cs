using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using PostSharp.Aspects;
using System;
using System.Collections.Generic;
using System.Linq;
using WebScrapingPudelekPL.Classes;
using PostSharp.Patterns.Diagnostics;
using log4net.Config;
using PostSharp.Patterns.Diagnostics;
using PostSharp.Patterns.Diagnostics.Backends.Log4Net;
using System.IO;
using log4net;
using System.Reflection;
using System.Threading;

namespace PudelekParser
{
    [Log(AttributeExclude = false)]
    public class PudelekParserToolkit
    {
        const string base_url = @"https://www.pudelek.pl/artykuly/";
        const string chrome_driver_path = @"E:\Tools\selenium_drivers\";
        public IWebDriver browser { get; set; }
        public int MyProperty { get; set; }
        private static readonly ILog Log = LogManager.GetLogger(typeof(PudelekParser.PudelekParserToolkit));

        public PudelekParserToolkit(string log_file_path, string db_connectionstring, string selenium_driver_path)
        {
           

            #region configure selenium
            var chrome_options = new ChromeOptions();
            chrome_options.AddArguments("headless");

            chrome_options.AddArguments("--headless");
            chrome_options.AddArguments("--disable-gpu");
            chrome_options.AddArguments("--no-sandbox");
            chrome_options.AddArguments("--disable-extensions");
            chrome_options.AddArguments("--log-level=2");
            chrome_options.AddArguments("start-maximized");
            chrome_options.AddArguments("disable-infobars");
            chrome_options.AddArguments("--disable-dev-shm-usage");
            chrome_options.AddArguments("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36");
            //browser = webdriver.Chrome(chrome_driver_path) // to run without headless mode
            browser = new ChromeDriver(chrome_driver_path, chrome_options);
            browser.Manage().Timeouts().PageLoad = TimeSpan.FromSeconds(180);
            IJavaScriptExecutor js = (IJavaScriptExecutor)browser;
            js.ExecuteScript("document.body.style.zoom='100'");
            this.browser.Manage().Window.Size = new System.Drawing.Size(1366, 768);
            this.browser.Manage().Window.Maximize();
            Thread.Sleep(5); // let him initialize...
            #endregion

        }

        
        public void get_articles_urls_and_save_to_db(int al_no_pages, int al_start_page)
        {

            foreach (int i in Enumerable.Range(al_start_page, al_start_page + al_no_pages + 1))
            {
                List<Article> articles = new List<Article>();

                #region get article urls
                try
                {
                    string current_url = base_url + i.ToString() + "/";

                    browser.Url = current_url;
                    browser.Navigate();

                    var _articles = browser.FindElements(By.XPath("//div[@class='news-all']//div[@class='results__entry ' or @class='results__entry results__entry--pudelekx']//h3[@class='entry__title']//a"));
                    foreach (var article in _articles)
                    {
                        string current_article_url = article.GetAttribute("href");
                        string article_type = "inny";

                        if (current_article_url.ToLower().StartsWith("https://www.pudelek.pl/artykul/"))
                        {
                            article_type = "artykul";
                        }
                        else if (current_article_url.ToLower().StartsWith("https://tv.pudelek.pl/video/"))
                        {
                            article_type = "video";
                        }
                        else if (current_article_url.ToLower().StartsWith("http://pudelekx.pl/"))
                        {
                            article_type = "x";
                        }

                        
                        #region save article details to database
                        try
                        {
                            // save basic article details to database
                            using (var context = new ArticlesContext())
                            {
                                Article current_article = new Article();
                                current_article.article_url = current_article_url;
                                current_article.article_type = article_type;
                                current_article.article_is_downloaded = false;
                                current_article.article_updated_at = DateTime.Now;
                                context.Add(current_article);
                                context.SaveChanges();
                            }
                        }
                        catch (Exception exc)
                        {
                            Console.WriteLine(exc.Message);
                        }
                        #endregion


                    }

                }
                catch (Exception exc)
                {
                    Console.WriteLine(exc.Message);
                }
                #endregion

            }

            browser.Dispose();

        }
        
        public void get_articles_content_using_selenium_and_save_to_db(int numberOfArticlesToDownload)
        {
            var a = 1;
            using (var context = new ArticlesContext())
            {
                var articles_to_download = context.Articles.Where(x => x.article_is_downloaded == false).Take(numberOfArticlesToDownload);

                foreach (var article in articles_to_download)
                {
                    if (article.article_type == "artykul")
                    {
                        get_single_article_content_basic_article_using_selenium_and_save_to_db(article.article_url, article.article_id);
                    }
                    else if (article.article_type == "video")
                    {
                        //throw new NotImplementedException();
                        //get_single_article_content_basic_video_using_selenium_and_save_to_db(article.article_url, article.article_id);
                    }
                    else if (article.article_type == "x")
                    {
                        //throw new NotImplementedException();
                        //get_single_article_content_basic_x_using_selenium_and_save_to_db(article.article_url, article.article_id);
                    }
                    else
                    {
                        throw new Exception("Incorrect article type");
                    }
                }
            }
        }

       
        public void get_single_article_content_basic_article_using_selenium_and_save_to_db(string url, int current_article_id)
        {

            #region prepare variables
            string article_title = null;
            DateTime? article_created_at = null;
            string article_author = null;
            string article_content = null;
            int? article_number_of_comments = null;
            int? article_number_of_likes = null;
            int? article_number_of_images = null;
            int? article_number_of_bolded_text = null;
            bool? article_has_slideshow = null;
            bool? article_has_video = null;
            var tags = new List<Tag>();
            var relatedArticles = new List<RelatedArticle>();
            var comments = new List<Comment>();
            #endregion


            // go to the artile url
            browser.Url = url;
            browser.Navigate();


            #region accept webiste policy
            try
            {
                var accept_site_policy = browser
                            .FindElements(By.XPath("//button"))
                            .Where(x => x.Text.ToLower().Contains("przechodzę do serwisu"))
                            .First()
                            ;

                accept_site_policy.Click();
            }
            catch(Exception exc)
            {
                Console.WriteLine(exc.Message);
            }
            #endregion


            #region get title
            try
            {
                var _article_title = browser.FindElement(By.XPath("//div[@id='item']//h1[@class='item-title']"));
                article_title = HelperMethods.CleanText(_article_title.GetAttribute("innerText").ToString());
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }
            #endregion


            #region get author
            try
            {
                var _article_author = browser.FindElement(By.XPath("//div[@class='item-details']//a"));
                article_author = HelperMethods.CleanText(_article_author.GetAttribute("innerText").ToString());
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }
            #endregion


            #region get creation datetime
            try
            {
                var _article_created_at = browser.FindElement(By.XPath("//head//meta[@property='og:published_at']"));
                article_created_at = Convert.ToDateTime(_article_created_at.GetAttribute("content").ToString());
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }
            #endregion


            #region get number of comments
            try
            {
                var _article_number_of_comments_candidate = browser.FindElement(By.XPath("//head//meta[@property='og:comments_count']"));
                var _article_number_of_comments = _article_number_of_comments_candidate.GetAttribute("content");
                article_number_of_comments = Convert.ToInt32(HelperMethods.CleanText(_article_number_of_comments.ToString()));
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }
            #endregion


            #region get number of facebook likes
            try
            {
                // find iframe with given name
                var detailFrame = browser.FindElement(By.XPath("//div[@class='single-entry__header']//iframe[@title='fb:like Facebook Social Plugin']"));

                // open selected iframe
                browser.SwitchTo().Frame(detailFrame);

                // the iframe code in this case is a bit "encrypted"
                // get all texts from all spans
                // try to parse each element
                // get the first one that contain number
                article_number_of_likes = browser.FindElements(By.XPath("//span"))
                                            .Select(x =>
                                            {
                                                int value;
                                                string old_value = x.Text;
                                                bool success = int.TryParse(x.Text, out value);
                                                return new { value, old_value, success };
                                            })
                                            .Where(y => y.success == true)
                                            .Select(z => z.value)
                                            .First()
                                            ;

                // switch to main window and main frame
                browser.SwitchTo().DefaultContent();

            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }
            #endregion


            #region get number of bolded texts
            try
            {
                var _article_number_of_bolded_text = browser.FindElement(By.XPath("//div[@class='single-entry-text bbtext' or @class='single-article-text' or @class='article']//p"));
                article_number_of_bolded_text = _article_number_of_bolded_text.ToString().Length;
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }
            #endregion


            #region get number of images

            #region get number of images (article content)
            int? _number_of_images = 0;
            try
            {
                _number_of_images = Convert.ToInt32(browser.FindElement(By.XPath("//div[@class='image-container']//img")).ToString());
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }
            #endregion

            #region get number of images (slideshow)
            article_has_slideshow = false;
            int? _images_in_slideshow = 0;
            try
            {
                var _slideshow = browser.FindElement(By.XPath("//div[@data-utm_campaign='slideshow']//span[@class='slideshow-current']"));
                _images_in_slideshow = Convert.ToInt32(_slideshow.GetAttribute("innerText").ToString().Split("/")[1]);
                article_has_slideshow = true;
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }
            #endregion

            // total number of images in website
            article_number_of_images = (_number_of_images ?? 0) + (_images_in_slideshow ?? 0);
            #endregion


            #region get article text
            try
            {
                var all_article_texts = browser.FindElements(By.XPath("//div[@class='item-content']//h2[@class='item-description']"));
                var _article_content = "";

                foreach(var text in all_article_texts)
                {
                    var current_text = text.GetAttribute("innerText").ToString();
                    if (current_text.Length > 0)
                    {
                        _article_content += current_text + " ";
                    }
                }

                if (_article_content.Length > 0)
                {
                    article_content = HelperMethods.CleanText(_article_content);
                }
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }
            #endregion


            #region get tags
            try
            {
                var _tags = browser.FindElements(By.XPath("//div[@class='item-content']//div[@class='tags']//a"));

                foreach(var _tag in _tags)
                {
                    var tag = new Tag(){  article_id = current_article_id, tag_text = HelperMethods.CleanText(_tag.GetAttribute("innerText")), tag_url = HelperMethods.CleanText(_tag.GetAttribute("href")) };
                    tags.Add(tag);
                }
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }
            #endregion
            

            #region get comments
            try
            {
                var _comments = browser.FindElements(By.XPath("//div[@class='comments-top']//div[@class='comment']"));

                foreach (var _comment in _comments)
                {
                    #region get single comment
                    try
                    {
                        #region get basic comment info
                        var _comment_author = _comment.FindElement(By.XPath(".//span[@class='comment-author']"));
                        var _comment_created_at = _comment.FindElement(By.XPath(".//span[@class='comment-date']"));
                        var comment_message = HelperMethods.CleanText(_comment.GetAttribute("innerText"));
                        var _comment_thumbs_up = _comment.FindElement(By.XPath(".//span[@class='yesCount']"));
                        var _comment_thumbs_down = _comment.FindElement(By.XPath(".//span[@class='noCount']"));
                        var _comment_is_highlited = true;
                        #endregion


                        #region get comment message
                        // get entire comment message
                        try
                        {
                            var _comment_info = _comment.FindElement(By.XPath(".//div[@class='comment-info']"));
                            var comment_info = HelperMethods.CleanText(_comment_info.GetAttribute("innerText").ToString());
                            comment_message = HelperMethods.CleanText(comment_message.Replace(comment_info, ""));
                        }
                        catch (Exception exc)
                        {
                            Console.WriteLine(exc.Message);
                        }
                        

                        // remove any comment info from message
                        try
                        {
                            var _comment_options = _comment.FindElement(By.XPath(".//div[@class='comment-options']"));
                            var comment_options = HelperMethods.CleanText(_comment_options.GetAttribute("innerText")).ToString();
                            comment_message = HelperMethods.CleanText(comment_message.Replace(comment_options, ""));
                        }
                        catch (Exception exc)
                        {
                            Console.WriteLine(exc.Message);
                        }

                        
                        // remove any quotes from comment message
                        try
                        {
                            var _comment_message_quote = _comment.FindElement(By.XPath(".//div[@class='quote']"));
                            var comment_message_quote = HelperMethods.CleanText(_comment_message_quote.GetAttribute("innerText"));
                            comment_message = HelperMethods.CleanText(comment_message.Replace(comment_message_quote, ""));
                        }
                        catch (Exception exc)
                        {
                            Console.WriteLine(exc.Message);
                        }


                        #endregion

                        
                        #region add comment to list   
                        var comment = new Comment()
                        {
                            article_id = current_article_id,
                            comment_author = HelperMethods.CleanText(_comment_author.GetAttribute("innerText")),
                            comment_created_at = Convert.ToDateTime(HelperMethods.CleanText(_comment_created_at.GetAttribute("innerText"))),
                            comment_message = comment_message,
                            comment_thumbs_up = Convert.ToInt32(HelperMethods.CleanText(_comment_thumbs_up.GetAttribute("innerText"))),
                            comment_thumbs_down = Convert.ToInt32(HelperMethods.CleanText(_comment_thumbs_down.GetAttribute("innerText"))),
                            comment_is_highlited = _comment_is_highlited
                        };

                        comments.Add(comment);
                        #endregion


                    }
                    catch (Exception exc)
                    {
                        Console.WriteLine(exc.Message);
                    }
                    #endregion
                }
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }

            
            #endregion

            
            #region get related articles list
            try
            {
                var _related_article_candidates = browser.FindElements(By.XPath("//div[@class='single-entry-text bbtext']//p//a"));
                foreach (var _related_article_candidate in _related_article_candidates)
                {
                    var relatedArticle = new RelatedArticle()
                    {
                        article_id = current_article_id,
                        related_article_text = HelperMethods.CleanText(_related_article_candidate.GetAttribute("innerText")),
                        related_article_url = _related_article_candidate.GetAttribute("href")
                    };
                    relatedArticles.Add(relatedArticle);
                }
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }
            #endregion

            
            #region save article details to database
            try
            {
                // save basic article details to database
                using (var context = new ArticlesContext())
                {
                    var current_article = context.Articles.Where(x => x.article_url == url).First();

                    current_article.article_title = article_title;
                    current_article.article_created_at = article_created_at;
                    current_article.article_author = article_author;
                    current_article.article_content = article_content;
                    current_article.article_number_of_comments = article_number_of_comments;
                    current_article.article_number_of_likes = article_number_of_likes;
                    current_article.article_number_of_images = article_number_of_images;
                    current_article.article_has_slideshow = article_has_slideshow;
                    current_article.article_has_video = article_has_video;
                    current_article.article_number_of_bolded_text = article_number_of_bolded_text;
                    current_article.article_is_downloaded = true;
                    current_article.article_updated_at = DateTime.Now;

                    current_article.Tags.AddRange(tags.Where(x => !current_article.Tags.Any(y => y.tag_text == x.tag_text)));
                    current_article.RelatedArticles.AddRange(relatedArticles.Where(x => !current_article.RelatedArticles.Any(y => y.related_article_text == x.related_article_text)));
                    current_article.Comments.AddRange(comments.Where(x => !current_article.Comments.Any(y => y.comment_author == x.comment_author && y.comment_message == x.comment_message && x.comment_created_at == y.comment_created_at)));

                    context.SaveChanges();
                }

                
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }
            #endregion

            
        }

        }
}
