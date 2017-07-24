# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     GetFreeProxy.py
   Description :  抓取免费代理
   Author :       JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: 
                   这一部分考虑用scrapy框架代替
-------------------------------------------------
"""
import re
import requests
from bs4 import BeautifulSoup
import sys

try:
    from importlib import reload   #py3 实际不会实用，只是为了不显示语法错误
except:
    reload(sys)
    sys.setdefaultencoding('utf-8')
sys.path.append('..')
test_url = "https://mainsite-restapi.ele.me/shopping/restaurant/155154177?extras[]=activities"

from Util.utilFunction import robustCrawl, getHtmlTree, getHTMLText

# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()

HEADER = {'Connection': 'keep-alive',
          'Cache-Control': 'max-age=0',
          'Upgrade-Insecure-Requests': '1',
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Encoding': 'gzip, deflate, sdch',
          'Accept-Language': 'zh-CN,zh;q=0.8',
          }


class GetFreeProxy(object):
    """
    proxy getterf
    """

    def __init__(self):
        pass

    @staticmethod
    @robustCrawl    # decoration print error if exception happen
    def freeProxyFirst(page=10):
        """
        抓取快代理IP http://www.kuaidaili.com/
        :param page: 翻页数
        :return:
        """
        url_list = ('http://www.kuaidaili.com/proxylist/{page}/'.format(page=page) for page in range(1, page + 1))
        # 页数不用太多， 后面的全是历史IP， 可用性不高

        for url in url_list:
            content = requests.request(method='get', url=url, headers=HEADER).content
            soup = BeautifulSoup(content, 'lxml')
            proxy_list = soup.find_all('tr')
            for proxy in proxy_list:
                ip = proxy.find('td', {'data-title': 'IP'})
                port = proxy.find('td', {'data-title': 'PORT'})
                if ip and port:
                    yield ip.text + ':' + port.text


    @staticmethod
    @robustCrawl
    def freeProxySecond(proxy_number=100):
        """
        抓取代理66 http://www.66ip.cn/
        :param proxy_number: 代理数量
        :return:
        """
        url = "http://m.66ip.cn/mo.php?sxb=&tqsl={}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=".format(
            proxy_number)

        html = getHTMLText(url, headers=HEADER)
        if html:
            for proxy in re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5})<br />', html):
                yield proxy

    @staticmethod
    @robustCrawl
    def freeProxyThird(days=1):
        """
        抓取有代理 http://www.youdaili.net/Daili/http/
        :param days:
        :return:
        """
        url = "http://www.youdaili.net/Daili/http/"
        tree = getHtmlTree(url)
        page_url_list = tree.xpath('.//div[@class="chunlist"]/ul/li/p/a/@href')[0:days]
        for page_url in page_url_list:
            html = requests.get(page_url, headers=HEADER).content
            # print html
            proxy_list = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', html)
            for proxy in proxy_list:
                yield proxy

    @staticmethod
    @robustCrawl
    def freeProxyFourth():
        """
        抓取西刺代理 http://api.xicidaili.com/free2016.txt
        :return:
        """
        url_list = ['http://www.xicidaili.com/nn',  # 高匿
                    'http://www.xicidaili.com/nt',  # 透明
                    ]
        for each_url in url_list:
            tree = getHtmlTree(each_url)
            proxy_list = tree.xpath('.//table[@id="ip_list"]//tr')
            for proxy in proxy_list:
                yield ':'.join(proxy.xpath('./td/text()')[0:2])

    @staticmethod
    @robustCrawl
    def freeProxyFifth(page=10):
        """
        抓取guobanjia http://www.goubanjia.com/free/gngn/index.shtml
        :return:
        """
        url = "http://www.goubanjia.com/free/gngn/index{page}.shtml"
        for idx in range(1, page + 1):
            page_url = url.format(page=idx)
            content = requests.request(method='get', url=page_url, headers=HEADER).text
            soup = BeautifulSoup(content, 'lxml')
            proxy_list = soup.find_all('td', class_='ip')
            for each_proxy in proxy_list:
                yield ''.join([
                    _.string
                    for _ in each_proxy.children
                    if ("display: none;" not in str(_) and "display:none;" not in str(_)) and _.string
                ])

if __name__ == '__main__':
    from collections import Counter
    from time import time, sleep
    from threading import Thread
    gg = GetFreeProxy()

    def debug_proxies(proxy):
        if proxy:
            try:
                t1 = time()
                response = requests.get(url=test_url, proxies={'https': proxy}, timeout=10)
                fetch_times.append(int(time() - t1))
            except Exception as e:
                print e
                fetch_times.append(None)
    counter = Counter()
    for i in range(100):
        fetch_times = []
        threads = []
        print('proxy1:')
        for proxy in gg.freeProxyFirst(1):
            # print proxy
            thread = Thread(target=debug_proxies, args=(proxy,))
            threads.append(thread)
            thread.start()

        print('proxy2:')
        for proxy in gg.freeProxySecond():
            # print proxy
            thread = Thread(target=debug_proxies, args=(proxy,))
            threads.append(thread)
            thread.start()

        #print('proxy3:')
        #for e in gg.freeProxyThird():
        #    print e

        print('proxy4:')
        for proxy in gg.freeProxyFourth():
            # print proxy
            thread = Thread(target=debug_proxies, args=(proxy,))
            threads.append(thread)
            thread.start()

        print("proxy5:")
        for proxy in gg.freeProxyFifth(1):
            # print proxy
            thread = Thread(target=debug_proxies, args=(proxy,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        cur_counter = Counter(fetch_times)
        counter += cur_counter
        for key in sorted(cur_counter.keys()):
            print "time:", key, "count:", cur_counter[key]
            with open("proxy_statistics_{}.csv".format(i), 'a') as wf:
                wf.write('{},{}\n'.format(key, cur_counter[key]))
        sleep(60)

    for key in sorted(counter.keys()):
        print "time:", key, "count:", counter[key]
        with open("proxy_statistics_all.csv", 'a') as wf:
            wf.write('{},{}\n'.format(key, counter[key]))
