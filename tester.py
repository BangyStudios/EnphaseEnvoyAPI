import query

crawler = query.Crawler()
crawler.write_titles_csv()
while True:
    crawler.update_page()
    crawler.update_page_data()
    crawler.write_values_csv()