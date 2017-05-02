# -*- coding: utf-8 -*-
import urllib2
import re
import bs4
import urlparse
import datetime
import time
import os

from zdatabase import ZDownData

class ZDownload(object):
    
    def __init__(self,delay=5,agent="bergy",proxy=None,num_retries=1,cache=None):
        
        self.throttle=Throttle(delay)
        self.agent=agent
        self.proxy=proxy
        self.num_retries=num_retries
        self.cache=cache

    def __call__(self,url):
        
        result=None
        
        if self.cache:
            try:
                result=self.cache[url]
            except KeyError as error:
                print url, "is not in the cache"

        if result is not None:
            self.throttle.wait(url)
            headers={"User-agent":self.agent}
            result=self.download(url,headers,self.num_retries)
            self.cache[url]=result

        return result


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

def download(url,agent="bergy",retry=2):
    print "Downloading Start:",url
    headers={'User-agent':agent}
    request=urllib2.Request(url,headers=headers)

    try:
        html=urllib2.urlopen(request).read()
    except urllib2.URLError as error:
        print "Download Error",error.reason
        html=None
        if retry>0 and 500<=error.code<600:
            html=download(url,retry-1)
    return html

def map_crawler(url):
    sitemap=download(url)
    links=re.findall('<loc>(.*?)</loc>',sitemap)
    for link in links:
        print link

def link_crawler(seed_url,max_iteration=100):
    
    #A crawler test
    
    #原始网页,scrap网页历史记录,最大数量
    crawl_queue=[seed_url]
    seen_queue=set(crawl_queue)
    count=0
    
    #循环内容
    
       
    while count<max_iteration:
        
        url=crawl_queue.pop()
        
        html=download(url)
        
        if html:
            link_list=get_links(html)
                
            for link in link_list:
                if link not in seen_queue:
                    crawl_queue.append(link)
                    seen_queue.add(link)
            
        count=count+1
            
        print("Counter %s" % count)
    
    '''for x in crawl_queue:
        print "http %s" % x'''
    
    
def get_links(html):
    
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
    
    
if __name__=="__main__":
    
    a=time.time()
    
    if os.path.isfile("eu4test.db"):
        os.remove("eu4test.db")
    
    link_crawler("http://www.eu4wiki.com/Europa_Universalis_4_Wiki",5)
    
    b=time.time()
    
    print "Runing %s seconds"% (b-a)





def test():
        if os.path.isfile("eu4test.db"):
        os.remove("eu4test.db")
    
    html=download("http://www.eu4wiki.com/Europa_Universalis_4_Wiki")

    bs4obj=bs4.BeautifulSoup(html)
    
    h2content=bs4obj.find_all("a",href=re.compile("^/"))
    
    b=1

    zyx=ZDownData("eu4test.db")
    
    zyx.create_table("Pages","Name","TEXT")
    zyx.add_column("Pages","HTML","TEXT")
    zyx.add_column("Pages","H1","TEXT")
    urlbase="http://www.eu4wiki.com"
    #zyx.create_table("Pages","Name")
    #zyx.add_column("Pages","HTML","TEXT")
    #zyx.insert("Pages","Name","HTML",1,2)

    for a in h2content:
        #print b, a["href"]
        if b<5:
            newlocation=urlparse.urljoin(urlbase,a["href"])
            html=download(newlocation)
            par=bs4.BeautifulSoup(html)
            h1=par.h1
            print h1.get_text()
            zyx.insert("Pages","Name","HTML",b+20,str(a["href"]))
            zyx.update("Pages","Name","H1",b+20,str(h1.get_text()))
            b=b+1
    
    dbtest=zyx.extract_by_data("Pages","*","Name","< 25.00")
    
  
    print dbtest
    
    zyx.cursor.close()
    
    zyx.db.commit()
    zyx.db.close()
    '''a.New("eu4.db","HTML","HM","TEXT")'''
    print "Done"
