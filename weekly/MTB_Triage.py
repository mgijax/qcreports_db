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
# lec   10/22/2014
#       - TR11750/postres complient
#
# 03/18/2014	lec
#	- TR11621/add reference information to this report
#
'''
 
import sys 
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE
reportlib.column_width = 150

#
# Main
#

fromDate = "current_date - interval '7 days'"
toDate = "current_date - interval '1 day'"

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], fileExt = '.' + os.environ['DATE'] + '.txt', printHeading = None)

db.sql('''
	select r._Refs_key 
	into temporary table triage 
	from BIB_Refs r, BIB_DataSet_Assoc a 
	where r.modification_date between %s and %s 
	and r._Refs_key = a._Refs_key 
	and a._DataSet_key = 1007
	''' % (fromDate, toDate), None)

db.sql('create index idx1 on triage(_Refs_key)', None)

results = db.sql('''
	select b.authors, b.title, b._primary, 
	       b.journal, b.year, 
	       b.vol, b.issue, b.pgs, b.abstract, 
	       a2.accID as pubmedID,
	       c.jnumID, c.citation, c.short_citation, c.reviewStatus
	from triage t
		LEFT OUTER JOIN ACC_Accession a2 on (t._Refs_key = a2._Object_key
					and a2._LogicalDB_Key = 29),
	     BIB_Refs b, BIB_Citation_Cache c
	where t._Refs_key = b._Refs_key 
	and b._Refs_key = c._Refs_key
	order by c.jnumID
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

    authors = r['authors']
    if authors == None:
	authors = 'Null'
    fp.write(authors + TAB)

    _primary = r['_primary']
    if _primary == None:
	_primary = 'Null'
    fp.write(_primary + TAB)

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

