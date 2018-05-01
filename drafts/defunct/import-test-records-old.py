#!/usr/bin/env python

#The xml2sql library works when converting our very simple "ReportingOrganizations" tag to something sqlite can use. 
#It fails to parse the larger "sites" tag correction, so I'm going to try this using xml.etree.ElementTree
#At least for now, this will be a very minimal import, covering only the fields I need to answer my questions.

"""

ASSUMPTIONS:

- We have access to the xml files fcsi-rscf.xml and test-subset.xml
- The file test-db-dump-for-compare-output.txt is an empty, writeable file that was just created with the "touch" command.
- We have access to all necessary modules thanks to virtualenvwrapper and pip


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
	x Wrap any optional text imports in "try" blocks, allowing the script to insert flag values for non-populated records.
	x Run a few more quick tests to make sure that the new logic works, allowing all lat/lon/country/name data to import into the database.
	x Add a SiteStatus importer to bring in required status information
	x Test that the SiteStatus importer is working correctly
	x Back up this file to the "snapshots" dir, since you're about to do a mini-refactor on a bunch of stuff.
	x Break out the creation of the connection and sites database into their own functions, making sure that the function gets called and works.
	x Move a lot of the current "attrib[blablabla]" references into a local object, as described in a TODO comment below.
	x Also move any independent variables into that object as needed.  
	x Have the importSites() function take in a mode as well, allowing it to choose between XML files.
	x Smoke test set three: Does this script now import lat/lon/country/name correctly for our purposes? 
	x What about the other tags?  
	x Assuming the smoke test above worked, find a way to programmaticaly export the sqlite database into a file against which we can run diffs.
	x Break out each tag retrieval into a function that takes in the "site" tag and returns the value.
	x Now build a function that imports the reporting organizations as well. 
	x Smoke test four: Does our test import of orgs to sqlite match or beat our earlier script's import? Yes. Yes, it does. Moving non-relevant script to "defunct" folder.
	- Do the remaining import-related items from the main TODOs file.
	-------------------------------------------------------------------
	- Test five (first formal unit test): Does a hashed representation of the test "site" data match a stored value? (Consider using something like PyUnit for this)
	- Test six: Same as test five, but for "org" data
	- Write up a quick description for what this creation/import script does (creation/import of selected fields) and omits (any sort of analysis)
	- Edit these comments a bit so you don't look insanely disorganized
	- Now build and run a unit test to make sure that all XML elements we loop through without protection are present ONLY at the intended level.
	  In other words, this should make sure that there are no other elements that behave like the Name tag.
	  (The Name tag is present in multipe contexts, so our search for a top-level Name tag was returning unintended data.)
	- The "design break" step below should include consideration of what to do with the xml-downloading code at the bottom of this file.
	- Now it's time for a design break. 
	  Now that I know more about what I can do, I should look at my original questions and plot out a bit more detail on a good design for answering them. 
	  I should also try to come up with a couple more questions for the Canadian folks to go along with my record-count disparity question. 
	  I should also make sure that I've documented the high-level design of the code somewhere.
	  (It is increasingly looking like this will eventually be a repo for DB creation/import, a repo for analysis, and a repo for presentation)
 

"""


import sqlite3
import xml.etree.ElementTree as ET	
import time


def importOrgs(mode,connection,cursor):

	#The importOrgs() function takes in a mode, a connection and a cursor.
	#The mode should be a string - 'test' or 'live'. It determines which xml file we connect to.
	#The connection should be a sqlite3 connection object pointing at the relevant database.
	#The cursor should be a sqlite3 cursor object. 
	#This function parses a test or full fcsi xml file (depending on mode).
	#It then attempts to extract relevant fields from that file and import their values into the database.
	#The function has no return values for now, since we're doing smoke tests and using "print" statements. 
	#TODO: Make the function return a value.


	print 'This is the stub for the importOrgs() function.'
	print 'Our database tables have now been created/wiped.'
	print 'Reading XML for reporting organizations ...'
	if mode == 'test':
		tree = ET.parse('test-subset.xml')
	else:
		tree = ET.parse('fcsi-rscf.xml') 
	root = tree.getroot()
	orgCounter = 1	
	importdata = {}
	for org in root[0]:
		identifier = retrieve_reportingorganization_code(org) 
		importdata[identifier] = {}
		importdata[identifier]['reportingorganization_code'] = retrieve_reportingorganization_code(org)
		importdata[identifier]['reportingorganization_en'] = retrieve_reportingorganization_en(org)
		importdata[identifier]['reportingorganization_fr'] = retrieve_reportingorganization_fr(org)
		print importdata[identifier]['reportingorganization_fr']
		#Now to build the actual insert ... 
		#(Low-priority todo, since we basically trust the Canadian XML: Convert this to use paramaterized inserting, as PDO does)
		sql =  'INSERT INTO orgs '
		sql += '(OrgCode, OrgEN, OrgFR  '
		sql += ') '
		sql += 'VALUES(?,?,?) '
		print 'Importing org ' + str(orgCounter) + ' out of our total. '
		print '(As of the time when this script was drafted, that total was 26 orgs for the text XML and the same number for the live XML.)'
		cursor.execute(sql, (importdata[identifier]['reportingorganization_code'], importdata[identifier]['reportingorganization_en'], importdata[identifier]['reportingorganization_fr']) )
		connection.commit()
		orgCounter += 1


def retrieve_reportingorganization_code(org):
	#Function takes in an "org" element from our larger etree object.
	#It then attempts to return a code string we can store in our database.
	output = ''
	for code in org.iter('Code'):
		try:
			output = code.text.strip()
      		except AttributeError, e:
			output = '000 - org code not present in XML'
	return(output)

def retrieve_reportingorganization_en(org):
	#Function takes in an "org" element from our larger etree object.
	#It then attempts to return a code string we can store in our database.
	output = ''
	for en in org.iter('EN'):
		try:
			output = en.text.strip()
      		except AttributeError, e:
			output = '000 - English org name not present in XML'
	return(output)

def retrieve_reportingorganization_fr(org):
	#Function takes in an "org" element from our larger etree object.
	#It then attempts to return a code string we can store in our database.
	output = ''
	for fr in org.iter('FR'):
		try:
			output = fr.text.strip()
      		except AttributeError, e:
			output = '000 - French org name not present in XML'
	return(output)

def importSites(mode,connection,cursor):

	#The importSites() function takes in a mode, a connection and a cursor.
	#The mode should be a string - 'test' or 'live'. It determines which xml file we connect to.
	#The connection should be a sqlite3 connection object pointing at the relevant database.
	#The cursor should be a sqlite3 cursor object. 
	#This function parses a test or full fcsi xml file (depending on mode).
	#It then attempts to extract relevant fields from that file and import their values into the database.
	#The function has no return values for now, since we're doing smoke tests and using "print" statements. 
	#TODO: Make the function return a value.


	print 'This is the stub for the importSites() function.'
	print 'Our database tables have now been created/wiped.'
	print 'Reading XML for sites ...'
	if mode == 'test':
		tree = ET.parse('test-subset.xml')
	else:
		tree = ET.parse('fcsi-rscf.xml') 
	#^The test-subset document contains roughly 10,000 of the data from the actual doc.
	# I have pared it down for faster test runs when possible. 
	root = tree.getroot()
	siteCounter = 1	
	importdata = {}
	for site in root[1]:
		latitude = ''
		longitude = ''
		country_en = ''
		name_en = ''
		identifier = site.attrib['FederalSiteIdentifier']
		#A few of the assignments below might appear redundant to some folks. For me, they're worth it.  
		#(I found that it reduced my stress level to have all INSERT values coming from the same object.)
		importdata[identifier] = {}
		importdata[identifier]['FederalSiteIdentifier'] = site.attrib['FederalSiteIdentifier']
		importdata[identifier]['Name_EN'] = retrieveSiteName(site) 
		importdata[identifier]['SiteStatus_Status_EN'] = retrieveSiteStatusStatus(site)
		importdata[identifier]['Classification_Code'] = retrieveClassificationCode(site)
		importdata[identifier]['SiteStatus_Description_EN'] = retrieveSiteStatusDescription(site)
		importdata[identifier]['Location_Latitude'] = retrieveLocationLatitude(site)
		importdata[identifier]['Location_Longitude'] = retrieveLocationLongitude(site)
		importdata[identifier]['Location_Province'] = retrieveLocationProvince(site)
		importdata[identifier]['Location_Municipality'] = retrieveLocationMunicipality(site)
		importdata[identifier]['Location_Country_EN'] = retrieveLocationCountry(site)
		importdata[identifier]['FederalSiteIdentifier'] = site.attrib['FederalSiteIdentifier']
		importdata[identifier]['ReportingOrganization'] = site.attrib['ReportingOrganization']
		importdata[identifier]['Created'] = site.attrib['Created']
		importdata[identifier]['LastModified'] = site.attrib['LastModified']
		#Now to build the actual insert ... 
		#(Low-priority todo, since we basically trust the Canadian XML: Convert this to use paramaterized inserting, as PDO does)
		sql =  'INSERT INTO sites '
		sql += '(FederalSiteIdentifier, ReportingOrganization, Created, LastModified, Location_Latitude, '
		sql += 'Location_Longitude, Location_Province, Location_Municipality,Location_Country_EN, Name_EN, SiteStatus_Status_EN, SiteStatus_Description_EN, Classification_Code' 
		sql += ') '
		sql += ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) '
		print 'Importing site ' + site.attrib['FederalSiteIdentifier']	
		print 'This is site ' + str(siteCounter) + ' out of our total. '
		print '(As of the time when this script was drafted, that total was 46 sites for the text XML and just under 27K sites for the live XML.)'
		cursor.execute(sql,(importdata[identifier]['FederalSiteIdentifier'], importdata[identifier]['ReportingOrganization'], importdata[identifier]['Created'], importdata[identifier]['LastModified'], importdata[identifier]['Location_Latitude'], importdata[identifier]['Location_Longitude'], importdata[identifier]['Location_Province'], importdata[identifier]['Location_Municipality'], importdata[identifier]['Location_Country_EN'], importdata[identifier]['Name_EN'], importdata[identifier]['SiteStatus_Status_EN'],importdata[identifier]['SiteStatus_Description_EN'], importdata[identifier]['Classification_Code']))
		connection.commit()
		siteCounter += 1
		#^In our test-subset file, this should be a count of 46. 
		# In our real file, the count is 26,723.
		# This is a bit higher than the 22,799 described at http://www.tbs-sct.gc.ca/fcsi-rscf/classification-eng.aspx
		# Each FederalSiteIdentifier number is unique, so eliminating redundancies does nothing. 
		# TODO: I'll need to ask about why this number differs so significantly from the official number.
		#       (One very distinct possiblity is that the tally is simply an out-of-date manual tabulation someone compiled.
		#        The data dictionary appears to unintentionallly hint at this possibily with some out-of-date field names.
		#        Anyway, I should eventually ask about this, once I have a few questions to lump together.)

def retrieveLocationLatitude(site):
		#Function takes in a "site" element from our larger etree object.
		#It then attempts to return a latitude string we can store in our database.
		output = ''
		for location in site.iter('Location'):
			for subloc in location.iter():
				if subloc.tag == 'Latitude':
					output = subloc.text.strip()
		return(output)

def retrieveLocationLongitude(site):
		#Function takes in a "site" element from our larger etree object.
		#It then attempts to return a longitude string we can store in our database.
		output = ''
		for location in site.iter('Location'):
			for subloc in location.iter():
				if subloc.tag == 'Longitude':
					output = subloc.text.strip()
		return(output)

def retrieveLocationProvince(site):
		#Function takes in a "site" element from our larger etree object.
		#It then attempts to return a province string we can store in our database.
		output = ''
		for location in site.iter('Location'):
			for subloc in location.iter():
				if subloc.tag == 'Province':
					output = subloc.text.strip()
		return(output)

def retrieveLocationMunicipality(site):
		#Function takes in a "site" element from our larger etree object.
		#It then attempts to return a municipality string we can store in our database.
		output = ''
		for location in site.iter('Location'):
			for subloc in location.iter():
				if subloc.tag == 'Municipality':
					output = subloc.text.strip()
		return(output)

def retrieveLocationCountry(site):
		#Function takes in a "site" element from our larger etree object.
		#It then attempts to return a country string we can store in our database.
		output = ''
		for location in site.iter('Location'):
			for subloc in location.iter():
				if subloc.tag == 'Country':
					english = ''
					for english in subloc.iter('EN'):
						output = english.text.strip()
		return(output)

def retrieveSiteName(site):
		#Function takes in a "site" element from our larger etree object.
		#It then attempts to return a name string we can store in our database.
		output = ''
		loopcount = 0
		for name in site.iter('Name'):
			if(loopcount == 0):
			#^Conditional makes sure I only get top-level Name elements.
			# I can rely on the order of our returned tags, since the etree documentation explicitly states that iter() gives us a specific order.
			# Specifically, it says iteration is "in document (depth first) order."
			# (This reliability is worth mentioning, since some methods -- like items() -- explicitly return results in an arbitrary order.
				loopcount = 1	
				englishname = ''
				for englishname in name.iter('EN'):
					try:
						output = englishname.text.strip()
					except AttributeError, e:
						output = '000 - english site name not present in XML'
		return(output)

def retrieveSiteStatusStatus(site):
		#Function takes in a "site" element from our larger etree object.
		#It then attempts to return a status string we can store in our database.
		output = ''
		for sitestatus in site.iter('SiteStatus'):
			for status in sitestatus.iter('Status'):
				for enstatus in status.iter('EN'):
					try:
						output = enstatus.text.strip()
					except:
						output = '000 - nostatus'
		return(output)

def retrieveClassificationCode(site):
		#Function takes in a "site" element from our larger etree object.
		#It then attempts to return a classification code we can store in our database.
		output = ''
		for classification in site.iter('Classification'):
			for code in classification.iter('Code'):
					try:
						output = code.text.strip()
					except:
						output = '000 - nocode'
		return(output)

def retrieveSiteStatusDescription(site):
		#Function takes in a "site" element from our larger etree object.
		#It then attempts to return a status string we can store in our database.
		output = ''
		for sitestatus in site.iter('SiteStatus'):
			english = ''
			for english in sitestatus.iter('EN'):
				try:
					output = english.text.strip()
        			except AttributeError, e:
					output = '000 - english site status description not present in XML'
		return(output)


def dumpSitesForCompare(mode,connection,cursor):
	#The dumpSitesForCompare() function takes in a mode, a connection and a cursor..
	#The connection should be a sqlite3 connection object pointing at the relevant database.
	#The cursor should be a sqlite3 cursor object. 
	#This function dumps the contents of our "sites" table to a file.
	#A unit test (in a different script) can compare our output against a previously stored file.
	#This will be a late-stage unit test that confirms the relative integrity of our importer.
	#This function assumes test mode, since live data is inherently likely to change, making comparisons useless.
	#TODO: Make the function return a value.
	if mode == "test":
		sql = 'SELECT * FROM sites;'
		fh = open('test-db-dump-for-compare-output.txt','w')
		result = cursor.execute(sql)
		for row in result.fetchall():
			fh.write('||||||||')
			for field in row:
				try:
					fh.write(field)
				except UnicodeEncodeError, e:
					print "--Ignoring unicode encoding error in our dump, since we just need to compare test output ... --"
		print "our sites table has been dumped into test-db-dump-for-compare-output.txt"
	else:
		print "no table output has been dumped, since we're using live data."
	

def initSitesTable(connection):
	#The initSitesTable function takes in a connection to a database.
	#It then drops any existing "sites" table, creates a new "sites" table and commits all actions.
	#The function returns a cursor object. 
	print 'This is the stub for the initSitesTable() function.'
	print 'Creating or wiping database table ... '
	cursor = connection.cursor()
	cursor.execute('DROP TABLE IF EXISTS SITES')
	cursor.execute('''CREATE TABLE sites 
		       (FederalSiteIdentifier TEXT, ReportingOrganization TEXT, Created TEXT, LastModified TEXT, Location_Latitude TEXT, Location_Longitude TEXT, Location_Province TEXT, Location_Municipality TEXT, Location_Country_EN TEXT, Name_EN TEXT, SiteStatus_Status_EN, Classification_Code TEXT,  SiteStatus_Description_EN TEXT)''')
	connection.commit()
	return(cursor)

def initOrgsTable(connection):
	#The initOrgsTable function takes in a connection to a database.
	#It then drops any existing "orgs" table, creates a new "orgs" table and commits all actions.
	#The function returns a cursor object. 
	print 'This is the stub for the initOrgsTable() function.'
	print 'Creating or wiping database table ... '
	cursor = connection.cursor()
	cursor.execute('DROP TABLE IF EXISTS ORGS')
	cursor.execute('''CREATE TABLE orgs 
		       (OrgCode TEXT, OrgEN TEXT, OrgFR TEXT)''')
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
		print 'Note: As of early 2016, this import of the full, live data can take a long time -- up to 15 minutes, depending on your machine -- to complete.'
		connection = sqlite3.connect('fcsi-live.db')
	return(connection)



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


mode = 'test'
#mode = 'live'
connection = createConnection(mode)
cursor = initSitesTable(connection)
cursor = initOrgsTable(connection)
importSites(mode,connection,cursor)
importOrgs(mode,connection,cursor)
dumpSitesForCompare(mode,connection,cursor)
