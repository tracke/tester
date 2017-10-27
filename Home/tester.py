#!/usr/bin/python
import datetime
import sys
import pymysql
import configparser


site=1
dbserver='AWS'

def db_connect(dbserver):
    username = 'admin'
    password = 'password'
    port = 3306
    db = 'ssproduct'
    hoststr='ssdbinstance.c5a2689qo1ly.ap-southeast-1.rds.amazonaws.com'
        
    try:
        conn=pymysql.connect(host=hoststr, port=port, user=username, passwd=password, db=db)                          
        if conn:  #connection established
            print  'connected to server host: ', dbserver
        return conn

    except:

        print ("Cannot get DB Server connection!")

        raise Exception("Cannot get db server connection!")
    
    return conn


if __name__ == "__main__":
    conn=db_connect(dbserver)
    parser=configparser.ConfigParser()
    parser.add_section('WO_data')
    if conn:
        dbcur = conn.cursor()
        sql="SELECT  Work_Order_Number, Part_Number, Work_Order_Qty,Firmware_File_Name FROM Work_Orders  WHERE  STATUS='OPEN'  AND site=%s"
        dbcur.execute(sql, site)
        openWorkOrders =  dbcur.fetchall()
        i=1
        for row in openWorkOrders:
            Work_Order_Number=row[0]
            Part_Number=row[1]
            Qty=row[2]
            FWARE=row[3]
            parser.set('WO_data','WO_Number',str(Work_Order_Number))
            parser.set('WO_data','Part_Number',str(Part_Number))
            parser.set('WO_data','Qty',str(Qty))
            parser.set('WO_data','Firmware_file',str(FWARE))
            opt='w'
            iniFileName=str(Work_Order_Number)+str(Part_Number)+".ini"
            with open(iniFileName,opt) as f:
                parser.write(f)
            print( i,") Open WO: ",Work_Order_Number, "for ",Qty," of ",Part_Number,"using",FWARE)
           # print " Part ", Mesh_Device_Root," - " , Mesh_Device_Description
            i+=1


    conn.close()
    print 'Connection to dbserver closed'    
                    
            


