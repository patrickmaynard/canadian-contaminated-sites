#!/usr/bin/env python



import sqlite3
import xml.etree.ElementTree as ET	
import time

def initTable(connection):
	#The initOrgsTable function takes in a connection to a database.
	#It then drops any existing "orgs" table, creates a new "orgs" table and commits all actions.
	#The function returns a cursor object. 
	print 'This is the stub for the initTable() function.'
	print 'Creating or wiping database table ... '
	cursor = connection.cursor()
	cursor.execute('DROP TABLE IF EXISTS cities')
	cursor.execute('''CREATE TABLE cities AS 
		       SELECT (Location_Municipality || ", " || Location_Province) AS Place, COUNT(*) AS TheCount FROM sites WHERE SiteStatus_Status_EN LIKE '%Active%' AND Classification_Code LIKE '1' GROUP BY Place ORDER BY TheCount DESC''')
	connection.commit()
	return(cursor)


def createConnection(mode):	
	#The createConnection function takes in a mode (should be either 'test' or 'live').
	#It then connects accordingly to either the 'fcsi-test.db' file or the 'fcsi-live.db' file.
	#The function returns a sqlite3 "connection" object.
	print 'This is the stub for the createConnection() function.'
	if mode == 'test':
		print 'Function has been called in test mode.'
		connection = sqlite3.connect('fcsi-test.db')
	else:
		print 'Function has been called in live mode.'
		connection = sqlite3.connect('fcsi-live.db')
	return(connection)



#mode = 'test'
mode = 'live'
connection = createConnection(mode)
cursor = initTable(connection)
#cursor = populateCities(connection)
