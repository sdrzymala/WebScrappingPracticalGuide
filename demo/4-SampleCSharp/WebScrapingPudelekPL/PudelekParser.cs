using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using HtmlAgilityPack;
using WebScrapingPudelekPL.Classes;
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using System.Threading;
using OpenQA.Selenium.Support.UI;
using System.Text.RegularExpressions;
using System.Timers;

namespace WebScrapingPudelekPL
{
    public class PudelekParser
    {
        const string base_url = @"https://www.pudelek.pl/artykuly/";
        const string chrome_driver_path = @"E:\Tools\selenium_drivers\";

        public static void GetArticlesUrlsAndSaveToDB(int numberOfPagesToParse, int startPageNumber)
        {
            using (var context = new ArticlesContext())
            {
                var current_articles_urls = context.Articles;

                for (int i = startPageNumber; i <= numberOfPagesToParse; i++)
                {
                    string current_url = base_url + i + "/";
                    var web = new HtmlWeb();
                    var doc = web.Load(current_url);

                    var articles = doc.DocumentNode
                                        .SelectNodes("//div[@class='news-all']//div[@class='results__entry ' or @class='results__entry results__entry--pudelekx']//h3[@class='entry__title']//a")
                                        .Select(x => new Article()
                                            {
                                                Url = x.Attributes["href"].Value,
                                                IsDownloaded = false,
                                                InsertedAt = DateTime.UtcNow
                                            })
                                        .Where(x => !current_articles_urls.Any(y => x.Url == y.Url))
                                        .ToList()
                                        .Where( x => x.Url.ToLower().StartsWith("https://www.pudelek.pl"));

                    context.Articles.AddRange(articles);
                    context.SaveChanges();
                }
            }
        }

        public static void GetArticlesContentUsingSeleniumAndSaveToDB(int numberOfArticlesToDownload, int numberOfPagesForCommentsToDownload)
        {
            using (var context = new ArticlesContext())
            {
                var articles_to_download = context.Articles.Where(x => x.IsDownloaded == false).Take(numberOfArticlesToDownload);

                foreach (var article in articles_to_download)
                {
                    GetSingleArticleContentUsingSeleniumAndSaveToDB(article.Url, numberOfPagesForCommentsToDownload);
                }
            }
        }

        public static void GetSingleArticleContentUsingSeleniumAndSaveToDB(string url, int numberOfPagesForCommentsToDownload)
        {
            

            string title = null;
            DateTime? createdAt = null;
            string author = null;
            string content = null;
            int? numberOfComments = null;
            int? numberOfLikes = null;
            List<Tag> tags = new List<Tag>();
            List<RelatedArticle> relatedArticles = new List<RelatedArticle>();
            List<Comment> comments = new List<Comment>();
       

           
            // initialize 
            var chromeOptions = new ChromeOptions();
            chromeOptions.AddArguments("headless");
            //chromeOptions.SetLoggingPreference(LogType.Browser, LogLevel.Severe);
            IWebDriver driver = new ChromeDriver(chrome_driver_path, chromeOptions);
            driver.Url = url;



            #region accept policy !!! (show)

            // accept policy
            try
            {
                var accept_site_policy = driver
                            .FindElements(By.XPath("//button"))
                            .Where(x => x.Text.ToLower().Contains("przechodzę do serwisu"))
                            .First()
                            ;

                accept_site_policy.Click();
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }

            #endregion




            #region title !!! (show)

            try
            {
                var _title = driver.FindElements(By.XPath("//div[@class='single-entry__header' or @class='single-article-header']//h1"))
                                                        .First()
                                                        .Text;

                title = HelperMethods.CleanText(_title);
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }

            #endregion



            #region created at

            try
            {

                var _createdAt = driver.FindElements(By.XPath("//div[@class='single-entry__header' or @class='single-article-header']//span[@class='time']"))
                                    .First()
                                    .GetAttribute("datetime");

                createdAt = Convert.ToDateTime(_createdAt);

            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }

            #endregion




            #region author !!! (show)

            try
            {
                // see, sometimes text will not return text, and we need to use innertext
                var _author = driver.FindElements(By.XPath("//div[@class='single-entry__footer' or @class='slideshow__footer']//span[@class='author']"))
                                        .First()
                                        .GetAttribute("innerText");

                author = HelperMethods.CleanText(_author);
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }

            #endregion




            #region get facebook likes number !!! (show)

            try
            {
                // find iframe with given name
                var detailFrame = driver.FindElement(By.XPath("//div[@class='single-entry__header']//iframe[@title='fb:like Facebook Social Plugin']"));

                // open selected iframe
                driver.SwitchTo().Frame(detailFrame);

                // the iframe code in this case is a bit "encrypted"
                // get all texts from all spans
                // try to parse each element
                // get the first one that contain number
                numberOfLikes = driver.FindElements(By.XPath("//span"))
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
                driver.SwitchTo().DefaultContent();

            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }
            #endregion



            #region number of comments 

            try
            {
                numberOfComments = driver.FindElements(By.XPath("//div[@class='single-entry__footer' or @class='slideshow__footer']//a[@class='comments-link']"))
                                                    .First()
                                                    .GetAttribute("innerText")
                                                    .Split(' ')
                                                    .Select(x =>
                                                    {
                                                        int value;
                                                        string old_value = x;
                                                        bool success = int.TryParse(x, out value);
                                                        return new { value, old_value, success };
                                                    })
                                                    .Where(y => y.success == true)
                                                    .Select(z => z.value)
                                                    .First();
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }


            #endregion


            

            #region tags
            try
            {
                var _tags = driver.FindElements(By.XPath("//div[@class='single-entry__header']//span[@class='inline-tags']//a"));

                foreach (var _tag in _tags)
                {
                    Tag tag = new Tag();
                    tag.Text = HelperMethods.CleanText(_tag.Text);
                    tag.Url = _tag.GetAttribute("href");
                    tags.Add(tag);
                }
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }
            #endregion

            


            #region related articles

            try
            {

                var _related_article_candidates = driver.FindElements(By.XPath("//div[@class='single-entry-text bbtext']//p//a"));

                foreach (var _related_article_candidate in _related_article_candidates)
                {
                    RelatedArticle relatedArticle = new RelatedArticle();
                    relatedArticle.Text = HelperMethods.CleanText(_related_article_candidate.Text);
                    relatedArticle.Url = _related_article_candidate.GetAttribute("href");
                    relatedArticles.Add(relatedArticle);
                }



            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }

            #endregion



            #region article text

            try
            {

                var all_article_texts = driver.FindElements(By.XPath("//div[@class='single-entry-text bbtext' or @class='single-article-text']//p"));

                string _content = "";

                foreach (var text in all_article_texts)
                {
                    string current_text = text.GetAttribute("innerText");

                    if (current_text.Length > 0)
                    {
                        _content += current_text + " ";
                    }
                }

                if (_content.Length > 0)
                {
                    content = HelperMethods.CleanText(_content);
                }
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.Message);
            }

            #endregion


            

            #region comments 

            // parse comments
            int comments_website_subpage_number = 1;
            List<Comment> current_website_popular_comments = new List<Comment>();
            while (comments_website_subpage_number <= numberOfPagesForCommentsToDownload)
            {

                string current_comments_website_subpage = url + "/" + comments_website_subpage_number.ToString() +  "/#comments";
                driver.Url = current_comments_website_subpage;
                var current_subpage_comments = driver.FindElements(By.XPath("//div[@class='comment comment-odd' or @class='comment comment-even']"));

                // ger the popular comments only onces
                if (comments_website_subpage_number == 1)
                {
                    // get higlither / most popular comments
                    var current_subpage_popular_comments = driver.FindElements(By.XPath("//div[@class='comments-popular']//div[@class='comment']"));
                    foreach (var current_popular_comment in current_subpage_popular_comments)
                    {
                        string popularCommentAuthor = null;
                        string popularCommentMessage = null;

                        try
                        {
                            popularCommentAuthor = HelperMethods.CleanText(current_popular_comment.FindElements(By.XPath(".//span[@class='comment-author']")).First().Text);
                        }
                        catch (Exception exc)
                        {
                            Console.WriteLine(exc.Message);
                        }

                        try
                        {
                            popularCommentMessage = HelperMethods.CleanText(current_popular_comment.FindElements(By.XPath(".//div[@class='comment-text']")).First().Text);
                        }
                        catch (Exception exc)
                        {
                            Console.WriteLine(exc.Message);
                        }


                        var popular_comment = new Comment();
                        popular_comment.Author = popularCommentAuthor;
                        popular_comment.Message = popularCommentMessage;
                        current_website_popular_comments.Add(popular_comment);

                    }
                }

                // break if there is no comments
                if (current_subpage_comments.Count() == 0)
                {
                    break;
                }
                else
                {
                    foreach (var current_subpage_comment in current_subpage_comments)
                    {
                        string commentAuthor = null;
                        DateTime? commentCreatedAt = null;
                        bool? commentIsHighlited = null;
                        string commentMessage = null;
                        int? commentThumbsDown = null;
                        int? commentThumbsUp = null;

                        try
                        {
                            commentAuthor = HelperMethods.CleanText(current_subpage_comment.FindElements(By.XPath(".//span[@class='comment-author']")).First().Text);
                        }
                        catch (Exception exc)
                        {
                            Console.WriteLine(exc.Message);
                        }

                        try
                        {
                            commentCreatedAt = Convert.ToDateTime(current_subpage_comment.FindElements(By.XPath(".//span[@class='comment-date']")).First().Text);
                        }
                        catch (Exception exc)
                        {
                            Console.WriteLine(exc.Message);
                        }

                        try
                        {
                            commentThumbsUp = Convert.ToInt32(current_subpage_comment.FindElements(By.XPath(".//div[@class='comment-vote']//span[@class='plus']")).First().Text);
                        }
                        catch (Exception exc)
                        {
                            Console.WriteLine(exc.Message);
                        }

                        try
                        {
                            commentThumbsDown = Convert.ToInt32(current_subpage_comment.FindElements(By.XPath(".//div[@class='comment-vote']//span[@class='minus']")).First().Text);
                        }
                        catch (Exception exc)
                        {
                            Console.WriteLine(exc.Message);
                        }

                        try
                        {
                            commentMessage = HelperMethods.CleanText(current_subpage_comment.FindElements(By.XPath(".//div[@class='comment-text']")).First().Text);
                        }
                        catch (Exception exc)
                        {
                            Console.WriteLine(exc.Message);
                        }

                        try
                        {
                            if (current_website_popular_comments.Where(x=> x.Author == commentAuthor && x.Message == commentMessage).Count() > 0)
                            {
                                commentIsHighlited = true;
                            }
                            else
                            {
                                commentIsHighlited = false;
                            }
                        }
                        catch (Exception exc)
                        {
                            Console.WriteLine(exc.Message);
                        }



                        Comment comment = new Comment();
                        comment.Author = commentAuthor;
                        comment.CreatedAt = commentCreatedAt;
                        comment.IsHighlited = commentIsHighlited;
                        comment.Message = commentMessage;
                        comment.ThumbsDown = commentThumbsDown;
                        comment.ThumbsUp = commentThumbsUp;
                        comments.Add(comment);
                    }

                    
                }

                comments_website_subpage_number++;
            }


            #endregion


            


            #region extras !!!


            // wait
            //driver.Manage().Timeouts().ImplicitWait = TimeSpan.FromSeconds(5);
            //var wait = new WebDriverWait(driver, TimeSpan.FromSeconds(3));

            // wait for element
            //var wait = new WebDriverWait(driver, TimeSpan.FromSeconds(timeOut)).Until(ExpectedConditions.ElementExists((By.Id(login))));

            // wait rundom number of seconds...
            //var rnd = new Random();
            //var delay = rnd.Next(5000, 10001);
            //Thread.Sleep(delay);

            #endregion

            

            // clean up the driver
            driver.Quit();


            #region db operations 

            // save results to database
            using (var context = new ArticlesContext())
            {
                var current_article = context.Articles.Where(x => x.Url == url).First();

                current_article.Title = title;
                current_article.CreatedAt = createdAt;
                current_article.Author = author;
                current_article.Content = content;
                current_article.NumberOfComments = numberOfComments;
                current_article.NumberOfLikes = numberOfLikes;
                current_article.IsDownloaded = true;
                current_article.UpdatedAt = DateTime.UtcNow;

                current_article.Tags.AddRange(tags.Where(x => !current_article.Tags.Any(y => y.Text == x.Text)));
                current_article.RelatedArticles.AddRange(relatedArticles.Where(x => !current_article.RelatedArticles.Any(y => y.Text == x.Text)));
                current_article.Comments.AddRange(comments.Where(x => !current_article.Comments.Any(y => y.Author == x.Author && y.Message == x.Message && x.CreatedAt == y.CreatedAt)));
                
                context.SaveChanges();
            }

            #endregion

        }
    }
}
