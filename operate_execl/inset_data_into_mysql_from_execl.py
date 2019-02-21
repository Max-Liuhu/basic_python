#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/1/23 19:00
# @Author  : liuhu
# @File    : inset_data_into_mysql_from_execl.py
# @Software: PyCharm
# @github  :https://github.com/Max-Liuhu
import xlrd
import mysql.connector

# 连接数据库
try:
    conn = mysql.connector.connect(host='192.168.6.96', port='3306', user='root', password='123123', database='desktop')
except:
    print "could not connect to mysql server"



# 打开Excel
execl_file_path = r'./liuhu.xlsx'
def open_excel():
    try:
        book = xlrd.open_workbook(execl_file_path)
    except:
        print("open excel file failed!")
    try:
        sheet = book.sheet_by_name("Sheet1")
        return sheet
    except BaseException:
        print("locate worksheet in excel failed!")

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False


import math
from decimal import Decimal
def insert_deta():
    sheet = open_excel()
    cursor = conn.cursor(buffered=True)
    row_num = sheet.nrows
    for i in range(1, row_num):
        print(i)
        row_data = sheet.row_values(i)
        # print type(row_data)
        # print '用户名'.decode('utf-8')
        # print row_data.index('用户名'.decode('gbk'))
        print type(row_data[2])
        # if '\\' in str(row_data[2]):
        #     print '中文'
        print len(row_data[2] if not isinstance(row_data[2],float) else str(row_data[2]))
        # print type(int(row_data[1]))
        # print  Decimal(row_data[1]).quantize(Decimal('0'))
        value = (row_data[0],row_data[1] ,row_data[2],row_data[3])
        print value
        if isinstance(row_data[2],unicode):
            print is_chinese(row_data[2])
        # sql = "INSERT INTO user(name,password,group_id,policy_id)VALUES(%s,%s,%s,%s)"
        # cursor.execute(sql, value)
        # conn.commit()
        print '-----------======------------'
        # if i ==1:
        #     break
    # cursor.close()





open_excel()
insert_deta()
# print (type(6.0))