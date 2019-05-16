using System;
using PudelekParser;
using CommandLine;
using log4net;

namespace ConsoleApp
{
    class Program
    {
        
        public class Options
        {
            #region prepare arguments
            [Option("log_file_path", Required = false, HelpText = "path to log file", Default = "myapp.log")]
            public string log_path { get; set; }
            [Option("selenium_driver_path", Required = false, HelpText = "path to selenium executable file", Default = @"E:\Tools\selenium_drivers\chromedriver.exe")]
            public string selenium_driver_path { get; set; }
            [Option("db_connectionstring", Required = false, HelpText = "database connection string", Default = @"Server=XX.XX.XX.XX;Database=PudelekCopy;;User Id=sa;Password=XX;")]
            public string db_connectionstring { get; set; }
            [Option("run_type", Required = false, HelpText = "type of run, [al] - articles list, [ad] - articles details", Default = "ad")]
            public string run_type { get; set; }
            [Option("al_start_page", Required = false, HelpText = "start page to get list of articles", Default = 5)]
            public int al_start_page { get; set; }
            [Option("al_no_pages", Required = false, HelpText = "number of pages to get list of articles", Default = 5)]
            public int al_no_pages { get; set; }
            [Option("ad_no_pages", Required = false, HelpText = "number of pages to get articles details", Default = 50)]
            public int ad_no_pages { get; set; }
            #endregion
        }

        private static readonly ILog Log = LogManager.GetLogger(typeof(Program));

        static void Main(string[] args)
        {

            #region handle arguments
            string log_file_path = null;
            string selenium_driver_path = null;
            string db_connectionstring = null;
            string run_type = null;
            int? al_start_page = null;
            int? al_no_pages = null;
            int? ad_no_pages = null;

            Parser.Default.ParseArguments<Options>(args)
                   .WithParsed<Options>(o =>
                   {
                       log_file_path = o.log_path;
                       selenium_driver_path = o.selenium_driver_path;
                       db_connectionstring = o.db_connectionstring;
                       run_type = o.run_type;
                       al_start_page = o.al_start_page;
                       al_no_pages = o.al_no_pages;
                       ad_no_pages = o.ad_no_pages;
                   });
            #endregion


            #region initialize pudelek parser toolkit

            PudelekParserToolkit toolkit = new PudelekParserToolkit(log_file_path, db_connectionstring, selenium_driver_path);
            if (run_type == "al")
            {
                toolkit.get_articles_urls_and_save_to_db(Convert.ToInt32(al_no_pages), Convert.ToInt32(al_start_page));
            }
            else if (run_type == "ad")
            {
                toolkit.get_articles_content_using_selenium_and_save_to_db(Convert.ToInt32(ad_no_pages));
            }
            else
            {
                throw new NotImplementedException();
            }

            #endregion

            Console.WriteLine("DONE");
        }
    }
}
