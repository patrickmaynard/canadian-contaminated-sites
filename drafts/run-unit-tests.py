#!/usr/bin/env python

import unittest
from xml.etree import ElementTree as ET
import sqlite3
import geojson

class TestMethods(unittest.TestCase):

	#Test the basics of etree handling
	def test_etree(self):
		document = ET.Element('root')
		et = ET.ElementTree(document)			

	#TODO:Test the basics of database connection
	def test_connection(self):
		connection = sqlite3.connect('fcsi-test.db')

	#TODO: Test a basic geojson method or two
	def test_geojson(self):
		my_location = geojson.Point((49.35,18))		

if __name__ == '__main__':
    unittest.main()
