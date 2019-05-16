using System;
using HtmlAgilityPack;
namespace SampleDotNet
{
    class Program
    {
        static void Main(string[] args)
        {
            var url = "https://www.alexa.com/topsites/countries/PL";
            var web = new HtmlWeb();
            var doc = web.Load(url);

            var all_websites = doc.DocumentNode.SelectNodes("//div[@class='tr site-listing']");

            foreach (HtmlNode webiste in all_websites)
            {
                // get
                var ranking_no = webiste.SelectNodes(".//div[@class='td']")[0].InnerText;
                var website_url = webiste.SelectNodes(".//div[@class='td DescriptionCell']//p")[0].InnerText;
                var daily_time_on_site = webiste.SelectNodes(".//div[@class='td right']")[0].InnerText;
                var daily_pageviews_per_visitor = webiste.SelectNodes(".//div[@class='td right']")[1].InnerText;
                var percent_of_traffic_from_search = webiste.SelectNodes(".//div[@class='td right']")[2].InnerText;
                var total_sites_linking_in = webiste.SelectNodes(".//div[@class='td right']")[3].InnerText;


                //transform
                website_url = website_url.Trim();
                ranking_no = ranking_no.Trim();
                daily_time_on_site = daily_time_on_site.Trim();
                daily_pageviews_per_visitor = daily_pageviews_per_visitor.Trim();
                percent_of_traffic_from_search = percent_of_traffic_from_search.Trim();
                total_sites_linking_in = total_sites_linking_in.Trim();

                Console.WriteLine("{0}  {1}  {2}  {3}  {4}", 
                            website_url, 
                            ranking_no.ToString(), 
                            daily_time_on_site, 
                            daily_pageviews_per_visitor, 
                            percent_of_traffic_from_search, 
                            total_sites_linking_in
                            );

            }

            Console.ReadKey();
        }
    }
}
