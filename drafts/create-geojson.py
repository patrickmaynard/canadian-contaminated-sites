#!/usr/bin/env python


import geojson
import sqlite3
import xml.etree.ElementTree as ET	
import time

def writeJSON(connection):
	#What's all this, then?
	#Creating some geojson goodness ...
	cursor = connection.cursor()
	#We want the half-dozen high-priority sites with the most people within a 5km radius. Those sites are (as of 2016) all in Montreal.
	result = cursor.execute('''SELECT FederalSiteIdentifier, PopulationCount_KM5, Name_EN, Location_Municipality, Location_Latitude, Location_Longitude FROM sites WHERE SiteStatus_Status_EN LIKE 'Active' AND Classification_Code LIKE '1' ORDER BY CAST(PopulationCount_KM5 AS integer) DESC LIMIT 0,6; ''')
	rows = result.fetchall()
	features = []
	for row in rows:
		site = {}
		site['Location_Latitude'] = float(row[4].strip())
		site['Location_Longitude'] = float(row[5].strip())
		my_point = geojson.Point((site['Location_Latitude'],site['Location_Longitude']))
		my_feature = geojson.Feature(geometry=my_point, properties={"FederalSiteIdentifier":row[0],"PopulationCount_KM5":row[1],"Name_EN":row[2],"Location_Municipality":row[3]});
		features.append(my_feature)
	my_feature_collection = geojson.FeatureCollection(features)
	with open('data.json', 'w') as f:
		print geojson.dump(my_feature_collection,f)	
	connection.commit()
	print "geojson has been successfully dumped into data.json."
	return(cursor)


def createConnection(mode):	
	#The createConnection function takes in a mode (should be either 'test' or 'live').
	#It then connects accordingly to either the 'fcsi-test.db' file or the 'fcsi-live.db' file.
	#The function returns a sqlite3 "connection" object.
	if mode == 'test':
		connection = sqlite3.connect('fcsi-test.db')
	else:
		connection = sqlite3.connect('fcsi-live.db')
	return(connection)



#mode = 'test'
mode = 'live'
connection = createConnection(mode)
cursor = writeJSON(connection)
#cursor = populateCities(connection)
