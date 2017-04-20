# -*- coding: utf-8 -*-

try:
    import xlrd
except Exception,error:
    print("No,xlrd")

import sqlite3

class zDatabase:

    def Create(self,database,table):
        rcol=table.ncols
        rown=table.nrows
        conn=sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute('create table %s (%s %s primary key)' % (table.name,table.row_values(0)[0],table.row_values(1)[0]))

        for key in range(1,rcol):
            #print table.row_values(0)[key]
            cursor.execute('alter table %s add column %s %s ' % (table.name,table.row_values(0)[key],table.row_values(1)[key]))

        #cursor.execute('insert into %s (%s, %s) values (1, \'%s\')' % (table.name,table.row_values(0)[0],table.row_values(0)[1],"haha"))
        #historical test

        description='insert into %s (' % (table.name)
        for key1 in range(0,(rcol-1)):
            description=description+table.row_values(0)[key1]+','
        description=description+table.row_values(0)[-1]  +')'  


        for key1 in range(2,(rown)):
            content=' values (\'' 
            for key2 in range(0,(rcol-1)):
                strnum=str(table.row_values(key1)[key2])
                content=content+strnum+'\',\''
            content=content+str(table.row_values(2)[-1])+'\')' 
            datades=description+content
            #print datades
            cursor.execute(datades)
        cursor.close()
        conn.commit()
        conn.close()

    def Locate(self,database,table,key,attribute,tag="Field1"):

        conn=sqlite3.connect(database)
        cursor = conn.cursor()
        #print('SELECT %s from %s where COMPONENT=\'%s\'' % (attribute,table,key))
        #historical test
        cursor.execute('SELECT %s from %s where %s=\'%s\'' % (attribute,table,tag,key))
        result=cursor.fetchone()

        cursor.close()
        conn.commit()
        conn.close()

        return result

     #创建数据表
        #cur.execute("create table student(id int ,name varchar(20),class varchar(30),age varchar(10))")
        #插入一条数据
        #cur.execute("insert into student values('2','Tom','3 year 2 class','9')")
        #修改查询条件的数据
        #cur.execute("update student set class='3 year 1 class' where name = 'Tom'")
        #删除查询条件的数据
        #cur.execute("delete from student where age='9'")

class ZDownData():
    def __init__(self,database):
        self.name=database
        self.db=sqlite3.connect(database)
        self.cursor=self.db.cursor()

    def create_table(self,table="Default",primekey="Field1",cat="TEXT"):
        self.cursor.execute('create table %s (%s %s primary key)' % (table,primekey,cat))

    def add_column(self,table,newkey,cat):
        self.cursor.execute('alter table %s add column %s %s ' % (table,newkey,cat))

    def insert(self,table,primekey,subkey,primecontent,subcontent):
        self.cursor.execute("insert into %s (%s,%s) values (\'%s\',\'%s\')" % (table,primekey,subkey,primecontent,subcontent))
        pass

    def extraction(self,table="Default",primekey="Field1",cat="TEXT"):
        #(self,table,att,key,keyvalue):
        pass
        #self.cursor.execute('SELECT %s from %s where %s=\'%s\'' % (att,table,key,keyvalue))

        #result=self.cursor.fetchall()

        #return result


if __name__=="__main__":
    
    excel=xlrd.open_workbook("Test.xlsm")

    table=excel.sheets()[0]
    rcol=table.ncols
    rown=table.nrows
    a=zDatabase()
    
    for table in excel.sheets():
        print table.name
        a.Create("zPro.db",table)



    
    
    
    
    
    
