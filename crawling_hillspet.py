#-*- coding:utf-8 -*-
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pymysql
import re
import requests
import time

class CrawlClass(object):
    def __init__(self):
        print('start')

    def run_crawl(self):
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
        try:
            result = self.crawl(driver)
            detail_result = self.crawl_detail(driver, result)
            self.insert_local(detail_result)
        except Exception:
            print(Exception)
        finally:
            driver.delete_all_cookies()
            driver.quit()

    def local_table(self):
        conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            port=3306,
            password='dangam',
            db='local',
            charset='utf8mb4'
        )
        return conn

    def insert_local(self, data):
        try:
            conn = self.local_table()
            sql = """INSERT INTO bio_class VALUES (%(id)s, %(name)s, %(weight)s, %(size)s, %(external_features)s, 
            %(daily_exercise)s, %(activity)s, %(life)s, %(spit)s, %(snore)s, %(bark)s, %(dig)s, %(sociability)s, %(breed_purpose)s, %(fur_length)s, 
            %(fur_features)s, %(fur_color)s, %(beauty_necessity)s, %(akc_class)s, %(ukc_class)s, %(distribution)s, %(character)s, %(living_together)s, %(history)s, %(description)s)"""
            conn.cursor().executemany(sql, data)
            conn.cursor().close()
            conn.commit()
            conn.close()
        except Exception:
            print(Exception)

    def crawl_detail(self, driver, result):
        cnt = 0
        res = []
        for row in result:
            cnt += 1
            arr = []
            if cnt != 0:
                print(str(cnt)+row['url'])
                response = requests.get(row['url'])
                time.sleep(1)
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                time.sleep(1)
                length = soup.select('#content > div > div > div > div:nth-child(3) > div > div > div > div > div > div.row')
                if len(length) > 2:
                    main = soup.select('#content > div > div > div > div:nth-child(3) > div > div > div > div')
                    div = str(main[0].contents[1].contents).replace('</strong>', '')
                elif len(length) == 2:
                    main = soup.select('#content > div > div > div > div:nth-child(3) > div > div > div')
                    div = str(main[0].contents[1].contents).replace('</strong>', '')

                pattern_name = r'https://www.hillspet.co.kr/dog-care/dog-breeds/([a-zA-Z\-]*)'
                pattern_desc1 = r'jpg\"\/\>\n\<\/div\>\n<p>([가-힣 ]*)'
                pattern_desc2 = r'row headline">([0-9가-힣\,\-<p></p>\s\n\.]*)'
                pattern_external_features = r'(\<h2\>|\<h2\>\<strong\>)특징:?\<\/h2\>\n\<p\>([가-힣 ,()]*)\<\/p\>'
                pattern_daily = r'(운동량|요구량):([0-9가-힣\,\-\<\>\/\s&lt;&gt;]*)\<\/p\>'
                pattern_activity = r'(운동량|활동량):([0-9가-힣 \,]*)'
                pattern_life = r'(수명 범위|예상 수명):([0-9가-힣 \,\-]*)'
                pattern_spit = r'침 흘리는 성향: ([0-9가-힣\,\-]*)'
                pattern_snore = r'(코고는 경향|코 고는 성향|코골이|코 고는 경향):([0-9가-힣\,\- ]*)'
                pattern_bark = r'짖는 (성향|경향):([0-9가-힣\,\- ]*)'
                pattern_dig = r'(땅|땅을) 파는 (경향|성향): ([0-9가-힣\,\-]*)'
                pattern_social = r'(관심도|관심 필요성|보살핌이 필요한 정도): ([0-9가-힣\,\-]*)'
                pattern_breed = r'(사육 목적:</h2>\n|사육 목적\<\/p\>\n)\<p\>([0-9가-힣\,\- ]*)'
                pattern_fur_len = r'길이:([0-9가-힣\,\-\/\s]*)'
                pattern_fur_fea = r'(특징|특성):([0-9가-힣\,\-\s\/]*)'
                pattern_fur_col = r'(색상|색):([0-9가-힣\,\-\s\/]*)'
                pattern_beauty = r'미용 필요성: ([0-9가-힣\,\-\s]*)'
                pattern_akc = r'(AKC 분류|ACK 분류|AKC\)):([0-9가-힣\,\-\s]*)'
                pattern_ukc = r'(UKC 분류|UKC\)):([0-9가-힣\,\-\s]*)'
                pattern_distri = r'(분포도|분포|\+): ([0-9가-힣\,\-\s]*)'
                pattern_char = r'성격\:\<\/h3\>([0-9a-zA-Z가-힣\,\s\'\/\\\<\>\.\\“\”\"\!\—\(\)\;]*)(<h3>|])'
                pattern_living = r'함께 살기\:\<\/h3\>([0-9a-zA-Z가-힣\,\s\'\/\\\<\>\.\\“\”\"\!\—\(\)\;]*)(<h3>|])'
                pattern_his = r'역사\:\<\/h3\>([0-9a-zA-Z가-힣\,\s\'\/\\\<\>\.\\“\”\"\;\!\—\(\)]*)(<h3>|])'
                row['id'] = int(cnt)
                temp_name1 = re.findall(pattern_name, row['url'])
                row['name'] = self.edit(temp_name1[0]).replace('-', ' ')
                row['weight'] = float(0.0)
                row['size'] = ''
                temp_desc1 = re.findall(pattern_desc1, div)
                if len(temp_desc1) != 0:
                    temp_desc1 = self.edit(temp_desc1[0])
                else:
                    temp_desc1 = ''
                temp_desc2 = re.findall(pattern_desc2, div)
                if len(temp_desc2) != 0:
                    temp_desc2 = self.edit(temp_desc2[0])
                else:
                    temp_desc2 = ''
                row['description'] = temp_desc1 + ' ' + temp_desc2
                temp_exter = re.findall(pattern_external_features, div)
                if len(temp_exter) != 0:
                    row['external_features'] = self.edit(temp_exter[0][1])
                else:
                    row['external_features'] = ''
                temp_daily = re.findall(pattern_daily, div)
                if len(temp_daily) != 0:
                    row['daily_exercise'] = self.edit(temp_daily[0][1])
                else:
                    row['daily_exercise'] = ''
                temp_act = re.findall(pattern_activity, div)
                if len(temp_act) != 0:
                    row['activity'] = self.edit(temp_act[0][1])
                else:
                    row['activity'] = ''
                temp_life = re.findall(pattern_life, div)
                if len(temp_life) != 0:
                    row['life'] = self.edit(temp_life[0][1])
                else:
                    row['life'] = ''
                temp_spit = re.findall(pattern_spit, div)
                if len(temp_spit) != 0:
                    row['spit'] = self.edit(temp_spit[0])
                else:
                    row['spit'] = ''
                temp_snore = re.findall(pattern_snore, div)
                if len(temp_snore) != 0:
                    row['snore'] = self.edit(temp_snore[0][1])
                else:
                    row['snore'] = ''
                temp_bark = re.findall(pattern_bark, div)
                if len(temp_bark) != 0:
                    row['bark'] = self.edit(temp_bark[0][1])
                else:
                    row['bark'] = ''
                temp_dig = re.findall(pattern_dig, div)
                if len(temp_dig) != 0:
                    row['dig'] = self.edit(temp_dig[0][2])
                else:
                    row['dig'] = ''
                temp_soc = re.findall(pattern_social, div)
                if len(temp_soc) != 0:
                    row['sociability'] = self.edit(temp_soc[0][1])
                else:
                    row['sociability'] = ''
                temp_breed = re.findall(pattern_breed, div)
                if len(temp_breed) != 0:
                    row['breed_purpose'] = self.edit(temp_breed[0][1])
                else:
                    row['breed_purpose'] = ''
                temp_fur_len = re.findall(pattern_fur_len, div)
                if len(temp_fur_len) != 0:
                    row['fur_length'] = self.edit(temp_fur_len[0])
                else:
                    row['fur_length'] = ''
                temp_fur_fea = re.findall(pattern_fur_fea, div)
                if len(temp_fur_fea) == 2:
                    row['fur_features'] = self.edit(temp_fur_fea[1][1])
                else:
                    row['fur_features'] = self.edit(temp_fur_fea[0][1])
                temp_fur_col = re.findall(pattern_fur_col, div)
                if len(temp_fur_col) != 0:
                    row['fur_color'] = self.edit(temp_fur_col[0][1])
                else:
                    row['fur_color'] = ''
                temp_beauty = re.findall(pattern_beauty, div)
                if len(temp_beauty) != 0:
                    row['beauty_necessity'] = self.edit(temp_beauty[0])
                else:
                    row['beauty_necessity'] = ''
                temp_akc = re.findall(pattern_akc, div)
                if len(temp_akc) != 0:
                    row['akc_class'] = self.edit(temp_akc[0][1])
                else:
                    row['akc_class'] = ''
                temp_ukc = re.findall(pattern_ukc, div)
                if len(temp_ukc) != 0:
                    row['ukc_class'] = self.edit(temp_ukc[0][1])
                else:
                    row['ukc_class'] = ''
                temp_distri = re.findall(pattern_distri, div)
                if len(temp_distri) != 0:
                    row['distribution'] = self.edit(temp_distri[0][1])
                else:
                    row['distribution'] = ''
                temp_char = re.findall(pattern_char, div)
                if len(temp_char) != 0:
                    row['character'] = self.edit(temp_char[0][0])
                else:
                    row['character'] = ''
                temp_liv = re.findall(pattern_living, div)
                if len(temp_liv) != 0:
                    row['living_together'] = self.edit(temp_liv[0][0])
                else:
                    row['living_together'] = ''
                temp_his = re.findall(pattern_his, div)
                if len(temp_his) != 0:
                    row['history'] = self.edit(temp_his[0][0])
                else:
                    row['history'] = ''
        return result

    def edit(self, word):
        return word.replace('<p>', '').replace('"', '').replace('</p>', '').replace('<strong>', '').replace('</strong>', '').replace('<h3>', '').replace('</h3>', '').replace('&lt;', '').replace(r"'\n'", '').replace(', ', '').replace('<', '').replace('“', '').strip()

    def crawl(self, driver):
        res = []
        url = 'https://www.hillspet.co.kr/dog-care/breeds#stq=&stp={}&preserveFilters=true'
        driver.maximize_window()

        for i in range(1, 12):
            driver.get(url.format(i))
            time.sleep(1)
            list_link = driver.find_elements_by_xpath('//*[@id="st-pcc-results-container"]/div/div[2]/a')
            for row in list_link:
                res.append({
                    'url': row.get_attribute('href')
                })
        return res


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
