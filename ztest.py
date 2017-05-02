# -*- coding: utf-8 -*-
import logging
import os
import datetime
import time

from zcache import ZCache
from zscrapy2 import ZDownload
from zscrapy2 import ZCrawler

def zscrapy2_test4():
    #数据库下载测试
    a=time.time()
    
    logging.info("Start")
    
    url="http://www.eu4wiki.com/Europa_Universalis_4_Wiki"
    
    z=ZDownData("pta.db")
    
    B=ZCache(category=4,cache_dir="zcachex",cache_db=z)
    
    Z=ZCrawler(delay=1,cache=B)
    
    Z(url,1,5)
    
    b=time.time()
    
    print "Runing %s seconds"% (b-a)
    
    print Z.Downloader.cache
    

def zscrapy2_test_thread():
    
    a=time.time()
    
    logging.info("Start")
    
    url="http://www.eu4wiki.com/Europa_Universalis_4_Wiki"
    
    B=ZCache(category=2,cache_dir="thread4")
    
    Z=ZCrawler(delay=1,cache=B)
    
    Z(url,1,50,2,cat="THREAD")
    #url,max_depth=-1,max_iteration=-1,threads=1,cat="LINK"
    
    b=time.time()