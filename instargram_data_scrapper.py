from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import tkinter as tk
import os
import re
import time

def scrapping(self, user, pwd):
    base_url = 'https://www.instagram.com/explore/tags/' # 기본 사이트 주소
    plus_url = input('검색할 태그를 입력하세요 : ') 

    url = base_url + quote_plus(plus_url) # url 합치기

    instagram_tags = []

    browser = webdriver.Chrome('./chromedriver.exe')
    browser.get(url)

    time.sleep(2)

    html = browser.page_source
    soup = BeautifulSoup(html)

    browser.find_element_by_css_selector('div.v1Nh3.kIKUG._bz0w').click()
    elem = browser.find_element_by_name('username')
    elem.send_keys(user)
    elem = browser.find_element_by_name('password')
    elem.send_keys(pwd)
    elem.send_keys(Keys.RETURN)

    time.sleep(3)

    browser.find_element_by_css_selector('button.sqdOP.L3NKy.y3zKF').click()

    time.sleep(3)

    insta = soup.select('.v1Nh3.kIKUG._bz0w') #select를 이용하여 이미지 태그로 선택

    if not os.path.isdir('./img\\{}'.format(plus_url)):
        os.mkdir('./img\\{}'.format(plus_url))

    n = 1
    for i in insta:
        time.sleep(1)
        img_url = i.select_one('.KL4Bh').img['src']

        with urlopen(img_url) as f:
            with open('./img/' + plus_url + '/' + plus_url + str(n) + '.jpg',mode='wb') as h:
                img = f.read()
                h.write(img)
            n += 1

    browser.find_element_by_css_selector('div.v1Nh3.kIKUG._bz0w').click()
    for i in range(0,n-1):
        time.sleep(1)
        data = browser.find_element_by_css_selector('div.C7I1f.X7jCj')
        tag_raw = data.text
        tags = re.findall('#[A-Za-z0-9가-힣]+', tag_raw)
        tag = ''.join(tags).replace("#"," ")

        tag_data = tag.split()

        for tag_one in tag_data:
            instagram_tags.append(tag_one)
        
        browser.find_element_by_css_selector('a._65Bje.coreSpriteRightPaginationArrow').click()
        time.sleep(3)

    browser.close()

    return instagram_tags

def get_str(txt,pwd):
    id_ = txt.get()
    password_ = pwd.get()
    print(id_,password_)
    return id_,password_

root = tk.Tk()
root.geometry('450x250+100+100')
root.title('인스타그램 크롤러')
root.resizable(False,False)


lbl = tk.Label(root, text="ID")
lbl.grid(row=0, column=0)
txt = tk.Entry(root)
txt.grid(row=0, column=1)
pwd_lbl = tk.Label(root, text="Password")
pwd_lbl.grid(row=1, column=0)
pwd = tk.Entry(root, show='*')
pwd.grid(row=1,column = 1)
btn = tk.Button(root, text="OK", width=15 , command=get_str(txt,pwd))
btn.grid(row=2, column=1)



root.mainloop()


