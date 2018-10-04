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
import re

base_url = r'https://www.nxp.com/support/developer-resources/evaluation-and-development-boards/analog-toolbox/s32k144-evaluation-board:S32K144EVB?&tab=Documentation_Tab&lang=en&lang_cd=en&'
base_download_url = r'https://www.nxp.com/'

def main_fun():
    try:
        page = requests.get(base_url)   
        con = sqlite3.connect("main.db")    
        cur = con.cursor()  
        cur.execute('create table if not exists user (name STRING, ver DOUBLE)')
        soup = BeautifulSoup(page.content)
        for item in soup.find_all('li','relatedDocs-docTitle'):
            title_link = base_download_url + item.contents[0].get('href')
            title_name = item.contents[0].find('strong').get_text().strip()
            title_ver = item.contents[1].get_text().strip()
            title_name = title_name + title_ver

            value_name = title_name
            value_ver =  float(re.split(r'[\s\)]+', title_ver)[1])
            sql = "insert into user values ('%s', '%s')" % (value_name, value_ver)
            cur.execute(sql)
            con.commit()
            response = requests.get(title_link)
            with open('doc/'+title_name+'.pdf','wb') as f:
                f.write(response.content)

            print('download pdf file successful', title_name)
        con.close()
        print('download all successful !!!')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main_fun()
