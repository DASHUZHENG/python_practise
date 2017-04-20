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