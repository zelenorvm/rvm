
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import string
import MySQLdb
import json
import time
import mysql.connector as mariadb

encoding = "utf-8" 
on_error = "replace"

DATABASE="zelenoDb"
HOST="localhost"
USERNAME="Administrator"
PASSWORD="admin123"

def execQuery(Query,fetch=None):
	tempSts = []
        db=None
	try:
            db = mariadb.connect(user=USERNAME,password=PASSWORD, database=DATABASE)
            cursor = db.cursor()
	    print '\n Connected to Database Successfully. Connector Id:', cursor 
	    if "Insert" in Query or "Update" in Query or "Delete" in Query:
	        try:
		    cursor.execute(Query)
		    db.commit()
		    tempSts = "0"
	        except mariadb.Error as err:
		    tempSts = "1"
		    print(err)
	    elif "Select" in Query:
	        try:
		    cursor.execute(Query)
		    if fetch is None:
	    	        value = cursor.fetchone()
			if value is not None:	
			    temp = 0
			    while temp != len(value):
			        tempSts.append(str(value[temp]))
				temp = temp + 1
			elif "multiple" in fetch:
			    for data in cursor.fetchall():
				if data is not None:
				    tempSts.append(str(data))
			else:
			    for data in cursor.fetchall():
			        tempSts.append(str(data[0]))
		except mariadb.Error as err:
			tempSts = "1"
			print(err)
	except mariadb.Error as err:
		tempSts = "2"
		print(err)
        if db is not None:
	    db.close()
	print '\n tempSts is :', tempSts
        return tempSts

#execQuery("Insert into Transaction(mobileNum,bottleCount,selCoupon) VALUES ('7042454318',2,'PayTm')")

