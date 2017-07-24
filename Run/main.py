# -*- coding: utf-8 -*-
import sys
from multiprocessing import Process

"""
-------------------------------------------------
   File Name：     main.py  
   Description :  运行主函数
   Author :       JHao
   date：          2017/4/1
-------------------------------------------------
   Change Activity:
                   2017/4/1: 
-------------------------------------------------
"""
__author__ = 'JHao'
sys.path.append('../')

from Api.ProxyApi import run as ProxyApiRun
from Schedule.ProxyValidSchedule import run as ValidRun
from Schedule.ProxyRefreshSchedule import run as RefreshRun


def run():
    p_list = list()
    p1 = Process(target=ProxyApiRun, name='ProxyApiRun')
    p_list.append(p1)
    p2 = Process(target=ValidRun, name='ValidRun')
    p_list.append(p2)
    p3 = Process(target=RefreshRun, name='RefreshRun')
    p_list.append(p3)
    for p in p_list:
        p.daemon = True
        p.start()
        with open(p.name + '.pid', 'w') as pid_file:
            pid_file.write(str(p.pid))
    for p in p_list:
        p.join()

if __name__ == '__main__':
    run()
