# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyValidSchedule.py
   Description :  验证useful_proxy_queue中的代理,将不可用的移出
   Author :       JHao
   date：          2017/3/31
-------------------------------------------------
   Change Activity:
                   2017/3/31: 验证useful_proxy_queue中的代理
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
from time import sleep

sys.path.append('../')

from Util.utilFunction import validUsefulProxy
from Manager.ProxyManager import ProxyManager
from Util.LogHandler import LogHandler
from Queue import Queue
from threading import Thread

MAX_THREADS = 20
proxies_queue = Queue(maxsize=MAX_THREADS)


class ProxyValidSchedule(ProxyManager):
    def __init__(self):
        ProxyManager.__init__(self)
        self.log = LogHandler('valid_schedule')
        self.db.changeTable(self.useful_proxy_queue)

    def __validProxy(self):
        """
        验证代理
        :return:
        """
        def valid_proxy_in_queue():
            while True:
                proxy = proxies_queue.get()
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')

                if validUsefulProxy(proxy):
                    # 成功->计数器加1
                    self.db.inckey(proxy, 1)
                    self.log.debug('validProxy_b: {} validation pass'.format(proxy))
                else:
                    # 失败->计数器减一
                    self.db.inckey(proxy, -1)
                    # self.db.delete(proxy)
                    self.log.info('validProxy_b: {} validation fail'.format(proxy))
                value = self.db.getvalue(proxy)
                if value and int(value) < -5:
                    # 计数器小于-5删除该代理
                    self.db.delete(proxy)

        for i in range(MAX_THREADS):
            thread = Thread(target=valid_proxy_in_queue)
            thread.daemon = True
            thread.start()

        while True:
            for each_proxy in self.db.getAll():
                proxies_queue.put(each_proxy)
            sleep(300)

    def main(self):
        self.__validProxy()


def run():
    p = ProxyValidSchedule()
    p.main()


if __name__ == '__main__':
    p = ProxyValidSchedule()
    p.main()
