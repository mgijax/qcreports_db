#!/usr/local/bin/python

'''
#
# MTB_Triage.py
#
# Report:
#       Weekly MTB Triage Report
#
# Usage:
#       MTB_Triage.py
#
# Notes:
#	- all reports use mgireport directory for output file
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- use proper case for all table and column names e.g. 
#         use MRK_Marker not mrk_marker
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
# 	- minor modifications to use the modification date, rather than the
#	  creation date for this report.
#
# 03/18/2014	lec
#	- TR11621/add reference information to this report
#
'''
 
import sys 
import os
import string
import mgi_utils
import reportlib

try:
    if os.environ['DB_TYPE'] == 'postgres':
        import pg_db
        db = pg_db
        db.setTrace()
        db.setAutoTranslateBE()
    else:
        import db
except:
    import db


CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE
reportlib.column_width = 150

#
# Main
#

currentDate = mgi_utils.date('%m/%d/%Y')
fromDate = db.sql('select convert(char(10), dateadd(day, -7, "%s"), 101) ' % (currentDate), 'auto')[0]['']
toDate = db.sql('select convert(char(10), dateadd(day, -1, "%s"), 101) ' % (currentDate), 'auto')[0]['']

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], fileExt = '.' + os.environ['DATE'] + '.txt', printHeading = None)

db.sql('''
	select r._Refs_key 
	into #triage 
	from BIB_Refs r, BIB_DataSet_Assoc a 
	where r.modification_date between '%s' and '%s' 
	and r._Refs_key = a._Refs_key 
	and a._DataSet_key = 1007
	''' % (fromDate, toDate), None)

db.sql('create index idx1 on #triage(_Refs_key)', None)

results = db.sql('''
	select b.authors, b.authors2, b.title, b.title2, b._primary, 
	       b.journal, b.year, 
	       b.vol, b.issue, b.pgs, b.abstract, 
	       a2.accID as pubmedID,
	       c.jnumID, c.citation, c.short_citation, c.reviewStatus
	from #triage t, BIB_Refs b, ACC_Accession a2, BIB_Citation_Cache c
	where t._Refs_key = b._Refs_key 
	and t._Refs_key *= a2._Object_key 
	and a2._LogicalDB_Key = 29 
	and b._Refs_key = c._Refs_key
	order by jnumID
	''', 'auto')

for r in results:

    fp.write(r['jnumID'] + TAB)

    pubmedID = r['pubmedID']
    if pubmedID == None:
	pubmedID = 'Null'
    fp.write(pubmedID + TAB)

    title = r['title']
    if title == None:
	title = 'Null'
    fp.write(title + TAB)

    title2 = r['title2']
    if title2 == None:
	title2 = 'Null'
    fp.write(title2 + TAB)

    authors = r['authors']
    if authors == None:
	authors = 'Null'
    fp.write(authors + TAB)

    authors2 = r['authors2']
    if authors2 == None:
	authors2 = 'Null'
    fp.write(authors2 + TAB)

    fp.write(r['_primary'] + TAB)
    fp.write(r['citation'] + TAB)
    fp.write(r['short_citation'] + TAB)

    journal = r['journal']
    if journal == None:
        journal = 'Null'
    fp.write(journal + TAB)

    vol = r['vol']
    if vol == None:
        vol = 'Null'
    fp.write(vol + TAB)

    issue = r['issue']
    if issue == None:
        issue = 'Null'
    fp.write(issue + TAB)

    pgs = r['pgs']
    if pgs == None:
        pgs = 'Null'
    fp.write(pgs + TAB)

    year = str(r['year'])
    if year == None:
        year = 'Null'
    fp.write(year + TAB)

    fp.write(r['reviewStatus'] + TAB)

    abstract = r['abstract']
    if abstract == None:
        abstract = 'Null'
    fp.write(abstract + CRT)

reportlib.finish_nonps(fp)	# non-postscript file

