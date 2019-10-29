# -*- coding: utf-8 -*-
import requests
import urllib.parse
from requests.exceptions import RequestException
from urllib.parse import urljoin
from lxml import etree
import re
import json
from sys import argv
import os, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


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


def parse_page(url, page):
    for i in range(1, int(page) + 1):
        # print("正在爬取第{}页....".format(i))
        title = ""
        sub_url = ""
        abstract = ""
        flag = 11
        if i == 1:
            flag = 10
        html = get_page(url)
        html = html.replace(u'\xa0', u' ')
        content = etree.HTML(html)
        a=content.xpath('//*[@id="rso"]')
        for j in range(1, flag):
            data = {}
            res_title = content.xpath('//*[@id="rso"]/div[%d]/div/div[1]/div/div[1]/a/h3' % j)
            if res_title:
                title = res_title[0].xpath('string(.)')

            sub_url = content.xpath('//*[@id="rso"]/div[%d]/div/div[1]/div/div[1]/a/@href' % j)
            if sub_url:
                sub_url = sub_url[0]

            res_abstract = content.xpath('//*[@id="rso"]/div[%d]/div/div[1]/div/div[2]/div[1]' % j)
            if res_abstract:
                abstract = res_abstract[0].xpath('string(.)')
            else:
                res_abstract = content.xpath('//*[@id="%d"]/div/div[2]/div[@class="c-abstract"]' % ((i - 1) * 10 + j))
                if res_abstract:
                    abstract = res_abstract[0].xpath('string(.)')
                    # res_abstract = content.xpath('//*[@id="%d"]/div/div[2]/p[1]'%((i-1)*10+j))
            # if not abstract:
            #     abstract = content.xpath('//*[@id="%d"]/div/div[2]/p[1]'%((i-1)*10+j))[0].xpath('string(.)')
            data['title'] = title
            data['sub_url'] = sub_url
            data['abstract'] = abstract

            # rel_url = content.xpath('//*[@id="nav"]/tbody/tr/td[{}]/a/@href'.format(flag))
            # if rel_url:
            #     url = urljoin(url, rel_url[0])
            # else:
            #     # print("无更多页面！～")
            #     return
            yield data


def main(keyword, page, op):
    if op == 0:
        keyword = input("输入关键字:")
        page = input("输入查找页数:")
    url = get_url(keyword)

    results = parse_page(url, page)
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
