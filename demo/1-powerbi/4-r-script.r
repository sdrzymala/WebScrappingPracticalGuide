#install.packages("rvest")

library(rvest)

url <- "https://www.alexa.com/topsites/countries/PL"


ranking_no <- url %>%
  read_html() %>%
  html_nodes(xpath='//div[@class="tr site-listing"]//div[@class="td"]') %>%
  html_text()

website_url <- url %>%
  read_html() %>%
  html_nodes(xpath='//div[@class="tr site-listing"]//div[@class="td DescriptionCell"]//p') %>%
  html_text()

daily_time_on_site <- url %>%
  read_html() %>%
  html_nodes(xpath='//div[@class="tr site-listing"]//div[@class="td right"][1]//p') %>%
  html_text() 

daily_pageviews_per_visitor <- url %>%
  read_html() %>%
  html_nodes(xpath='//div[@class="tr site-listing"]//div[@class="td right"][2]//p') %>%
  html_text() 

percent_of_traffic_from_search <- url %>%
  read_html() %>%
  html_nodes(xpath='//div[@class="tr site-listing"]//div[@class="td right"][3]//p') %>%
  html_text() 

total_sites_linking_in <- url %>%
  read_html() %>%
  html_nodes(xpath='//div[@class="tr site-listing"]//div[@class="td right"][4]//p') %>%
  html_text() 


# clean data
website_url = gsub("[\r\n]", "", website_url)
ranking_no = as.numeric(gsub("[\r\n]", "", ranking_no))
daily_time_on_site = gsub("[\r\n]", "", daily_time_on_site)
daily_pageviews_per_visitor = gsub("[\r\n]", "", daily_pageviews_per_visitor)
percent_of_traffic_from_search = gsub("[\r\n]", "", percent_of_traffic_from_search)
total_sites_linking_in = gsub("[\r\n]", "", total_sites_linking_in)


df_r <- data.frame(ranking_no, website_url, daily_time_on_site, daily_pageviews_per_visitor, percent_of_traffic_from_search, total_sites_linking_in)

df_r
