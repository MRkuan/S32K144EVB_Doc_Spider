#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ref doc
# http://docs.python-requests.org/zh_CN/latest/user/quickstart.html      request
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.zh.html    BeautifulSoup
# http://www.w3school.com.cn/h.asp                                       w3school
# http://www.runoob.com/sqlite/sqlite-python.html                        sqlite python ref

import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from urllib import request
from email.utils import parseaddr, formataddr
import requests
from bs4 import BeautifulSoup
import sqlite3
import datetime
import re
import operator
import os

base_url = r'https://www.nxp.com/support/developer-resources/evaluation-and-development-boards/analog-toolbox/s32k144-evaluation-board:S32K144EVB?&tab=Documentation_Tab&lang=en&lang_cd=en&'
base_download_url = r'https://www.nxp.com/'

#email config ,please care, do not let out
email_send_user = ''
email_send_password = ''
email_send_addr = ''
email_rcv_addr = ['']
email_host = ''
email_port = 0

old_list = [] #old list link name ver
new_list = [] #new list link name ver

def list_cmp(__old_list,__new_list):
    if len(__old_list) != len(__new_list):
        return False

    for i in range(len(__old_list)):
        if not(operator.eq(__old_list[i][0],__new_list[i][0])):
            return False
        if not(operator.eq(__old_list[i][1],__new_list[i][1])):
            return False
        if not(__old_list[i][2] == __new_list[i][2]):
            return False
    return True

def main_fun():
    try:
        page = requests.get(base_url)
        con = sqlite3.connect("main.db")
        cur = con.cursor()
        cur.execute('create table if not exists user (link STRING, name STRING, ver DOUBLE)')
        old_list = cur.execute('select * from user').fetchall()
        new_list.clear();
        soup = BeautifulSoup(page.content,"html.parser")

        for item in soup.find_all('li','relatedDocs-docTitle'):
            title_link = base_download_url +item.contents[0].get('href')
            title_name = item.contents[0].find('strong').get_text().strip()
            title_ver = item.contents[1].get_text().strip()
            title_name = title_name + title_ver

            value_name = title_name
            value_ver =  float(re.split(r'[\s\)]+', title_ver)[1])
            new_list.append([title_link,value_name,value_ver])

        # if not eq then download file
        if not(list_cmp(old_list,new_list)) :
            print(old_list)
            print(new_list)

            # 1 save new list
            cur.execute("delete from user")
            cur.execute('create table if not exists user (link STRING, name STRING, ver DOUBLE)')
            for item in new_list:
                sql = "insert into user values ('%s', '%s', '%s')" % (item[0], item[1], item[2])
                cur.execute(sql)
            cur.close()
            con.commit()
            con.close()

            # # 2 delete doc file
            # dir = os.path.join(os.path.abspath('.'),'doc')
            # if os.path.exists(dir) :
            #     for item in os.listdir(dir):
            #          os.remove(os.path.join(dir,item))
            # else:
            #     os.mkdir(dir)

            # # 3 download file
            # for item in new_list:
            #     file_link = item[0]
            #     file_name = item[1]
            #     response = requests.get(file_link)
            #     with open(os.path.join(os.path.abspath('.'),'doc',file_name+'.pdf'),'wb') as f:
            #         f.write(response.content)
            #     print('download pdf file successful', file_name)
            # print('download all successful !!!')

            # 4 email notify
            message = MIMEMultipart()
            name, addr = parseaddr('S32k144_document_updater <%s>' % email_send_addr)

            message['From'] = formataddr((Header(name, 'utf-8').encode(), addr))
            message['To'] = Header("; ".join(email_rcv_addr),'utf-8')
            message['Subject'] = Header('[update] S32k144 document update', 'utf-8')
            message.attach(MIMEText(base_url, 'plain', 'utf-8'))

            file_paths = []
            file_names = []

            for item in new_list:
                file_name = item[1]
                file_paths.append(os.path.join(os.path.abspath('.'),'doc',file_name+'.pdf'))
                file_names.append(file_name +'.pdf')

            for file_path, file_name in zip(file_paths, file_names):
                att = MIMEText(open(file_path, 'rb').read(), 'base64', 'utf-8')
                att["Content-Type"] = 'application/octet-stream'
                att["Content-Disposition"] = 'attachment; filename="' + file_name + '"'
                message.attach(att)

            # smtpObj = smtplib.SMTP(email_host, email_port)
            smtpObj = smtplib.SMTP_SSL(email_host, email_port)

            smtpObj.login(email_send_user, email_send_password)
            smtpObj.sendmail(email_send_addr, email_rcv_addr, message.as_string())
            smtpObj.quit()
            print('email notify successful !!!')
        else:
            print('no change')
    except Exception as e:
        print(e)

if __name__ == '__main__':
     main_fun()
