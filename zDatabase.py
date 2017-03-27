import xlrd
import sqlite3

class zDatabase:

    def Create(self,database,table):
        rcol=table.ncols
        rown=table.nrows
        conn=sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute('create table %s (%s %s primary key)' % (table.name,table.row_values(0)[0],table.row_values(1)[0]))

        for key in range(1,rcol):
            print table.row_values(0)[key]
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
       
