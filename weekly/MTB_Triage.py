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

results = db.sql('select authors = b.authors + b.authors2, b.title, b.journal, b.year, b.vol, b.issue, b.pgs, b.abstract, ' + \
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
    fp.write(r['pubmedID']  + TAB)
    fp.write(r['authors'] + TAB)
    fp.write(r['title'] + TAB)
    fp.write(r['journal'] + TAB)
    fp.write(str(r['year']) + TAB)
    fp.write(r['vol'] + TAB)
    fp.write(r['issue'] + TAB)
    fp.write(r['pgs'] + TAB)
    fp.write(r['abstract'] + CRT)

reportlib.finish_nonps(fp)	# non-postscript file

