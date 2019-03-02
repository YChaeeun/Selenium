
from selenium import webdriver as wd

import time, urllib
from tqdm import tqdm_notebook

## =====================================================================

# 접속
driver = wd.Chrome('./tools/chromedriver.exe')

param = urllib.parse.quote('xNp7Bw3sN3c')
site ='https://www.youtube.com/watch?v='+param

driver.get(site)

## =====================================================================

def del_comma(string) :
    if ',' in string :
        string = string.replace(',', '')
    return string

## =====================================================================

# 영상 제목 .title yt-formatted-string
# 댓글 작성자 #author-text span
# 댓글 내용 #content-text a
# 댓글 좋아요 수 #vote-count-middle

## =====================================================================

# 영상 제목
title = driver.find_element_by_css_selector('.title yt-formatted-string')

# 댓글 작성자
comment_writer = driver.find_element_by_css_selector('#author-text span')

# 댓글 내용
comments = driver.find_element_by_css_selector('#content-text')

# 댓글 좋아요
c_likes = driver.find_element_by_css_selector('#vote-count-middle')


## =====================================================================

# 전체 댓글 긁어오기

for _ in tqdm_notebook(range(10000)):
    driver.execute_script('window.scrollBy(0,500)')

content = driver.find_elements_by_css_selector('#comments #contents #comment')

v_comments = list()

for values in tqdm_notebook(content) :
    comment_writer = values.find_element_by_css_selector('#author-text span')
    comments = values.find_element_by_css_selector('#content-text')
    c_likes = values.find_element_by_css_selector('#vote-count-middle')
    
    # 좋아요 값이 있다면 int 형으로 바꾸고, 없다면 0으로 처리
    if c_likes.text :
        c_likes = int(c_likes.text)
    else :
        c_likes = 0
        
    dic1 = {
        'v_title' : title,
        'comment_writer' : comment_writer.text,
        'comments' : comments.text,
        'c_likes' : c_likes
    }
    v_comments.append(dic1)

## =====================================================================

import pymysql as sql
from sqlalchemy import create_engine

import pandas as pd
import pandas.io.sql as pSql

## =====================================================================

# DB에 적제하기
driver = 'mysql+pymysql://root:1234@localhost:3306/crawling'
engine = create_engine(driver, encoding='utf-8')

conn = engine.connect()

df = pd.DataFrame.from_dict(v_comments)
df.to_sql(name='v_comments', con=conn, if_exists='append', index=False)

# 만약 이모티콘 저장에 문제가 있다면
# 이모티콘 저장을 위해 DB 테이블 설정을 utf8mb4, utf8mb4_unicode_ci 로 변경

if conn:
    conn.close()
    print('엔진 정상 종료')

