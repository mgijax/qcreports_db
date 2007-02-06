#!/usr/local/bin/python

'''
#
# PRB_Strain4.py
#
# Report:
#       Tab-delimited file
#       Strains with MGI ID and > 1 external ID
#
# Used by:
#       Internal Report
#
# Notes:
#
# History:
#
# 11/02/2006	lec
#	- TR 7983
#
'''
 
import sys
import os
import string
import db
import mgi_utils
import reportlib

TAB = reportlib.TAB
CRT = reportlib.CRT

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], title = 'Strains with MGI IDs that have more than one additional external ID')

# strains with MGI IDs

db.sql('select distinct a._Object_key, a.accID, s.strain ' + \
	'into #strains ' + \
	'from ACC_Accession a, PRB_Strain s ' + \
	'where a._MGIType_key = 10 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.preferred = 1 ' + \
	'and a._Object_key = s._Strain_key', None)
db.sql('create index idx1 on #strains(_Object_key)', None)

# external accession IDs

results = db.sql('select distinct a._Object_key, a.accID, l.name ' + \
	'from #strains s, ACC_Accession a, ACC_LogicalDB l ' + \
	'where s._Object_key = a._Object_key ' + \
	'and a._LogicalDB_key != 1 ' + \
	'and a._MGIType_key = 10 ' + \
	'and a._LogicalDB_key = l._LogicalDB_key', 'auto')
externalIDs = {}
for r in results:
	key = r['_Object_key']
	value = r['accID'] + ' (' + r['name'] + ')'
	if not externalIDs.has_key(key):
		externalIDs[key] =[]
	externalIDs[key].append(value)

# process

rows = 0
results = db.sql('select * from #strains order by strain', 'auto')
for r in results:
    key = r['_Object_key']

    if not externalIDs.has_key(key):
        continue

    if len(externalIDs[key]) == 1:
        continue

    fp.write(r['accID'] + TAB)
    fp.write(r['strain'] + TAB)
    fp.write(string.join(externalIDs[key], ',') + CRT)
    rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))
reportlib.finish_nonps(fp)

