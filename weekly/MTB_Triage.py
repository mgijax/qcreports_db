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
#
'''
 
import sys 
import os
import string
import db
import reportlib
import mgi_utils

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

db.sql('select r._Refs_key ' + \
	'into #triage ' + \
	'from BIB_Refs r, BIB_DataSet_Assoc a ' + \
	'where r.creation_date between "%s" and "%s" ' % (fromDate, toDate) + \
	'and r._Refs_key = a._Refs_key ' + \
	'and a._DataSet_key = 1007', None)

db.sql('create index idx1 on #triage(_Refs_key)', None)

results = db.sql('select b.authors, b.authors2, b.title, b.journal, b.year, b.vol, b.issue, b.pgs, b.abstract, ' + \
	'jnumID = a1.accID, pubmedID = a2.accID ' + \
	'from #triage t, BIB_Refs b, ACC_Accession a1, ACC_Accession a2 ' + \
	'where t._Refs_key = b._Refs_key ' + \
	'and b._Refs_key = a1._Object_key ' + \
	'and a1._LogicalDB_Key = 1 ' + \
	'and a1.prefixPart = "J:" ' + \
	'and t._Refs_key *= a2._Object_key ' + \
	'and a2._LogicalDB_Key = 29 ' + \
	'order by jnumID', 'auto')

for r in results:
    fp.write(r['jnumID'] + TAB)

    pubmedID = r['pubmedID']
    if pubmedID == None:
	pubmedID = 'Null'
    fp.write(pubmedID  + TAB)
   
    author1 = r['authors']
    author2 = r['authors2']
    # if author empty, no authors
    if author1 == None:
        authors = 'Null'
    # if author not empty and author2 empty
    elif author2 == None:
	authors = author1
    # both author and author2 not empty
    else:
	authors = author1 + author2
     
    fp.write(authors + TAB)

    title = r['title']
    if title == None:
        title = 'Null'
    fp.write(title + TAB)

    journal = r['journal']
    if journal == None:
        journal = 'Null'
    fp.write(journal + TAB)

    year = str(r['year'])
    if year == None:
        year = 'Null'
    fp.write(year + TAB)

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

    abstract = r['abstract']
    if abstract == None:
        abstract = 'Null'
    fp.write(abstract + CRT)

reportlib.finish_nonps(fp)	# non-postscript file

