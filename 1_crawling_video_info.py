from selenium import webdriver as wd

import time, urllib
from tqdm import tqdm_notebook

# 사이트 접속

driver = wd.Chrome('./tools/chromedriver.exe')

param = urllib.parse.quote('IC1Zv4CXnAE')
site = 'https://www.youtube.com/watch?v=' + param

driver.get(site)

# ==============================================================

# 영상 제목 : .title > yt-formatted-string
# 채널 명 : #upload-info > a
# 게시일 : #upload-info > span
# 조회수 : .view-count
# 좋아요 : #top-level-buttons > yt-formatted-string > aria-label
# 싫어요 : #top-level-buttons > yt-formatted-string > aria-label
# 댓글 수 : #count

# ==============================================================

# int 자료형으로 저장하기 위해 4,300 => 4300 으로 바꾸는 함수 (',' 제거)
def del_comma(string) :
    if ',' in string :
        string = string.replace(',', '')
    return string

# ==============================================================

title = driver.find_element_by_css_selector('.title yt-formatted-string')

owner = driver.find_element_by_css_selector('#upload-info a')

# DB에 날짜 자료형으로 넣기 위해 처리
upload_date = driver.find_element_by_css_selector('#upload-info span')
upload_date = upload_date.text.split(':')
date = upload_date[1][1:].split('.')
upload_date = date[0]+'-'+date[1]+'-'+date[2]
upload_date = upload_date.replace(' ', '')


view = driver.find_element_by_css_selector('.view-count')
view = view.text.split(' ')
view = del_comma(view[1][:-1])


likes = driver.find_element_by_css_selector('#top-level-buttons yt-formatted-string').get_attribute('aria-label')
likes = likes.split(' ')
likes = del_comma(likes[1][:-1])


dislike = driver.find_elements_by_css_selector('#top-level-buttons yt-formatted-string')
dislike = dislike[1].get_attribute('aria-label').split(' ')
dislike = del_comma(dislike[1][:-1])


# 커서 아래로 이동
for _ in range(5) :
    driver.execute_script("window.scrollBy(0,400)")


num_comments = driver.find_elements_by_css_selector('#count')
num_comments = num_comments[2].text.split(' ')
num_comments = del_comma(num_comments[1][:-1])


# ==============================================================

# 리스트 딕셔너리에 정보 저장

result_list = list()
dic1 = {
    'v_title' : title.text,
    'v_owner' :owner.text,
    'v_upload_date' :upload_date,
    'v_views' :float(view),
    'v_likes' : int(likes),
    'v_dislikes' : int(dislike),
    'v_num_comments' : int(num_comments)
}

# 디비에 저장하려면 테이블 컬럼의 이름과 동일해야 함

result_list.append(dic1)

# ==============================================================

# DB에 적제 

import pymysql as sql
from sqlalchemy import create_engine

import pandas as pd
import pandas.io.sql as pSql


driver = 'mysql+pymysql://root:1234@localhost:3306/crawling'
engine = create_engine(driver, encoding='utf-8') # DB를 general-ci로 

# 미리 디비에 테이블을 만들어놓고, 값을 저장하는게 좋아 -> 자료형 정의

conn = engine.connect()

# 리스트 딕셔너리를 데이터프레임으로 바꾸기
df = pd.DataFrame.from_dict(result_list)

# 데이터 프레임을 sql에 저장하기
# name = 테이블 명 / con= 연결정보 / if_exist=기존 정보가 이미 있다면 어떻게 처리할래?
# index 인덱스 처리
df.to_sql(name='video_info', con=conn, if_exists='append', index=False)

if conn:
    conn.close()
    print('엔진 정상 종료')
