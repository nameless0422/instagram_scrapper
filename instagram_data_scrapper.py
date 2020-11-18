"""
first commit : 2020. 11. 3

202011751 컴퓨터공학부 최진영

name : instagram_data_scrapper

인스타그램의 특정 태그를 검색하여 이미지와 해시태그 데이터를 수집하는 프로그램이다.

"""
from urllib.request import urlopen
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from collections import Counter
import tkinter as tk
import tkinter.messagebox
import os
import os.path
import re
import time
import threading
import csv

isRunning = False # 현재 크롤링 중인지 확인할 변수
instagram_tags = [] # 태그를 저장할 리스트

def scrapping(user, pwd, plus_url):
    global instagram_tags
    instagram_tags.clear() # 크롤링을 시작하자마자 초기화 해준다.
    try:
        base_url = 'https://www.instagram.com/explore/tags/' # 기본 사이트 주소

        url = base_url + quote_plus(plus_url) # url 합치기

        browser = webdriver.Chrome('./chromedriver.exe') #현재 폴더에 위치한 드라이버를 browser로 객체화함
        browser.get(url) # 웹드라이버를 실행햐여 url 주소에 접근

        time.sleep(3) # 3초동안 페이지 업데이트를 기다림

        html = browser.page_source # 페이지의 html 데이터 가져옴
        soup = BeautifulSoup(html) # html 데이터를 beautifulsoup로 객체화함

        browser.find_element_by_css_selector('div.v1Nh3.kIKUG._bz0w').click() # 페이지 내의 이미지의 CSS 태그 div.v1Nh3.kIKUG._bz0w 를 찾아 클릭한다.
        elem = browser.find_element_by_name('username') # 페이지 내의 username 이라는 요소를 찾는다.
        elem.send_keys(user) # user(ID)값을 요소에 보낸다. 
        elem = browser.find_element_by_name('password') # 페이지 내의 password 이라는 요소를 찾는다.
        elem.send_keys(pwd) # pwd(Password)값을 요소에 보낸다.
        elem.send_keys(Keys.RETURN) # RETURN 시킨다.

        time.sleep(4) # 페이지 로딩 대기

        browser.find_element_by_css_selector('button.sqdOP.L3NKy.y3zKF').click() # button.sqdOP.L3NKy.y3zKF 태그를 찾아 클릭

        time.sleep(4) # 페이지 로딩 대기

        insta = soup.select('.v1Nh3.kIKUG._bz0w') # 한 줄(3개)의 이미지를 나타내는 .v1Nh3.kIKUG._bz0w 태그를 선택

        if not os.path.isdir('./img\\{}'.format(plus_url)): # img 폴더에 태그명으로 만들어진 폴더가 없으면
            os.mkdir('./img\\{}'.format(plus_url)) # 태그명의 폴더 생성

        n = 0
        for i in insta:
            time.sleep(1)
            img_url = i.select_one('.KL4Bh').img['src'] # 이미지 하나를 선택

            with urlopen(img_url) as f:
                with open('./img/' + plus_url + '/' + plus_url + str(n+1) + '.jpg',mode='wb') as h: # img/태그명 디렉토리에 태그명n+1.jpg 식의 이름으로 
                    img = f.read()
                    h.write(img) # 이미지를 작성
                n += 1                

        browser.find_element_by_css_selector('div.v1Nh3.kIKUG._bz0w').click() # 한 줄(3개)의 이미지를 나타내는 .v1Nh3.kIKUG._bz0w 태그를 클릭
        for i in range(0,n): # 다운받은 파일의 개수만큼 for 문이 돈다.
            try:
                time.sleep(1)
                data = browser.find_element_by_css_selector('div.C7I1f.X7jCj') # 해시태그가 있는 요소를 선택
                tag_raw = data.text # text 데이터를 받아온다.
                tags = re.findall('#[A-Za-z0-9가-힣]+', tag_raw) #text 데이터에서 영문과 한글만을 추려낸다.
                tag = ''.join(tags).replace("#"," ") # #를 공백문자로 치환하여 문자열화 시킨다.

                tag_data = tag.split() # 문자열을 리스트로 나눈다.

                for tag_one in tag_data:
                    instagram_tags.append(tag_one) # tag_data 의 값을 instagram_tages 리스트에 넣는다.
            except Exception as a: # 요소선택에 실패했을 경우 오류 메세지 출력후 다음 작업 진행
                print(a)
            browser.find_element_by_css_selector('a._65Bje.coreSpriteRightPaginationArrow').click() # 다음 게시물로 넘어가는 버튼을 찾아 클릭
            time.sleep(3)

        # 모은 태그들을 csv 파일화 한다.
        make_csv(instagram_tags,plus_url)

        browser.close()

        global isRunning
        isRunning = False
        tk.messagebox.showinfo("","크롤링이 완료되었습니다.")
    except Exception as e:
        isRunning = False
        print('예외 발생 : ',e) # 예외 발생시 오류 메세지 출력
        tk.messagebox.showerror("","크롤링이 중단되었습니다.") # 예외가 발생하여 크롤링이 중단되었을시 에러메시지 윈도우를 보여준다.
        

def get_str():
    global isRunning
    if isRunning == False:
        id_ = txt.get()
        password_ = pwd.get()
        search_ = search.get()
        isRunning = True
        t = threading.Thread(target=scrapping, args=(id_,password_,search_)) # scrapping 함수를 별도의 스레드를 통하여 구동하여 GUI부분의 응답없음 문제를 해결
        t.start()
    else:
        tk.messagebox.showwarning("경고!","아직 크롤링 중입니다.")
        

def setting():
    newWindow = tk.Toplevel(root)
    labelExample = tk.Label(newWindow, text = "New Window")
    buttonExample = tk.Button(newWindow, text = "New Window button")
    labelExample.pack()
    buttonExample.pack()

# csv 파일을 만드는 함수
def make_csv(tag_list,name):
    cnt = Counter(tag_list) # Counter를 이용하여 태그의 종류와 갯수를 딕셔너리화 한다.
    f = open(f'./csv/{name}.csv', 'w', encoding='utf-8',newline='')
    csvWriter = csv.writer(f)
    for key,count in cnt.items(): # cnt 에서 key값과 count 값을 뽑아낸다.
        csvWriter.writerow([key,count])
    f.close()
    

root = tk.Tk()
root.geometry('325x120')
root.title('인스타그램 크롤러')
root.resizable(False,False)
root.iconphoto(False, tk.PhotoImage(file='./img/instagram_icon.png'))

menu_bar = tk.Menu(root)
menu1 = tk.Menu(menu_bar, tearoff = 0)
menu1.add_command(label="Setting", command = setting)
menu_bar.add_cascade(label='Setting', menu = menu1)

root.config(menu = menu_bar)

lbl = tk.Label(root, text="ID")
lbl.grid(row=0, column=0)
txt = tk.Entry(root)
txt.grid(row=0, column=1)
pwd_lbl = tk.Label(root, text="Password")
pwd_lbl.grid(row=1, column=0)
pwd = tk.Entry(root, show='*')
pwd.grid(row=1,column = 1)
search_lbl = tk.Label(root, text="검색할 해시태그를 입력하세요")
search_lbl.grid(row = 2, column = 0)
search = tk.Entry(root)
search.grid(row=2, column = 1)
btn = tk.Button(root, text="실행", width=15 , command=get_str)
btn.grid(row=3, column=0, columnspan=2, padx = 5, pady= 5, ipadx = 100)

root.mainloop()