# -*- coding: utf-8 -*-

import os
import sqlite3
import logging

logging.basicConfig(level="INFO")


class ZDownData():
    
    def __init__(self,database):
        self.name=database
        self.db=sqlite3.connect(database)
        self.cursor=self.db.cursor()
    
    def execute(self,sentence):
        
        self.cursor.execute(sentence)
        
        result=self.cursor.fetchall()
        
        return result
        
    def create_table(self,table="Default",primekey="Field1",cat="TEXT"):
        self.cursor.execute('''create table if not exists %s (%s %s primary key)''' % (table,primekey,cat))
    
    def table_info(self,table="Default"):
        
        self.cursor.execute('''PRAGMA table_info(%s)''' % table)
        result=self.cursor.fetchall()
        
        return result
    
    def add_column(self,table,newkey,cat):
        self.cursor.execute('''alter table %s add column %s %s ''' % (table,newkey,cat))
        
    def add_column_not_exist(self,table,newkey,cat):
        
        exist_name=None
        
        for content in self.table_info(table):
            
            
            if content[1]==newkey:
                
                exist_name=content[0]
                
                break
        
        if exist_name==None:
            
            self.cursor.execute('''alter table %s add column %s %s ''' % (table,newkey,cat))
                
        else:
            
            logging.info("Column Name Existed in Column %s!" % exist_name)
            
            
            
    def insert(self,table,primekey,subkey,primecontent,subcontent):
        #!Does it need a commit?
        #logging.debug('''insert into %s (%s,%s) values ("%s","%s")''' % (table,primekey,subkey,primecontent,subcontent))
        
        self.cursor.execute('''insert into %s (%s,%s) values ("%s","%s")''' % (table,primekey,subkey,primecontent,subcontent))
        self.db.commit()
    
    def insert_not_exist(self,table,primekey,subkey,primecontent,subcontent):   
        
        exist_name=None
        
        for content in self.extract_all(table,primekey):
            
            if primecontent==content[0]:
                
                self.update(table,primekey,subkey,primecontent,subcontent)
                
                exist_name=1
                
                logging.debug("%s already exists" % primecontent)
                
                break
        
        if exist_name==None:
            
            self.insert(table,primekey,subkey,primecontent,subcontent)
            
            
        
    def update(self,table,primekey,subkey,primecontent,subcontent):
        #UPDATE 表名称 SET 列名称 = 新值 WHERE 列名称 = 某值
        self.cursor.execute('''update %s set %s = "%s" where %s = "%s"''' % (table,subkey,subcontent,primekey,primecontent))
        self.db.commit()
    
    def extract_all(self,table="Default",att="*"):
        #(self,table,att,key,keyvalue):
        self.cursor.execute("SELECT %s from %s" % (att,table))
        result=self.cursor.fetchall()
        
        return result
    
    def extract_by_text(self,table="Default",att="*",key="Field1",value="Default"):
        #(self,table,att,key,keyvalue):
        self.cursor.execute("SELECT %s from %s where %s=\'%s\'" % (att,table,key,value))
        result=self.cursor.fetchall()
        
        return result
        
    def extract_by_data(self,table="Default",att="*",key="Field1",relation="= 0",advance=None):
        #(self,table,att,key,keyvalue):
        self.cursor.execute('SELECT %s from %s where %s %s' % (att,table,key,relation))
        result=self.cursor.fetchall()
        
        return result

if __name__=="__main__":
    
    if os.path.isfile("test.db"):
        
        os.remove("test.db")
    
    zyx=ZDownData("test.db")
    
    zyx.create_table("Pages","URL","TEXT")
    zyx.add_column("Pages","HTML","TEXT")
    zyx.add_column("Pages","H1","TEXT")
    zyx.add_column_not_exist("Pages","H1","TEXT")
    
    t=zyx.table_info("Pages")
    
    for con in t :
        
        print con[1]
    
    print t


    
    
    
    
    
    
    
    
