#!/usr/bin/env python

from imptfunctions import *

mode = 'test'
connection = createConnection(mode)
cursor = initSitesTable(connection)
cursor = initOrgsTable(connection)
importSites(mode,connection,cursor)
importOrgs(mode,connection,cursor)
dumpSitesForCompare(mode,connection,cursor)
