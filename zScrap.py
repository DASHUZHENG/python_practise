import urllib2
import re
import bs4
import urlparse
import datetime
import time
import zDatabase

class zDownload:
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

def link_crawler(seed_url):
    crawl_queue=[seedurl]
    while crawl_queue:
        url=crawl_queue.pop()
        html=download(url)

def get_links(html):
    webpage_re=re.compile()
    pass

if __name__=="__main__":
    html=download("http://www.eu4wiki.com/Europa_Universalis_4_Wiki")

    bs4obj=bs4.BeautifulSoup(html)
    h2content=bs4obj.find_all("a",href=re.compile("^/"))

    b=1
    zyx=zDatabase.zDatabase()
    urlbase="http://www.eu4wiki.com"
    for a in h2content:
        #print b, a["href"]
        newlocation=urlparse.urljoin(urlbase,a["href"])
        html=download(newlocation)
        par=bs4.BeautifulSoup(html)
        h1=par.h1
        print b,h1.get_text()
        zyx.Create("eu4.db","name",)
        b=b+1

    '''a.New("eu4.db","HTML","HM","TEXT")'''
    print "Done"

