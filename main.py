#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ref doc
# http://docs.python-requests.org/zh_CN/latest/user/quickstart.html      request
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.zh.html    BeautifulSoup
# http://www.w3school.com.cn/h.asp                                       w3school


import requests
from bs4 import BeautifulSoup
import sqlite3
import datetime

base_url = r'https://www.nxp.com/support/developer-resources/evaluation-and-development-boards/analog-toolbox/s32k144-evaluation-board:S32K144EVB?&tab=Documentation_Tab&lang=en&lang_cd=en&'
base_download_url = r'https://www.nxp.com/'

def write_txt_fun(txt):
    with open('tmp.html', 'w',encoding = 'utf8') as f:
        f.write(txt)

def download_file(file_link,file_name):
    response = requests.get(file_link)
    with open('doc/'+file_name+'.pdf','wb') as f:
        f.write(response.content)

def main_fun():
    try:
        page = requests.get(base_url)
    except:
        print('requests get fail!!')
        return
        
    soup = BeautifulSoup(page.content)
    write_txt_fun(soup.prettify())

    for item in soup.find_all('li','relatedDocs-docTitle'):
        title_link = base_download_url + item.contents[0].get('href')
        title_name = item.contents[0].find('strong').get_text().strip()
        title_ver = item.contents[1].get_text().strip()
        title_name = title_name + title_ver

        download_file(title_link, title_name)

        print('download pdf file successful', title_name)
    print('download all successful !!!')

if __name__ == '__main__':
    main_fun()
  