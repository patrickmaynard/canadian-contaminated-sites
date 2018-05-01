#!/usr/bin/env python

#The xml2sql library works when converting our very simple "ReportingOrganizations" tag to something sqlite can use. 
#It fails to parse the larger "sites" tag correction, so I'm going to try this using xml.etree.ElementTree
#At least for now, this will be a very minimal import, covering only the fields I need to answer my questions.

"""

ASSUMPTIONS:

- Our sqlite database already exists, having been created by the ___ script.
  ^This one is actually temporary.
- We have access to the xml module.

TODO LIST:

~ Write a basic importSites function, running some tests along the way.
	x Since the xml file is huge, create a test file that only contains a few dozen sites. 
	  The frequently repeated tests will run faster with this file, saving a ton of time during the initial, exploratory work.
	x Smoke test one (FAILED): Does it process the same number of sites that are shown on the public-facing online database? 
		No, but not through any failure of my logic. 
		TODO: I'll ask the Canadian federal folks about this later in my process, so I can clump a few relevant questions together.
	x Smoke test two (PASSED): Does the sqlite import bring in the requisite 46 sites from our test-subset.xml file? 
	x Before I get too far into this, I should look around for a simple way to calculate lat/lon distances using python/sqlite.
	  YES. It looks like the geopy library's vincenty() can easily figure out a sufficiently accurate distance between to lat/lon points. 
	x Build out a lat/lon import
	x Add a few more lines of logic to import site names, which are optional but usually present. 
	x Wrap any optional text imports in "try" blocks, allowing us to insert flag values for non-populated records.
	x Run a few more quick tests to make sure that the new logic works, allowing all lat/lon/country/name data to import into the database.
	x Add a SiteStatus importer to bring in required status information
	x Test that the SiteStatus importer is working correctly
	- Back up this file, since you're about to do a mini-refactor on a bunch of stuff.
	- Break out the creation of the sites database into its own function, making sure that the function gets called and works.
	- Move a lot of the current "attrib[blablabla]" references into a local object, as described in a TODO comment below.
	- Also move any independent variables into that object as needed.  
	- Smoke test three: Does this function import lat/lon/country/name correctly for our purposes? 
	- Now split off the genuine import from the test import -- maybe just by having our functions take in a "mode" flag indicating test/live import status.
	- Now build a function that imports the reporting organizations as well. 
	- Smoke test four: Does our test import of orgs to sqlite match or beat our earlier script's import?
	- Test five (first formal unit test): Does a hashed representation of the test "site" data match a stored value? (Consider using something like PyUnit for this)
	- Test six: Same as test five, but for "org" data
	- Write up a quick description for what this creation/import script does (creation/import of selected fields) and omits (any sort of analysis)
	- Edit these comments a bit so you don't look insanely disorganized
	- Now it's time for a design break. 
	  Now that I know more about what I can do, I should look at my original questions and plot out a bit more detail on a good design for answering them. 
	  I should also try to come up with a couple more questions for the Canadian folks to go along with my record-count disparity question. 
	  I should also make sure that I've documented the high-level design of the code somewhere.
	  (It is increasingly looking like this will be a repo for DB creation/import, a repo for analysis, and a repo for presentation)
 

"""

TIWIS - Time to back this stuff up a bit! 


import sqlite3
import xml.etree.ElementTree as ET	
import time

def importSites():
	print 'This is the stub for the importSites() function.'
	mode = 'test'
	if mode == 'test':
		print 'Function has been called in test mode.'
		print 'Creating or wiping "sites" table in test database  ... '
		conn = sqlite3.connect('fcsi-test.db')
	else:
		print 'Function has been called in live mode.'
		print 'Creating or wiping "sites" table in live database  ... '
		conn = sqlite3.connect('fcsi-live.db')
	c = conn.cursor()
	c.execute('DROP TABLE SITES')
	c.execute('''CREATE TABLE IF NOT EXISTS sites 
		       (FederalSiteIdentifier TEXT, ReportingOrganization TEXT, Created TEXT, LastModified TEXT, Location_Latitude TEXT, Location_Longitude TEXT, Location_Country_EN TEXT, Name_EN TEXT, SiteStatus_EN TEXT)''')
	c.execute('DELETE FROM sites')
	conn.commit()
	print 'Our database tables have now been created/wiped.'
	#^Trying a sleep to see whether our inserts (farther down) are hitting a race condition.
	# (Our table is blank when we try to look at it -- not sure why that is. No obvious errors occur.)	
	#tree = ET.parse('fcsi-rscf.xml')
	tree = ET.parse('test-subset.xml')
	#^The test-subset document contains roughly 10,000 of the data from the actual doc.
	# I have pared it down for faster test runs when possible. 
	root = tree.getroot()
	print root.tag	
	siteCounter = 1	
	identifiers = {}
	for site in root[1]:
		latitude = ''
		longitude = ''
		country_en = ''
		name_en = ''
		#print site.tag, site.attrib
		identifier = site.attrib['FederalSiteIdentifier']
		identifiers[identifier] = 1
		#print "sitecounter: ", siteCounter
		#print "identifiers length: ", len(identifiers)
		for name in site.iter('Name'):
			english = ''
			for english in name.iter('EN'):
				try:
					name_en = english.text.strip()
        			except AttributeError, e:
					name_en	= '000 - not present in XML'
		for sitestatus in site.iter('SiteStatus'):
			english = ''
			for english in sitestatus.iter('EN'):
				try:
					sitestatus_en = english.text.strip()
        			except AttributeError, e:
					sitestatus_en	= '000 - not present in XML'
		for location in site.iter('Location'):
			for subloc in location.iter():
				print subloc.tag, subloc.attrib, subloc.text.strip()
				if subloc.tag == 'Latitude':
					latitude = subloc.text.strip()
				if subloc.tag == 'Longitude':
					longitude = subloc.text.strip()
				if subloc.tag == 'Country':
					english = ''
					for english in subloc.iter('EN'):
						country_en = english.text.strip()
		sql =  'INSERT INTO sites (FederalSiteIdentifier, ReportingOrganization, Created, LastModified, Location_Latitude, Location_Longitude, Location_Country_EN, Name_EN, SiteStatus_EN) '
		sql += ' VALUES("'+site.attrib['FederalSiteIdentifier']+'","'+site.attrib['ReportingOrganization']+'","'+site.attrib['Created']+'","'+site.attrib['LastModified']+'","'+latitude+'","'+longitude+'","'+country_en+'","'+name_en+'","'+sitestatus_en+'");'
		#TODO: ^Clean up the assignment of temporary values so that they all follow the same format. 
		#	(Right now, there's a mix of local variables and site attributes. 
		#	I should ideally move all of these values to a temporary local object ahead of time.
		#	I should also label what I'm doing during that process. 
		print site.attrib['FederalSiteIdentifier']	
		print sql;
		c.execute(sql)
		conn.commit()
		#^We trust the data from the Canadian federal folks, so I'm ok with a direct insert here.
		# (If I didn't, I wouldn't be using their database at all.)
		siteCounter += 1
		#^In our test-subset file, this should be a count of 46. 
		# In our real file, the count is 26,723.
		# This is a bit higher than the 22,799 described at http://www.tbs-sct.gc.ca/fcsi-rscf/classification-eng.aspx
		# Each FederalSiteIdentifier number is unique, so eliminating redundancies does nothing. 
		# TODO: I'll need to ask about why this number differs so significantly from the official number.
		#       (One very distinct possiblity is that the tally is simply an out-of-date manual tabulation someone compiled.
		#        The data dictionary appears to unintentionallly hint at this possibily with some out-of-date field names.
		#        Anyway, I should eventually ask about this, once I have a few questions to lump together.)

importSites()
