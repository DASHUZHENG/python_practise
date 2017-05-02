# -*- coding: utf-8 -*-
import urllib2
import re
import bs4
import urlparse
import datetime
import time
import os
import logging
import pickle
import random

from zdatabase import ZDownData

logging.basicConfig(level="INFO")

class ZCache():
    
    def __init__(self,category=1,cache_dir="",cache_db=None):
        
        logging.debug("Zcache Started")
        
        self.category=category
        
        self.cache_dir=cache_dir
        
        self.db=cache_db
        
        self._methodset()
        
        
    
    def __getitem__(self,url):
        
        if self.category==1:
            
            try:
                result=self.library[url]

            except Exception,error:
                
                logging.info("Cache Get Cat%s Mistake: %s" % (self.category,error))
                result=None
                
        elif self.category==2:
            
            path=self.url_to_path(url)
            
            #logging.debug("Get Item %s" % path)
            
            if os.path.exists(path):
                
                try:
                    with open(path) as fp:
                        
                        result=pickle.load(fp)
                
                except Exception,error:
                    
                    logging.info("Cache Get Cat%s Mistake: %s" % (self.category,error))
                    result=None
            
            else:
                
                result=None
        
        elif self.category==3:
            
            try:
                da_data=self.db.extract_by_text(table=self.db_setting["table"],\
                att=self.db_setting["att"],key=self.db_setting["key"],value=url)
                
                result=da_data[0]
                
                logging.debug("Result Retrieved %s %s" % (url,result))
                
                
            except Exception,error:
                
                logging.info("Cache Get Cat%s Mistake: %s" % (self.category,error))
                result=None
        
        elif self.category==4:
            
            
            
            try:
                da_data=self.db.extract_by_text(table=self.db_setting["table"],\
                att=self.db_setting["att"],key=self.db_setting["key"],value=url)
            
               
                
                if len(da_data)!=0:
                    
                    doc_name=da_data[0][0]
                    
                    print "Doc Name",doc_name
                    
                    path=self.cache_dir+"/"+str(int(doc_name))
                    
                    
                    with open(path) as fp:
                            
                        result=pickle.load(fp)
                
                else:
                    
                    result=None
            
            except Exception,error:
                    
                logging.info("Cache Get Cat%s Mistake: %s" % (self.category,error))
                result=None     
               
                

        
        else:
            
            logging.info("No Cache Get Method Set %s" % self.category)
            
            result=None
        
        return result

    
    def __setitem__(self,url,html):
        
        if self.category==1:
            
            self.library[url]=html
        
        elif self.category==2:
            path=self.url_to_path(url)
            
            folder=os.path.dirname(path)
            
            logging.debug(folder)
            
            if not os.path.exists(folder):
                
                os.makedirs(folder)
            
            with open(path,"wb") as fp:
                
                fp.write(pickle.dumps(html))
            
        elif self.category==3:
            
            logging.debug("Cat 3 Setting Start")
            self.db.insert_not_exist(table=self.db_setting["table"],\
                primekey=self.db_setting["key"],subkey=self.db_setting["att"],\
                primecontent=url,subcontent=1)
        
            #!Subcontent内容非HTML,为Debug态
        
        elif self.category==4:
            
            self.db.insert_not_exist(table=self.db_setting["table"],\
                primekey=self.db_setting["key"],subkey=self.db_setting["att"],\
                primecontent=url,subcontent=str(int(self.counter)))   
                
            
            
            doc_name=str(self.counter)
            
            path=self.cache_dir+"/"+doc_name
            
            with open(path,"wb") as fp:
                
                fp.write(pickle.dumps(html))
            
            self.counter=self.counter+1
            
            print "4 SET", self.counter
            
            #!并不必要not exist 方法
            
    def url_to_path(self,url):
        
        url_analysis=urlparse.urlsplit(url)
        
        path=url_analysis.path
        
        if not path:
            
            path="index.html"
        
        elif path[-1]==("/"):
            
            path=path + "index.html"
            
        filename=url_analysis.netloc+path+url_analysis.query
        
        logging.debug(filename)
        
        filename=re.sub('[^/0-9a-zA-Z\-.,;_]','_',filename)
        
        filename="/".join(segment[:255] for segment in filename.split("/"))
        
        logging.debug(filename)
        
        result=self.cache_dir+"/"+filename
        
        return result
    
    
    def refresh(self):
        
        if self.category==1:
            pass
        
        elif self.category==2:
            pass
        
        elif self.category==3:
            pass
        
        elif self.category==4:
            
            try :
                self.db.insert_not_exist(table=self.db_log["table"],\
                primekey=self.db_log["key"],subkey=self.db_log["att"],\
                primecontent=self.cache_dir,subcontent=str(int(self.counter)))  
                
                print "CAT 4 Cache Refreshed",self.counter
                
            except Exception,error:
                
                logging.info("CAT 4 Cache Not Refreshed: %s" % error)
                
        else:
            pass
        
        
    def _methodset(self):
        #根据self.category 选择确定缓存方法
        
        if self.category==1:
            
            self.library={}
        
        elif self.category==2:
            
            pass
        
        elif self.category==3:
            
            
            #zdatabase,sqlite3
            self.db_setting={"table":"HTML","att":"HTML","key":"URL"}
            
            try:
                self.db.create_table(self.db_setting["table"],\
                self.db_setting["key"],"TEXT")
                
                
                self.db.add_column_not_exist(self.db_setting["table"],\
                self.db_setting["att"],"TEXT")
                
            except Exception, error:
                
                logging.info("Database initilization failed: %s" % error)
                
                default_name=".db"
                db_num=random.randint(1,100)
                db_name="3"+str(db_num)+default_name
                self.db=ZDownData(db_name)
                
                self.db.create_table(self.db_setting["table"],\
                self.db_setting["key"],"TEXT")
                
                self.db.add_column(self.db_setting["table"],\
                self.db_setting["att"],"TEXT")
        
        elif self.category==4:  
            
            
            #zdatabase,sqlite3
            self.db_setting={"table":"HTML","att":"TAG","key":"URL"}
            
            self.db_log={"table":"DB","att":"COUNTER","key":"DB"}
            
            
            try:
                self.db.create_table(self.db_setting["table"],\
                self.db_setting["key"],"TEXT")
                #创建网页数据库
                
                self.db.add_column_not_exist(self.db_setting["table"],\
                self.db_setting["att"],"TEXT")
                
                self.db.create_table(self.db_log["table"],\
                self.db_log["key"],"TEXT")
                #创建目录信息
                
                self.db.add_column_not_exist(self.db_log["table"],\
                self.db_log["att"],"TEXT")
                
                
                
            
            except Exception, error:
                
                logging.info("Database initilization failed: %s" % error)
                
                default_name=".db"
                db_num=random.randint(1,100)
                db_name="4"+str(db_num)+default_name
                self.db=ZDownData(db_name)
                
                self.db.create_table(self.db_setting["table"],\
                self.db_setting["key"],"TEXT")
                
                self.db.add_column(self.db_setting["table"],\
                self.db_setting["att"],"TEXT")
            
            
                self.db.create_table(self.db_log["table"],\
                self.db_log["key"],"TEXT")
                #创建目录信息
                
                self.db.add_column_not_exist(self.db_log["table"],\
                self.db_log["att"],"TEXT")
            
            try:
                
                self.counter=0
                
                counter_seed=self.db.extract_by_text(self.db_log["table"],\
                self.db_log["att"],self.db_log["key"],value=self.cache_dir)
                
                print "Counter_Seed",counter_seed
                
                if counter_seed[0]!=None:
                    
                    self.counter=int(counter_seed[0][0])
                    
                    print "Counter_Seed",self.counter
            
            except Exception,error:
                
                logging.info("Database Counter failed: %s" % error)
                
                self.counter=0
                
                
            print "4 Initial",self.counter
            
        #cat=1,lib;cat=2,doc;cat=3,database;cat=4,doc&database
    
if __name__=="__main__":
    
    
    url="http://www.eu4wiki.com/Europa_Universalis_4_Wiki"
    
    db=ZDownData("test.db")
    
    Z=ZCache(category=3,cache_dir="cache",cache_db=db)
    
    q=Z.__setitem__(url,2)
    
    w=Z[url]
    
    t=Z.url_to_path(url)
    
    logging.info(w)
    logging.info(t)
    
    
   