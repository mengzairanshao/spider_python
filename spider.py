# -*- coding: utf-8 -*-
import sys
import threading
import requests
import urllib.parse
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from sys import argv
from time import sleep
import sqlite3
import random
import re

threads = []
lock = threading.Lock()
sleep_time = 1
cat = ['Phones ', 'Accessories', 'Consumer Electronics', 'Home Appliances', 'Computer ', 'Office', 'Wigs ',
       'Hair Extensions', 'Womens Clothing', 'Mens Clothing', 'Sports ', 'Outdoors', 'Home ', 'Garden', 'Health ',
       'Beauty', 'Toys, Kids ', 'Babies', 'Shoes ', 'Bags', 'Jewelry ', 'Watches', 'Automotive ', 'Motorcycles']

cat_map = {}
num_of_getting = 100


# google搜索接口


def create_table():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    sql1 = '''CREATE TABLE '''
    sql3 = ''' (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           title TEXT,
           abstract TEXT,
           url  TEXT,
           description TEXT);'''
    try:
        for sql2 in cat:
            c.execute(sql1 + sql2.strip(' ').replace(',', ' ').replace('  ', ' ').replace(' ', '_') + sql3)
        print('Created DB')
    except sqlite3.OperationalError as e:
        print(e, file=sys.stderr)
    return


def format_url(url, params: dict = None) -> str:
    query_str = urllib.parse.urlencode(params)
    return f'{url}?{query_str}'


def get_url(params):
    url = "https://www.google.com.hk/search"
    url = format_url(url, params)
    # print(url)

    return url


def get_page(url):
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        }
        response = requests.get(url=url, headers=headers)
        # 更改编码方式，否则会出现乱码的情况
        response.encoding = "utf-8"
        # print(response.status_code)
        # print(response.text)
        if response.status_code == 200:
            return response.text
        print('status is not 200', file=sys.stderr)
        print(response.text, file=sys.stderr)
        return None
    except RequestException:
        print('request exception', file=sys.stderr)
        return None


def threads_get_description(keyword, url, m):
    html1 = get_page(url)
    if html1 is None:
        print('domain page cannot be got', file=sys.stderr)
        return
    print('ready to parse domain page')
    soup1 = BeautifulSoup(html1, "lxml")
    c2 = soup1.find(attrs={"name": "description"})
    m['description'] = ' '
    if c2 is not None:
        try:
            m['description'] = c2['content']
        except:
            print('cannot get content', file=sys.stderr)
    # 写入数据库 TODO
    lock.acquire()
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    sql1 = keyword.strip(' ').replace(',', ' ').replace(' ', '_')
    sql = 'INSERT INTO ' + sql1 + ' (title,abstract,url,description) VALUES("' + m['title'].replace('"', "'") + '","' + \
          m['abstract'].replace('"', "'") + '","' + m['url'].replace('"', "'") + '","' + m['description'].replace('"',
                                                                                                                  "'") + '")'
    print(sql)
    try:
        c.execute(sql)
        conn.commit()
        print('run this SQL ok')
    except:
        conn.rollback()
        print('error to run this SQL', file=sys.stderr)
    conn.close()
    lock.release()
    return 0


def parse_page1(keyword, page):
    params = {
        'q': str(keyword),
        'start': page * 10
    }
    print('request page')
    url = get_url(params)
    html = get_page(url)
    if html is None:
        print('page is None', file=sys.stderr)
        return
    print('page is ready')
    soup = BeautifulSoup(html, "lxml")
    num = int(re.findall(r"\d+", soup.select('#resultStats')[0].contents[0])[0])
    if num < num_of_getting:
        cat_map[keyword] = num
    c = soup.select('.bkWMgd')
    c1 = []
    for cc in c:
        if len(cc.contents) > 0 and str(cc.contents[0]).startswith('<h2 class="bNg8Rb">'):
            c1.extend(cc.select('.rc'))
    m = {'title': '', 'abstract': '', 'url': '', 'description': ''}
    for cc in c1:
        try:
            print('parse page')
            m.clear()
            m['title'] = cc.select('.r')[0].select('a')[0].select('.S3Uucc')[0].get_text()
            m['abstract'] = cc.select('.s')[0].select('.st')[0].get_text()
            m['url'] = cc.select('.r')[0].select('a')[0]['href']
            ss = m['url'].split('/')
            domain = ss[0] + '//' + ss[2]
            # 加锁保护临界资源
            t = threading.Thread(target=threads_get_description, args=(keyword, domain, m.copy()))
            t.start()
            threads.append(t)
            print('parse is ok')
        except:
            m.clear()
            print('this page cannot be parsed', file=sys.stderr)
    return


def threads_parse_page(keyword, page):
    for i in range(0, page):
        if (i + 1) * 10 > cat_map[keyword]:
            break
        t = threading.Thread(target=parse_page1, args=(keyword, i))
        t.start()
        threads.append(t)
        print('ready to start thread ', keyword, i + 1)
        sleep(random.randint(5, 20))
    return 0


def main(keyword, page, op):
    if op == 0:
        keyword = input("输入关键字:")
        page = input("输入查找页数:")
        threads_parse_page(keyword, int(page))
    random.shuffle(cat)
    for k in cat:
        threads_parse_page(k, num_of_getting)
    # threads_parse_page(keyword, int(page))
    for t in threads:
        t.join()


if __name__ == '__main__':
    create_table()
    for k in cat:
        cat_map[k] = num_of_getting * 10
    if len(argv) == 1:
        main("", "", 1)
    else:
        keyword_1 = argv[1]
        page_1 = argv[2]
        main(keyword_1, page_1, 1)
