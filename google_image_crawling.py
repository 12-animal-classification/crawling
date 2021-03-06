from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve
import os
import socket
import time


def scroll_down():
    scroll_count = 0
    print("ㅡ 스크롤 다운 시작 ㅡ")
    # 스크롤 위치값 얻고 last_height 에 저장
    last_height = driver.execute_script("return document.body.scrollHeight")
    # 결과 더보기 버튼을 클릭했는지 유무
    after_click = False
    while True:
        div = driver.find_element_by_xpath('//*[@id="islrg"]/div[1]')
        # class_name에 공백이 있는 경우 여러 클래스가 있는 것이므로 아래와 같이 css_selector로 찾음
        img_list = div.find_elements_by_css_selector(".rg_i.Q4LuWd")
        if len(img_list) > end_count:
            break
        print(f"ㅡ 스크롤 횟수: {scroll_count} ㅡ")
        # 스크롤 다운
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        scroll_count += 1
        driver.implicitly_wait(2)
        time.sleep(2)
        # 스크롤 위치값 얻고 new_height 에 저장
        new_height = driver.execute_script("return document.body.scrollHeight")
        # 스크롤이 최하단이며
        if last_height == new_height:
            # 결과 더보기 버튼을 클릭한적이 있는 경우
            if after_click is True:
                print("ㅡ 스크롤 다운 종료 ㅡ")
                break
            # 결과 더보기 버튼을 클릭한적이 없는 경우
            if after_click is False:
                if driver.find_element_by_xpath('//*[@id="islmp"]/div/div/div/div/div[5]/input').is_displayed():
                    driver.find_element_by_xpath('//*[@id="islmp"]/div/div/div/div/div[5]/input').click()
                    after_click = True
                elif NoSuchElementException:
                    print("ㅡ NoSuchElementException ㅡ")
                    print("ㅡ 스크롤 다운 종료 ㅡ")
                    break
        last_height = new_height


def click_and_retrieve(index, img, img_list_length):
    global crawled_count
    try:
        img.click()
        driver.implicitly_wait(3)
        src = driver.find_element_by_xpath(
            '//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div/div[2]/a/img').get_attribute('src')
        # src.split('.')[-1] = 확장자
        time.sleep(2)
        # urlretrieve(src, f"{path}/{date}/{query}/{crawled_count + 1}.{src.split('.')[-1]}")
        urlretrieve(src, f"{path}/{date}/{query}/{crawled_count + 1}.jpg")
        print(f"{index + 1} / {img_list_length} 번째 사진 저장 (png)")
        crawled_count += 1
    except HTTPError:
        print("ㅡ HTTPError & 패스 ㅡ")
        pass


def crawling():
    global crawled_count
    print("ㅡ 크롤링 시작 ㅡ")
    # 이미지 고급검색 중 이미지 유형 '사진'
    url = f"https://www.google.com/search?as_st=y&tbm=isch&hl=ko&as_q={query}&as_epq=&as_oq=&as_eq=&cr=&as_sitesearch=&safe=images&tbs=itp:photo"
    driver.get(url)
    driver.maximize_window()
    scroll_down()
    driver.implicitly_wait(3)
    time.sleep(3)
    div = driver.find_element_by_xpath('//*[@id="islrg"]/div[1]')
    # class_name에 공백이 있는 경우 여러 클래스가 있는 것이므로 아래와 같이 css_selector로 찾음
    img_list = div.find_elements_by_css_selector(".rg_i.Q4LuWd")
    os.makedirs(path + '/' + date + '/' + query)
    print(f"ㅡ {path}{date}/{query} 생성 ㅡ")
    cnt = 0
    for index, img in enumerate(img_list):
        if end_count == cnt and end_count != 0:
            break
        cnt += 1
        try:
            click_and_retrieve(index, img, len(img_list))
        except ElementClickInterceptedException:
            print("ㅡ ElementClickInterceptedException ㅡ")
            driver.execute_script("window.scrollTo(0, window.scrollY + 100)")
            print("ㅡ 100만큼 스크롤 다운 및 3초 슬립 ㅡ")
            time.sleep(3)
            click_and_retrieve(index, img, len(img_list))
        except NoSuchElementException:
            print("ㅡ NoSuchElementException ㅡ")
            driver.execute_script("window.scrollTo(0, window.scrollY + 100)")
            print("ㅡ 100만큼 스크롤 다운 및 3초 슬립 ㅡ")
            time.sleep(3)
            click_and_retrieve(index, img, len(img_list))
        except ConnectionResetError:
            print("ㅡ ConnectionResetError & 패스 ㅡ")
            pass
        except URLError:
            print("ㅡ URLError & 패스 ㅡ")
            pass
        except socket.timeout:
            print("ㅡ socket.timeout & 패스 ㅡ")
            pass
        except socket.gaierror:
            print("ㅡ socket.gaierror & 패스 ㅡ")
            pass
        except ElementNotInteractableException:
            print("ㅡ ElementNotInteractableException ㅡ")
            break
    try:
        print("ㅡ 크롤링 종료 (성공률: %.2f%%) ㅡ" % (crawled_count / len(img_list) * 100.0))

    except ZeroDivisionError:
        print("ㅡ img_list 가 비어있음 ㅡ")
    # driver.quit()


def filtering():
    print("ㅡ 필터링 시작 ㅡ")
    filtered_count = 0
    dir_name = path + date + '/' + query
    for index, file_name in enumerate(os.listdir(dir_name)):
        try:
            file_path = os.path.join(dir_name, file_name)
            img = Image.open(file_path)

            # 이미지 해상도의 가로와 세로가 모두 350이하인 경우
            if img.width < 351 and img.height < 351:
                img.close()
                os.remove(file_path)
                print(f"{index} 번째 사진 삭제")
                filtered_count += 1
        # 이미지 파일이 깨져있는 경우
        except OSError:
            os.remove(file_path)
            filtered_count += 1
    print(f"ㅡ 필터링 종료 (총 갯수: {crawled_count - filtered_count}) ㅡ")


def checking():
    # 입력 받은 검색어가 이름인 폴더가 존재하면 중복으로 판단
    for dir_name in os.listdir(path):
        file_list = os.listdir(path + '/' + dir_name)
        if query in file_list:
            print(f"ㅡ 중복된 검색어 ({dir_name}) ㅡ")
            return True


# clickAndRetrieve() 과정에서 urlretrieve 이 너무 오래 걸릴 경우를 대비해 타임 아웃 지정
socket.setdefaulttimeout(30)

# 이미지들이 저장될 경로 및 폴더 이름
path = "D:/"
date = "1"

# 드라이버 경로 지정 (Microsoft Edge)
option = webdriver.ChromeOptions()
option.add_argument('headless')
option.add_argument('window-size=1920x1080')
driver = webdriver.Chrome(executable_path="C:/workspace/flask_crawling/chromedriver.exe", options=option)
crawled_count = 100


# 목표 크롤링 수 만약 0 이면 전체 크롤링
end_count = 10
# 여기다가 검색할 키워드 입력하면 됨.
# arr = [
#   '1', '2', '3' ... 'n'
# ]
arr = [
    '가수 민경훈 얼굴',
    '호랑이 상 연예인',
    '고양이 상 연예인'
]


for row in arr:
    query = row
    time.sleep(2)
    crawling()

driver.delete_all_cookies()
driver.quit()
# filtering()








