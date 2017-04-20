# -*- coding: utf-8 -*-
try:
    import xlrd
except Exception,error:
    print("No,xlrd")

import sqlite3


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
        self.cursor.execute('create table %s (%s %s primary key)' % (table,primekey,cat))

    def add_column(self,table,newkey,cat):
        self.cursor.execute('alter table %s add column %s %s ' % (table,newkey,cat))

    def insert(self,table,primekey,subkey,primecontent,subcontent):
        self.cursor.execute("insert into %s (%s,%s) values (\'%s\',\'%s\')" % (table,primekey,subkey,primecontent,subcontent))
    
    def update(self,table,primekey,subkey,primecontent,subcontent):
        #UPDATE 表名称 SET 列名称 = 新值 WHERE 列名称 = 某值
        self.cursor.execute('''update %s set %s = "%s" where %s = "%s"''' % (table,subkey,subcontent,primekey,primecontent))
    
    def extract_by_text(self,table="Default",att="*",key="Field1",value="Default"):
        #(self,table,att,key,keyvalue):
        self.cursor.execute('SELECT %s from %s where %s=\'%s\'' % (att,table,key,value))
        result=self.cursor.fetchall()
        
        return result
        
    def extract_by_data(self,table="Default",att="*",key="Field1",relation="= 0",advance=None):
        #(self,table,att,key,keyvalue):
        self.cursor.execute('SELECT %s from %s where %s %s' % (att,table,key,relation))
        result=self.cursor.fetchall()
        
        return result

if __name__=="__main__":
    
    excel=xlrd.open_workbook("Test.xlsm")

    table=excel.sheets()[0]
    rcol=table.ncols
    rown=table.nrows
    a=zDatabase()
    
    for table in excel.sheets():
        print table.name
        a.Create("zPro.db",table)



    
    
    
    
    
    
    
    
