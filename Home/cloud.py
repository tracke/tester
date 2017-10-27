#!/usr/bin/python
import datetime
import sys, os
import pymysql
import configparser
import boto3
import botocore

#from __future__ import print_function

region = 'ap-southeast-1'
aws_access_key_id = 'AKIAIFGBDJXSDCE2ZMBQ'
aws_secret_access_key = '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'


site=1
dbserver='AWS'
global WorkOrder

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



def dumpclean(obj):
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print k
                dumpclean(v)
            else:
                print '%s : %s' % (k, v)
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print v
    else:
        print obj


def get_S3_File(obj):
    BUCKET_NAME = 'ssfirmware'
    KEY = obj
    s3 = boto3.resource('s3',region,None,True,None,None,aws_access_key_id, aws_secret_access_key)
    try:
        s3.Bucket(BUCKET_NAME).download_file(KEY,obj)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
        return(e)         
    pass


def put_S3_File(bucket,obj): 
    s3 = boto3.client('s3')
    with open('filename', 'rb') as data:
        s3.upload_fileobj(data, 'mybucket', 'mykey')



def selectWorkOrder(openWorkOrders):
    WorkOrderList={}
    choice=0
    i=0
    print "Open Work Orders"
    for row in openWorkOrders:
        i+=1
        print 'Work Order ',row[0],': P/N ',row[1],' Qty:',row[2],' Firmware_File_Name:',row[3] 
        WorkOrderList[row[0]]=row    
    while choice not in WorkOrderList:
        print "Select 3 digit Work Order"
        choice =int(raw_input('Enter Work Order - '))                    
    return WorkOrderList[choice] 




def pull_order_data(conn):
    parser=configparser.ConfigParser()
    parser.add_section('WO_data')
    dbcur = conn.cursor()
    sql="SELECT  Work_Order_Number, Part_Number, Work_Order_Qty,Firmware_File_Name FROM Work_Orders  WHERE  STATUS='OPEN'  AND site=%s"
    dbcur.execute(sql, site)
    openWorkOrders =  dbcur.fetchall()
    # put in check for no records found
   
    work_order = selectWorkOrder(openWorkOrders)   


    return work_order   
    pass    


if __name__ == "__main__":
    print("Production Tester Cloud Services")
    print("1) db connection; user/password")
    conn=db_connect(dbserver)
        
    
    if conn:
        WorkOrder = pull_order_data(conn)
        Work_Order, Part_Number, QTY, FWARE = WorkOrder
        print "Using WO #",Work_Order, "for ", QTY,"units of part ",Part_Number
        print "looking for firmware file",FWARE
        fware_path = "/FWARE/"+ FWARE
        if not os.path.isfile(fware_path):
            print "local copy not found, checking cloud"
            if not get_S3_File(FWARE):
                print FWARE,"in local store"
            else:
                print FWARE,"File not found"       



    conn.close()
    print 'Connection to dbserver closed'    
                    
            


