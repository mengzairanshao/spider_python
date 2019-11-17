# -*- coding: utf-8 -*-
import requests
import urllib.parse

from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from urllib.parse import urljoin
from lxml import etree
import re
import json
from sys import argv
import os, sys, io


# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# 百度搜索接口

def format_url(url, params: dict = None) -> str:
    query_str = urllib.parse.urlencode(params)
    return f'{url}?{query_str}'


def get_url(keyword):
    params = {
        'q': str(keyword)
    }
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
        return None
    except RequestException:
        return None


def parse_page1(url, page):
    html = get_page(url)
    soup = BeautifulSoup(html, "lxml")
    c = soup.select('.bkWMgd')
    c1 = []
    for cc in c:
        if len(cc.contents) > 0 and str(cc.contents[0]).startswith('<h2 class="bNg8Rb">'):
            c1.extend(cc.select('.rc'))
    rt = []
    m = {'title': '', 'abstract': '', 'url': '', 'description': ''}
    for cc in c1:
        m['title'] = cc.select('.r')[0].select('a')[0].select('.S3Uucc')[0].get_text()
        m['abstract'] = cc.select('.s')[0].select('.st')[0].get_text()
        m['url'] = cc.select('.r')[0].select('a')[0]['href']
        ss = m['url'].split('/')
        domain = ss[0] + '//' + ss[2]
        html1 = get_page(domain)
        soup1 = BeautifulSoup(html1, "lxml")
        c2 = soup1.find(attrs={"name": "description"})
        if c2 is not None:
            m['description'] = c2['content']
        rt.append(m.copy())
    return rt


def main(keyword, page, op):
    if op == 0:
        keyword = input("输入关键字:")
        page = input("输入查找页数:")
    url = get_url(keyword)

    results = parse_page1(url, page)
    for result in results:
        for k in result.keys():
            print(result[k])
            print("<br>")
        print("<br><br>")
    # 写入文件
    # file = open("data.json", 'w+', encoding='utf-8')
    # for result in results:
    #     print(result)
    #     file.write(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    if len(argv) == 1:
        main("", "", 0)
    else:
        keyword = argv[1]
        page = argv[2]
        main(keyword, page, 1)
