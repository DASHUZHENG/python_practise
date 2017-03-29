import urllib2
import re
import bs4

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
    html=download("http://www.pythonscraping.com/pages/warandpeace.html")

    bs4obj=bs4.BeautifulSoup(html)
    h2content=bs4obj.find_all("a")

    b=1
    for a in h2content:
        print b, a
        b=b+1
    print "Done"
