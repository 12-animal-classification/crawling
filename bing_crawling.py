from icrawler.builtin import BingImageCrawler


bing_crawler = BingImageCrawler(downloader_threads=4,
                                storage={'root_dir': 'img/pig'})
bing_crawler.crawl(keyword='pig front face -iconfinder -illustration', filters=None, offset=0, max_num=1000)
