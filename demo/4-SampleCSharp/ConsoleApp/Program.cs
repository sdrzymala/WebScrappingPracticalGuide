using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using WebScrapingPudelekPL;

namespace ConsoleApp
{
    class Program
    {
        static void Main(string[] args)
        {

            //// GetArticlesUrlsAndSaveToDB
            //int numberOfPagesToParse = 1000;
            //int startPageNumber = 499;
            //PudelekParser.GetArticlesUrlsAndSaveToDB(numberOfPagesToParse, startPageNumber);


            // GetArticlesUrlsAndSaveToDB
            //int numberOfArticlesToDownload = 1;
            //PudelekParser.GetArticleContentAndSaveToDB(numberOfArticlesToDownload);

            //PudelekParser.GetSingleArticleContentUsingSeleniumAndSaveToDB("https://www.pudelek.pl/artykul/136444/21-letnia_modelka_zlapala_leonardo_dicaprio_na_pierogi/");
            int numberOfArticlesDetailsToDownload = 1;
            int numberOfPagesForCommentsToDownload = 1;
            PudelekParser.GetArticlesContentUsingSeleniumAndSaveToDB(numberOfArticlesDetailsToDownload, numberOfPagesForCommentsToDownload);

            Console.WriteLine("Done");
            Console.ReadKey();
        }

    }
}
