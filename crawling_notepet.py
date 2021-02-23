from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv
import datetime
import re
import time


class CrawlClass(object):
    def __init__(self):
        self.url = 'https://www.notepet.co.kr/news/article/article_list/'
        self.file_name = 'news'
        self.file_extension = 'tsv'

    def selenium_init(self):
        ua = UserAgent(verify_ssl=False)
        user_agent = ua.random
        opts = Options()
        opts.add_argument('user-agent={}'.format(user_agent))
        option = webdriver.ChromeOptions()
        # option.add_argument('headless')
        option.add_argument('window-size=1920x1080')
        # server
        # driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', options=option)
        # local
        driver = webdriver.Chrome(executable_path=r'..\chromedriver.exe', options=opts)
        return driver

    def main(self):
        # 웹드라이버 옵션 설정
        driver = self.selenium_init()

        # 크롤링 타겟 사이트 주소 입력
        driver.get(self.url)
        driver.maximize_window()
        try:
            crawl_results = self.crawl(driver)
            append_results = self.append(driver, crawl_results)
            self.save_tsv(append_results)
        except Exception as ex:
            print('{}'.format(ex))
            exit(1)
        finally:
            driver.delete_all_cookies()
            driver.quit()

    def save_tsv(self, arr):
        f = open(r'D:\{}.{}'.format(self.file_name, self.file_extension), 'w', encoding='utf-8', newline='')
        wr = csv.writer(f, delimiter='\t')
        cnt = 0
        wr.writerow(['url', 'date', 'title', 'header', 'contents'])
        for row in arr:
            wr.writerow(row.values())
        f.close()

    def get_page_cnt(self, driver):
        pattern_date = r'(\d{4}(\.\d{2})*)'
        cnt = 0
        page = 0
        while True:
            cnt += 1
            if cnt != 1:
                driver.execute_script('javascript:goPage({})'.format(cnt))
                time.sleep(1)
            date_list = driver.find_elements_by_xpath('/html/body/div[2]/div[3]/div/div/div[1]/div[3]/ul/li/div[2]')
            for row in date_list:
                time.sleep(0.5)
                date = re.findall(pattern_date, row.text)[0][0]
                pre_date = datetime.datetime.now() - datetime.timedelta(days=7)
                to_date = datetime.datetime.strptime(date, '%Y.%m.%d')
                days = to_date - pre_date
                if days.days < 0:
                    page = cnt
                    break
            if page != 0:
                break
        return page

    def append(self, driver, rows):
        for row in rows:
            contents = ''
            driver.execute_script(row['url'])
            time.sleep(0.5)
            p_list = driver.find_elements_by_xpath('/html/body/div[2]/div[4]/div/div/div[1]/div[2]/div[2]/div[1]/p')
            for p in p_list:
                if p.text != '':
                    contents += p.text
            pattern = r'(\[노트펫\][a-zA-Z0-9가-힣\s\'\,\"]*)'
            intro = re.search(pattern, contents)
            row['url'] = driver.current_url
            row['title'] = driver.find_element_by_xpath('/html/body/div[2]/div[4]/div/div/div[1]/div[2]/h1').text
            row['header'] = intro.group()
            row['contents'] = contents
            driver.back()
            # driver.execute_script("window.history.go(-1)")
            time.sleep(0.5)
        return rows

    def crawl(self, driver):
        page = self.get_page_cnt(driver)
        pattern_date = r'(\d{4}(\.\d{2})*)'
        res = []
        for i in range(1, int(page)):
            li_list = driver.find_elements_by_xpath('/html/body/div[2]/div[3]/div/div/div[1]/div[3]/ul/li')
            for li in li_list:
                title = li.find_element_by_xpath('p').text
                url = li.find_element_by_xpath('a').get_attribute('href')
                temp_date = li.find_element_by_xpath('div[2]').text
                date = re.findall(pattern_date, temp_date)[0][0]
                res.append({
                    'url': url,
                    'date': date
                })
        return res


# "BPLC_NM":"새롬동물병원"
# 광주, 대구, 서울, 경기에서 에러남.
if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.main()
