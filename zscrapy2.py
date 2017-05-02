# -*- coding: utf-8 -*-
import urllib2
import re
import bs4
import urlparse
import datetime
import time
import os

import threading

import logging
import logging.config

import ztest

#logging.basicConfig(level="DEBUG")
logging.config.fileConfig("logger.config")
logger = logging.getLogger("example01")


from zcache import ZCache
from zdatabase import ZDownData

class ZDownload(object):
    
    def __init__(self,delay=5,agent="bergy",proxy=None,num_retries=1,use_cache=0,cache=None):
        
        self.throttle=Throttle(delay)
        self.agent=agent
        self.proxy=proxy
        self.num_retries=num_retries
        
        self.use_cache=use_cache
        #use_cache=1,lib作为cache;use_cache=2,文件系统作为缓存
        
        self.cache=cache
        #ZCache类文件,或None
    def __call__(self,url):
        
        html=None
        
        if self.use_cache:
            
            try:
                html=self.cache[url]
                
                logging.debug("HTML LOAD")
            
            except KeyError as error:
                
                logging.info("There is no %s" % url)
               
                html=None
        
        
        if html==None: 
            
            #self.throttle.wait(url)
            
            headers={"User-agent":self.agent}
            
            html=self.download(url,headers,self.num_retries)
            
            if self.use_cache:
                
                self.cache[url]=html

        return html

    def download(self,url,agent="bergy",retry=2):
        
        print("Downloading Start:",url)
        
        headers={'User-agent':agent}
        
        request=urllib2.Request(url,headers=headers)

        try:
            html=urllib2.urlopen(request).read()
        
        except urllib2.URLError as error:
            
            logging.info("Download Error",error.reason)
            
            html=None
            
            if retry>0 and 500<=error.code<600:
                html=download(url,retry-1)
        
        return html
    
    def cacheRefresh(self):
        
        #更新数据库中的记录表单
        
        self.cache.refresh()
        
        
        
        
        


class Throttle():
    def __init__(self,delay):
        self.delay=delay
        self.domains={}

    def wait(self,url):
        domain=urlparse.urlparse(url).netloc
        last_accessed=self.domains.get(domain)
        if self.delay>0 and last_accessed is not None:
            timerecord=datetime.datetime.now()
            sleep_secs=self.delay-(timerecord-last_accessed).seconds
            if sleep_secs>0:
               time.sleep(sleep_secs)
        self.domains[domain]=timerecord



class ZCrawler():

    def __init__(self,delay=5,agent="bergy",proxy=None,num_retries=1,use_cache=1,cache=None):
        
        self.Downloader=ZDownload(delay,agent,proxy,num_retries,use_cache,cache)
        
        
    def __call__(self,url,max_depth=-1,max_iteration=-1,threads=1,cat="LINK"):

        if cat=="LINK":
            
            print("Link Crawler Started")
            
            result=self.link_crawler(url,max_depth,max_iteration)
            
        elif cat=="THREAD":
            
            print("Thread Crawler Started")
            
            result=self.threaded_crawler(url,max_depth,max_iteration,threads)
            
        else:
            
            print("Crawler Not Started")
            
        return result
        
        #!Whether or not call method needs a return?
        
    def map_crawler(self,url):
        sitemap=download(url)
        links=re.findall('<loc>(.*?)</loc>',sitemap)
        for link in links:
            print link
        pass

        
    def link_crawler(self,seed_url,max_depth=-1,max_iteration=-1):
                
        #原始网页,scrap网页历史记录,最大数量
        crawl_queue=[seed_url]
        
        seen_queue={seed_url:0}
        
        count=0
        
        #循环内容
        
        while crawl_queue:  
            #深度定义
            
            while count!=max_iteration:
                #while crawl_queue
                
                try:
                    
                    url=crawl_queue.pop()
                
                except Exception,error:
                    
                    print("Pop error %s Counter to %s" % (error,count))
                    break
                
                depth=seen_queue[url]    
                
                #logging.debug("link_crawler depth=%s" % depth) 
                
                html=self.Downloader(url)
                
                if html:
                    
                    url_list=self.get_links(html)
                        
                    if depth!= max_depth:
                            
                        for new_url in url_list:
                             
                            if new_url not in seen_queue:
                                #更新URL列表
                                crawl_queue.append(new_url)
                                seen_queue[new_url]=depth+1
                    
                count=count+1
                
            print("Counter to %s" % count)
            break
            
        self.Downloader.cacheRefresh()
        
        #!!Method Refresh Cache       
        
    
    
    def get_links(self,html):
        
        link_list=[]
        
        bs4obj=bs4.BeautifulSoup(html)
        
        
        h2content=bs4obj.find_all("a",href=re.compile("^/((?!\?)(?!\:).)*$"))
        #!好的正则!
        
        url_base="http://www.eu4wiki.com"
        
        for link in h2content:
            new_url=urlparse.urljoin(url_base,link["href"])
            
            link_list.append(new_url)
            
        #暂时直接在get_links内全部过滤好
        
        eu_filter=lambda x:re.match(".+eu4",x)
        
        link_list=filter(eu_filter,link_list)
        
        return link_list



    def links_filter(seed_url,url,link_regex):
        
        urlparse.urljoin(seed_rul,url.a["href"])
        
        return 1
    
    def threaded_test(self):
        
        time.sleep(1)
        
        print "haha"
    
    
    def threaded_crawler(self,seed_url,max_depth=-1,max_iteration=-1,max_thread=1):
        
        crawl_queue=[seed_url]
        #总queue
        
        seen_queue={seed_url:0}
        
        def thread_pop():
            
            print 'thread %s is running...' % threading.current_thread().name
            
            #time.sleep(5)
            
            #print 'thread %s start up after 5s...' % threading.current_thread().name
            
            count=0
            
            while crawl_queue:  
                #深度定义
                
                while count != max_iteration:
                    #while crawl_queue
                    
                    #time.sleep(0.5)
                    
                    try:
                        url=crawl_queue.pop()
                    
                    except Exception,error:
                        
                        print("Pop error %s Counter to %s" % (error,count))
                        break
                    
                    depth=seen_queue[url]    
                    
                    #logging.debug("link_crawler depth=%s" % depth) 
                    
                    html=self.Downloader(url)
                    
                    print 'thread %s is downloading...' % threading.current_thread().name
                    
                    if html:
                        
                        url_list=self.get_links(html)
                            
                        if depth!= max_depth:
                                
                            for new_url in url_list:
                                 
                                if new_url not in seen_queue:
                                    #更新URL列表
                                    crawl_queue.append(new_url)
                                    seen_queue[new_url]=depth+1
                        
                    count=count+1
                    
                print("%s Counter to %s" % (threading.current_thread().name,count))
                
                break
            
            print 'thread %s Done' % threading.current_thread().name    
        
        self.Downloader.cacheRefresh()
            
            #!!Method Refresh Cache       
        
        threads=[]
        
        crawl_counter={}
        
        for num in range(0,max_thread):
            
            thread_str="Thread"+str(num)
            
            thread_name=threading.Thread(target=thread_pop,name=thread_str)
            
            threads.append(thread_name)
            
            crawl_counter[thread_str]=0
        
  
        for thread in threads:
            
            print("Thread %s Start" % thread.name)
            
            thread.start()
            
            time.sleep(20)

        for thread in threads:
            
            thread.join()    
        
        print("Threads All End")   
        
    def process_queue(self):
        pass

        

if __name__=="__main__":
    
    
    ztest.zscrapy2_test_thread()







