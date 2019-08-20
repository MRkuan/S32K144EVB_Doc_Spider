#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ref doc
# http://docs.python-requests.org/zh_CN/latest/user/quickstart.html      request
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.zh.html    BeautifulSoup
# http://www.w3school.com.cn/h.asp                                       w3school
# http://www.runoob.com/sqlite/sqlite-python.html                        sqlite python ref
# https://blog.csdn.net/zwq912318834/article/details/79571110            Simulation login
# https://www.cnblogs.com/liujiacai/p/7804848.html                       logging
# https://zhidao.baidu.com/question/588558497.html                       windows timer task
 
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

import yaml
import logging

base_url = r'https://www.nxp.com/products/processors-and-microcontrollers/arm-processors/s32-automotive-platform/32-bit-automotive-general-purpose-microcontrollers:S32K?tab=Documentation_Tab'

header = {
"Referer": r"https://www.nxp.com/security/login?TARGET=https://www.nxp.com/ruhp/myAccount.html",
"User-Agent": r"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
}
postUrl = r"https://www.nxp.com/security/login?TARGET=https://www.nxp.com/ruhp/myAccount.html"
postData = {
    "lt": "",
    "execution": "",
    "_eventId": "",
    "username": "",
    "password": "",
}

#email config ,please care, do not let out
email_send_user = ''
email_send_password = ''
email_send_addr = ''
email_rcv_addr = []
email_host = ''
email_port = 0

nxp_email_address = ''
nxp_password = ''

old_list = [] #old list link name ver
new_list = [] #new list link name ver

admin_flag = 0

nxp_session = requests.Session()

log_name = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S-')+ 'log.txt'
cfg_Path = os.path.join(os.path.dirname(__file__),'main_cfg.yaml')
log_path = os.path.join(os.path.dirname(__file__),'log')
db_path = os.path.join(os.path.dirname(__file__),'main.db')
doc_path = os.path.join(os.path.dirname(__file__),'doc')

def list_cmp(__old_list,__new_list):
    if len(__old_list) != len(__new_list):
        return False

    for i in range(len(__old_list)):
        if not(len(__old_list[i]) == len(__new_list[i])):
            return False    

    for i in range(len(__old_list)):
        for j in range(len(__old_list[i])):
            if not(operator.eq(__old_list[i][j][0],__new_list[i][j][0])):
                return False
            if not(operator.eq(__old_list[i][j][1],__new_list[i][j][1])):
                return False
            if not(__old_list[i][j][2] == __new_list[i][j][2]):
                return False
    return True

def del_file(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)

def delete_gap_dir(dir):
    if os.path.isdir(dir):
        for d in os.listdir(dir):
            delete_gap_dir(os.path.join(dir, d))
    if not os.listdir(dir):
        os.rmdir(dir)

def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title

def main_fun():
    try:
        # 1. logging set
        logger = logging.getLogger(__name__)
        logger.setLevel(level = logging.INFO)
        handler = logging.FileHandler(os.path.join(log_path,log_name))
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)

        logger.addHandler(handler)
        logger.addHandler(console)
        logger.info('1.set logging sucessfull')
  
        # 2. read cfg
        content = yaml.load(open(cfg_Path))

        email_send_user = content['email_send_user']
        email_send_password = content['email_send_password']
        email_send_addr = content['email_send_addr']
        email_host = content['email_host']
        email_port = content['email_port']

        nxp_email_address = content['nxp_email_address']
        nxp_password = content['nxp_password']
        logger.info('2.read cfg sucessfull')

        # 3.Simulation on nxp
        nxp_page = nxp_session.get(postUrl, allow_redirects = False)
        nxp_soup = BeautifulSoup(nxp_page.content,"html.parser")

        postData["lt"] = nxp_soup.find('input', {'name': 'lt'}).get('value')
        postData["execution"] = nxp_soup.find('input', {'name': 'execution'}).get('value')
        postData["_eventId"] = nxp_soup.find('input', {'name': '_eventId'}).get('value')
        postData["username"] = nxp_email_address
        postData["password"] = nxp_password

        responseRes = nxp_session.post(postUrl,data = postData, headers = header)
        logger.info('3.Simulation on nxp sucessfull')
        # print(f"statusCode = {responseRes.status_code}")
        # print(f"text = {responseRes.text}")

        #4. analyze baseurl
        page = nxp_session.get(base_url, allow_redirects = False)
        soup = BeautifulSoup(page.content,"html.parser")

        logger.info('4.analyze baseurl')
        logger.info('--------------------------')
        # ref: https://segmentfault.com/q/1010000004828602
        for item in soup.find_all('table',class_ = re.compile('table')):
            logger.info(item.get('data-dtmtablename'))
            tmp_new_list = []
            tmp_new_list.append(['',item.get('data-dtmtablename'),0.0])
            for tr_item in item.find('tbody',class_ = 'wraptable').find_all('tr'):
                tmpList = tr_item.find_all('ul',class_ = re.compile('docList'))
                title_item = tmpList[0].find('li',class_ = re.compile('docTitle'))
                title_link = "https://www.nxp.com/" +title_item.contents[0].get('href')
                title_name = title_item.contents[0].find('strong').get_text().strip()
                if len(title_item.contents) == 1 :
                    title_ver = '(REV 0)'
                else:
                    title_ver = title_item.contents[1].get_text().strip()
                title_name = title_name + title_ver

                value_name = title_name
                value_ver =  float(re.split(r'[\s\)]+', title_ver)[1])

                logger.info('-------')
                logger.info('link: %s | name: %s | ver: %s' %(title_link,value_name,value_ver))
          
                tmp_new_list.append([title_link,value_name.replace(':',','),value_ver])

                if len(tmpList) == 1 :
                    pass #todo: alone pdf
                else:
                    pass #todo: Related file
            new_list.append(tmp_new_list)
            logger.info('--------------------------')

        #5. read sqlite data
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        for i in range(len(new_list)):
            table_name = 'user%d' %(i)
            cmd = 'create table if not exists %s (link STRING, name STRING, ver DOUBLE)' %(table_name)
            cmd_select = 'select * from %s' %(table_name)

            cur.execute(cmd)
            tmp_old_list = cur.execute(cmd_select).fetchall()
            old_list.append(tmp_old_list)
        logger.info('5.read sqlite data sucess full')
        # if not eq then download file
        if not(list_cmp(old_list,new_list)) :
            # print(old_list)
            # print(new_list)
            logger.info('doc upadte!!!')
            # 6 delete doc file
            dir = doc_path
            if os.path.exists(dir) :
                del_file(dir)
                delete_gap_dir(dir)
                if not(os.path.exists(dir)) :
                    os.mkdir(dir)
            else:
                os.mkdir(dir)
            logger.info('6.delete doc floder file')

            # 7 download file
            tmp_dir = ''
            for list_item in new_list:
                for item in list_item:
                    if (0 == list_item.index(item)):
                        tmp_dir = os.path.join(dir,item[1])
                        os.mkdir(tmp_dir)
                        logger.info('create floder：%s' %(tmp_dir))
                    else:
                        file_link = item[0]
                        file_name = validateTitle(item[1]) # filter illegality character

                        if(file_link.endswith('.pdf')) :
                            response = nxp_session.get(file_link, allow_redirects = False)
                            with open(os.path.join(tmp_dir,file_name+'.pdf'),'wb') as f:
                                f.write(response.content)
                            logger.info('download pdf：%s suessful' %(file_name+'.pdf'))
                        elif(file_link.endswith('.zip')) :
                            response = nxp_session.get(file_link, allow_redirects = False)
                            with open(os.path.join(tmp_dir,file_name+'.zip'),'wb') as f:
                                f.write(response.content)
                            logger.info('download zip：%s suessful' %(file_name+'.zip'))
                        else:
                            response = nxp_session.get(file_link,allow_redirects = True, headers = header)
                            # print(f"statusCode = {response.status_code}")
                            # print(f"text = {response.text}")
                            soup = BeautifulSoup(response.content,"html.parser")
                            tmp_link =''
                            try:
                                tmp_link= soup.find('div',class_='col-md-1 col-md-offset-2 text-center').find('a').get("href")
                            except:
                                file_link = file_link[len("https://www.nxp.com/"):].strip()
                                response = nxp_session.get(file_link, allow_redirects=False, headers=header)
                                soup = BeautifulSoup(response.content, "html.parser")
                                tmp_link = soup.find('div',class_='jive-attachments').find('a',class_='j-attachment-icon').get("href")
                                tmp_link = "https://community.nxp.com/" + tmp_link
                            response = nxp_session.get(tmp_link, allow_redirects = False)
                            if(tmp_link.endswith('.pdf')) :
                                with open(os.path.join(tmp_dir,file_name+'.pdf'),'wb') as f:
                                    f.write(response.content)
                                logger.info('download pdf：%s suessful' %(file_name+'.pdf'))
                            elif(tmp_link.endswith('.zip')) :
                                with open(os.path.join(tmp_dir,file_name+'.zip'),'wb') as f:
                                    f.write(response.content)
                                logger.info('download zip %s suessful' %(file_name+'.zip'))

            logger.info('download all suessful')

            # 8 save new list
            for i in range(len(new_list)):
                table_name = 'user%d' %(i)
                cmd = 'create table if not exists %s (link STRING, name STRING, ver DOUBLE)' %(table_name)
                cmd_delete = 'delete from %s' %(table_name)

                cur.execute(cmd_delete)
                cur.execute(cmd)
            for i in range(len(new_list)):
                table_name = 'user%d' %(i)
                for item in new_list[i]:
                    sql = "insert into %s values ('%s', '%s', '%s')" % (table_name,item[0], item[1], item[2])
                    cur.execute(sql)
            cur.close()
            con.commit()
            con.close()  
            logger.info('8.save new list successful !!!')
            admin_flag = 0
        else:
            logger.info('doc no change')
            admin_flag = 1
    except Exception as e:
        logger.error(e)
        admin_flag = 1
    finally:
        # finally: email notify
        if (0 == admin_flag):
            email_rcv_addr = content['email_rcv_addr']
            logger.info('email to everyone')
        else:
            email_rcv_addr = content['email_rcv_admin_addr']
            logger.info('email to adimn')

        message = MIMEMultipart()
        name, addr = parseaddr("%s <%s>" % (email_send_user,email_send_addr))
        message['From'] = formataddr((Header(name, 'utf-8').encode(), addr))
        message['To'] = Header("; ".join(email_rcv_addr),'utf-8')
        message['Subject'] = Header('[update] S32k144 document update', 'utf-8')
        tmp_txt = '[doc_url]: ' + base_url + '\r\n' + '[doc_download_path]:' + doc_path + '\r\n'  + '[log_download_file]:' + os.path.join(log_path,log_name)
        message.attach(MIMEText(tmp_txt, 'html', 'utf-8'))

        # att = MIMEText(open(os.path.join(log_path,log_name), 'rb').read(), 'base64', 'utf-8')
        # att["Content-Type"] = 'application/octet-stream'
        # att["Content-Disposition"] = 'attachment; filename="' + log_name + '"'
        # message.attach(att)

        smtpObj = smtplib.SMTP(email_host, email_port)

        smtpObj.login(email_send_user, email_send_password)

        smtpObj.sendmail(email_send_addr, email_rcv_addr, message.as_string())
        smtpObj.quit()

if __name__ == '__main__':
     main_fun()
