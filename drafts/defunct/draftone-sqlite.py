#!/usr/bin/env python

import urllib
import zipfile 
from xmlutils.xml2sql import xml2sql
import sqlite3

#Dieses Zweige ist nicht so tot, wie ich gedacht hatte. 

"""

#All of this stuff works.
#The sextuple-quote commenting is just to avoid re-downloading the fcsi stuff every time I test other logic.

#Download the FCSI data extract in ZIP form and save it as extract.zip
#(Data is described at http://www.tbs-sct.gc.ca/fcsi-rscf/opendata-eng.aspx)
urllib.urlretrieve('http://www.tbs-sct.gc.ca/fcsi-rscf/oddo/fcsi-rscf.zip','extract.zip')

#Unzip the file to reveal its contents.
#(This should create a lone file: fcsi-rscf.xml)
compressed = zipfile.ZipFile('extract.zip')
compressed.extractall()

"""

#We want sites that are simultaneously marked with status of *active* and classification of *high priority for action*.
#As of December 2015, that group comprises 730 sites.
#So sez http://www.tbs-sct.gc.ca/fcsi-rscf/numbers-numeros-eng.aspx?qid=422012

#It appears that our downloaded XML essentially describes two tables.
#ReportingOrganizations is what it sounds like and is very small.
#Sites is much larger, taking up the vast majority of the 6MB+ file space.

#First, we import the organizations. This is a small table, so that's relatively simple.
#TODO: Add logic that uses something like sed to fix the utf-16 declaration. (The xml doc is actually utf-8.)
#orgconverter = xml2sql("fcsi-rscf.xml", "organizations.sql")
#orgconverter.convert(table="organizations",tag="ReportingOrganization")

#Now we want to import our "Site" tags. 
#These have a ton of nested subtags, many of which have redundant names.
#To avoid hair-tearing, I'm starting simple by omitting most subtags, then adding complexity. 
sitetags = open('sitetags.txt','r').read(100000) 
fulltaglist = sitetags.split(',')
tagstokeep = ['PropertyNumber']
#^So far, it looks like our conversion library is only able to handle Location_Latitude and Location_Longitude reliably.
#PopulationCounts_KM10 and Classification_Code appear to yield results on at least most of the rows, though some are missing these fields. 
#A previous test confirmed that I can leave parent tags like FederalContaminatedSitesInventory and Sites out of the tagstokeep list and still get child elements.
#  This helps keep our list of tags to keep reasonably short.)
#A previous test confirmed that point "67.828889", "-115.006389" has 29 rows associated when only lat/lon are imported. 
#  This means that there is probably NOT some sort of cartesian-product problem at play -- a huge relief.)
#A previous test was to see whether adding the Classification_Code tag takes our row count beyond 25,944 -- our previous count with lat/lon alone.
#  Result: It does. Count goes up to 26143. This is problematic.)
#A previous test was to see whether the PropertyNumber tag alone gives us more than 26,143 properties. (Our goal is to find a true UID.)
#  Result: We get 16446 rows, including some duplicates.
TIWIS: Per line below, I am doing new tests in draftone-altxml.py to see if I can just make a nice manual importer of some sort. 
#NEXT TEST is to see whether the FederalSiteIdentifier ATTRIBUTE is a true "site" uid. This will require a different XML module.
#  Result: _______ 
#Next test is to keep cycling in fields to see whether solely non-numeric fields are ignored. 
#(I have tried fields up through and including Classification_Name so far. 
#(If we can even get a basic numeric site identifier field, we may be able to scrape other data manually from the XML using other libraries.)
ignorestring = "ReportingOrganization PlannedCompletionDateStep7 PlannedCompletionDateStep8 PlannedCompletionDateStep9 "
for tag in fulltaglist:
	try:
		index = tagstokeep.index(tag)
		print "using "+tag
	except ValueError, e:
		print "discarding "+tag
		ignorestring += tag+" "
ignorestring = ignorestring.strip()
siteconverter = xml2sql("fcsi-rscf.xml", "sites.sql")
siteconverter.convert(table="sites",tag="Site",ignore=ignorestring)
#In converting sites to a .sql dump, we'll want to ignore most tags, since they create all sorts of probles. 
#I'll then need to break up that dump into individual transactions.
#(30,000+ inserts in a single transaction is a bad idea in SQLite. The "lite" is there for a reason. 



#Now let's create a very crude sqlite database (mainly using TEXT types for now) and import the smaller table. 
#conn = sqlite3.connect('crude.db')
#c = conn.cursor()
#c.execute('''CREATE TABLE IF NOT EXISTS organizations 
#		(Code TEXT, EN TEXT, FR TEXT)''')
#c.execute('DELETE FROM organizations')
