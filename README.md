# FCSI importer

This is a small set of tools I created in 2016 as a chance to play with Python a bit. It is not terribly professional -- witness the fact that the tools still live in a "drafts" folder, for instance -- but I'm putting it up as-is in case it can be adapted in a helpful way for someone else.

TODO: Now that some of the old Python 2 libraries this is built on are dead, redo this as a Symfony/MySQL app, building out a frontend that shows global sites on a map. Then report on what that map shows, sending it to the blog if necessary.

-----------------------------------
-----------------------------------
-----------------------------------

## MANDATORY FUN 

To get a basic FCSI database up and running, do the following:

-- Install python2 and virtualenvwrapper if needed

-- cd to the "drafts" folder.

-- Use   source ~/.virtualenvs/ccs/bin/activate  (or your method of choice) to activate a virtualenv and then ... 

-- Use   pip install -r requirements.txt   to install all required libraries. 

-- Use   python2 run-unit-tests.py   to run some basic unit tests. (You should get "OK" as your result. Any other result probably means you're missing a dependency.)

-- Use   python2 import-test-records.py   to import a set of test records into a testing version of our database. You should get a screenfull of text.  

-- Now run     diff test-db-dump-for-compare-output.txt test-db-dump-for-compare-baseline.txt

(^This should result in no differences -- just another command prompt. If you see a bunch of text, something is wrong.)

-- Assuming everything has worked so far, you can now safely run the following commands ... 

-- wget https://map-carte.tbs-sct.gc.ca/fcsi-rscf/oddo/fcsi-rscf.zip 

-- unzip fcsi-rscf.zip

-- python2 import-live-records.py

-- python2 create-municipal-tally-table.py

-- sqlite3 fcsi-live.db

... and there you are! You've got a database containing a bunch of the basic FCSI data. A couple more notes: 

-- The "cities" table contains tallies of the active, priority-1 sites in each municipality. 

-- Try     SELECT * FROM sites;    and    SELECT * FROM cities;     to get started. Also     SELECT * FROM orgs;

-- Note that some "number" columns have imported as text and will need to be explicitly cast as numbers. Mea culpa. 

-- You can view table structure via the   PRAGMA table_info(cities);    command.

Feel free to modify this setup for your own needs. 



-----------------------------------
-----------------------------------
-----------------------------------

## OPTIONAL FUN

create a geojson dump of the half-dozen most populated (in a 5km radius) high-priority sites

-- python2 create-geojson.py

-- cp data.json ~/path/to/where/you/want/it.json



-----------------------------------
-----------------------------------
-----------------------------------

## MORE OPTIONAL FUN

To get site counts by country, I do this:

SELECT COUNT(*) AS TheCount, Location_Country_EN FROM sites GROUP BY Location_Country_EN ORDER BY TheCount DESC;

... and if I just want the countries, do this:

SELECT Location_Country_EN FROM sites GROUP BY Location_Country_EN;

... which gives me the following list: 

Australia,Austria,Brazil,Canada,Chile,China,Costa Rica,Côte d'Ivoire,Denmark,Dominican Republic,Egypt,Ethiopia,Finland,France,French Polynesia,Ghana,Guyana,Haiti,Italy,Jamaica,Jordan,Kenya,Korea (South), Republic of,Kuwait,Kyrgyzstan,Mexico,Morocco,Mozambique,Peru,Russian Federation,Rwanda,Saint Pierre and Miquelon,Saudi Arabia,Senegal,Serbia,Sudan,Syrian Arab Republic,Tanzania, United Republic of,Ukraine,United Arab Emirates,United Kingdom,United States,Zimbabwe

... which I can manually narrow to continential European countries like so:

Austria,Denmark,Finland,France,Italy,Russian Federation,Serbia,United Kingdom

... which I can then insert into a query to get European site counts by country: 

"Austria","Denmark","Finland","France","Italy","Russian Federation","Serbia","United Kingdom"

SELECT COUNT(*) AS TheCount, Location_Country_EN FROM sites WHERE Location_Country_EN IN("Austria","Denmark","Finland","France","Italy","Russian Federation","Serbia","United Kingdom") GROUP BY Location_Country_EN ORDER BY TheCount DESC;

... and maybe I want the "reporting organization" tallies for those? 

SELECT COUNT(*) AS TheCount, ReportingOrganization FROM sites WHERE Location_Country_EN IN("Austria","Denmark","Finland","France","Italy","Russian Federation","Serbia","United Kingdom") GROUP BY ReportingOrganization ORDER BY TheCount DESC;

... which gives me this result:

24|EXT
1|DFO
1|DND

... meaning that I would want to reach out to Global Affairs Canada, Fisheries and Oceans Canada and National Defence (in that order of priority) if I were doing a Europe-based story.

(I would also wish to reach out to the Treasury Board Secretariat, but I would probably do so after talking to the groups above.)  





