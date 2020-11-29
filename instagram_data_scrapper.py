"""
first commit : 2020. 11. 3

last commit : 2020. 11. 30.

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
import configparser

isRunning = False # 현재 크롤링 중인지 확인할 변수
instagram_tags = [] # 태그를 저장할 리스트

# 크롤링을 하는 함수
def scrapping(user, pwd, plus_url):
    global instagram_tags
    instagram_tags.clear() # 크롤링을 시작하자마자 태그를 저장하는 리스트를 초기화 해준다.
    try:
        base_url = 'https://www.instagram.com/explore/tags/' # 기본 사이트 주소

        url = base_url + quote_plus(plus_url) # url 합치기

        browser = webdriver.Chrome('./chromedriver.exe') #현재 폴더에 위치한 드라이버를 browser로 객체화함

        browser.get(url) # 웹드라이버를 실행햐여 url 주소에 접근

        time.sleep(3) # 3초동안 페이지 업데이트를 기다림

        elem = browser.find_element_by_name('username') # 페이지 내의 username 이라는 요소를 찾는다.
        elem.send_keys(user) # user(ID)값을 요소에 보낸다. 
        elem = browser.find_element_by_name('password') # 페이지 내의 password 이라는 요소를 찾는다.
        elem.send_keys(pwd) # pwd(Password)값을 요소에 보낸다.
        elem.send_keys(Keys.RETURN) # RETURN 시킨다.

        time.sleep(4) # 페이지 로딩 대기

        browser.find_element_by_css_selector('button.sqdOP.L3NKy.y3zKF').click() # button.sqdOP.L3NKy.y3zKF 태그를 찾아 클릭

        time.sleep(3) # 페이지 로딩 대기

        browser.get(url) # 웹드라이버를 실행햐여 url 주소에 접근

        time.sleep(5) # 페이지 로딩 대기

        html = browser.page_source # 페이지의 html 데이터 가져옴
        soup = BeautifulSoup(html) # html 데이터를 beautifulsoup로 객체화함

        insta = soup.select('.eLAPa') #이미지를 나타내는 .eLAPa 태그를 선택

        if not os.path.isdir('./img\\{}'.format(plus_url)): # img 폴더에 태그명으로 만들어진 폴더가 없으면
            os.mkdir('./img\\{}'.format(plus_url)) # 태그명의 폴더 생성

        n = 0
        for i in insta:
            time.sleep(1)
            img_url = i.select_one('.KL4Bh').img['src'] # 이미지 하나를 선택하여 주소를 저장한다.

            with urlopen(img_url) as f:
                with open('./img/' + plus_url + '/' + plus_url + str(n+1) + '.jpg',mode='wb') as h: # img/태그명 디렉토리에 태그명n+1.jpg 식의 이름으로 
                    img = f.read()
                    h.write(img) # 이미지를 작성
                n += 1                

        browser.find_element_by_css_selector('div.v1Nh3.kIKUG._bz0w').click() # 한 개의 이미지를 나타내는 .v1Nh3.kIKUG._bz0w 태그를 클릭
        time.sleep(2)
        for i in range(0,n-1): # 다운받은 파일의 개수만큼 for 문이 돈다.
            try:
                tag_data = []
                time.sleep(1.5)
                data = browser.find_element_by_css_selector('div.C7I1f.X7jCj') # 해시태그가 있는 요소를 선택
                tag_raw = data.text # text 데이터를 받아온다.
                tags = re.findall('#[A-Za-z0-9가-힣]+', tag_raw) #text 데이터에서 영문과 한글만을 추려낸다.
                for j in range(0,len(tags)):
                    tag = tags[j].replace("#","") # #를 공백문자로 치환한다.
                    tag_data.append(tag) 
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

# 설정 파일을 읽어와 반환하는 함수
def open_setting():
    global config
    if os.path.isfile('./config.ini') == True:
        config.read("./config.ini")
        id_ = config['acount_info']['ID']
        password_ = config['acount_info']['Password']
        return id_, password_
    else: # config.ini 파일이 없을 경우 그냥 return
        return

# 크롤링 전에 설정파일과 키워드를 전달하는 함수
def pre_scrapping(search):
    global isRunning
    if isRunning == False:
        try:
            id_, password_ = open_setting() #그냥 return 되었을 경우 오류가 발생해 예외처리로 넘어감
        except:
            tk.messagebox.showwarning("경고!","config.ini 파일이 존재하지 않습니다.")
            return
        search_ = search.get()
        isRunning = True
        t = threading.Thread(target=scrapping, args=(id_,password_,search_)) # scrapping 함수를 별도의 스레드를 통하여 구동하여 GUI부분의 응답없음 문제를 해결
        t.start()
    else:
        tk.messagebox.showwarning("경고!","아직 크롤링 중입니다.")

# 설정 window GUI
def setting_Window():
    make_set = tk.Toplevel(root)
    make_set.geometry('290x80')
    make_set.title('Setting')
    make_set.resizable(False,False)
    make_set.iconphoto(False, tk.PhotoImage(file='./img/instagram_icon.png'))

    lbl = tk.Label(make_set, text="ID")
    lbl.grid(row=0, column=0)
    txt = tk.Entry(make_set)
    txt.grid(row=0, column=1)
    pwd_lbl = tk.Label(make_set, text="Password")
    pwd_lbl.grid(row=1, column=0)
    pwd = tk.Entry(make_set, show='*')
    pwd.grid(row=1,column = 1)
    btn = tk.Button(make_set, text = "확인 후 종료" ,command = lambda : is_entered(make_set, txt, pwd, config))
    btn.grid(row=2,column = 0, columnspan=2, padx = 5, pady= 5, ipadx = 100)

# csv 파일을 만드는 함수
def make_csv(tag_list,name):
    cnt = Counter(tag_list) # Counter를 이용하여 태그의 종류와 갯수를 딕셔너리화 한다.
    scnt = sorted(cnt.items(), key=lambda x: x[1], reverse=True) # 내림차순으로 정렬한다.
    f = open(f'./csv/{name}.csv', 'w', encoding='utf-8',newline='')
    csvWriter = csv.writer(f)
    for key,count in dict(scnt).items(): # scnt 에서 key값과 count 값을 뽑아낸다.
        csvWriter.writerow([key,count])
    f.close()

#설정을 저장하는 함수
def is_entered(window, ID, PWD, Config):
    if len(ID.get()) == 0 or len(PWD.get()) == 0:
        tk.messagebox.showerror("","입력값이 필요합니다.")
        return
    else:
        config['acount_info'] = {}
        config['acount_info']['ID'] = ID.get()
        config['acount_info']['Password'] = PWD.get()
        with open('config.ini','wt',encoding='utf-8') as con_file:
            config.write(con_file)
        window.destroy()

# ConfigParser 객체 생성
config = configparser.ConfigParser()

# main GUI 구현부
root = tk.Tk()
root.geometry('325x75')
root.title('인스타그램 크롤러')
root.resizable(False,False)
root.iconphoto(False, tk.PhotoImage(file='./img/instagram_icon.png'))

menu_bar = tk.Menu(root)
menu1 = tk.Menu(menu_bar, tearoff = 0)
menu1.add_command(label="Setting", command = setting_Window)
menu_bar.add_cascade(label='Setting', menu = menu1)

root.config(menu = menu_bar)

search_lbl = tk.Label(root, text="검색할 해시태그를 입력하세요")
search_lbl.grid(row = 0, column = 0)
search = tk.Entry(root)
search.grid(row=0, column = 1)
btn = tk.Button(root, text="실행", width=15 , command=lambda : pre_scrapping(search))
btn.grid(row=1, column=0, columnspan=2, padx = 5, pady= 5, ipadx = 100)

if os.path.isfile('./config.ini') == False:
    setting_Window()

root.mainloop()

