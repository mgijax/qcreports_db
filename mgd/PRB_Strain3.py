#!/usr/local/bin/python

'''
#
# PRB_Strain3.py 09/27/2001
#
# Report:
#       Tab-delimited file
#       All Non-Standard Strains that have a MGI ID or External ID
#
# Usage:
#       PRB_Strain3.py
#
# Used by:
#       Internal Report
#
# Notes:
#
# History:
#
# 03/10/2006	lec
#	- TR 7554
#
'''
 
import sys
import os
import string
import db
import mgi_utils
import reportlib

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

fp.write('Public Non-Standard Strains that have a MGI ID or an External ID\n\n')

fp.write(string.ljust('Strain', 75))
fp.write(string.ljust('MGI ID', 25))
fp.write(string.ljust('External IDs', 35))
fp.write(reportlib.CRT)

fp.write(string.ljust('------', 75))
fp.write(string.ljust('------', 25))
fp.write(string.ljust('------------', 35))
fp.write(reportlib.CRT *2)

# Non-Standard Strains
db.sql('select _Strain_key, strain = substring(strain,1,70) ' + \
	'into #strains from PRB_Strain where standard = 0 and private = 0', None)
db.sql('create index idx1 on #strains(_Strain_key)', None)

# Retrieve MGI Accession number

results = db.sql('select distinct s._Strain_key, a.accID from #strains s, ACC_Accession a ' + \
	'where s._Strain_key = a._Object_key ' + \
	'and a._MGIType_key = 10 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1 ', 'auto')
mgiIDs = {}
for r in results:
	mgiIDs[r['_Strain_key']] = r['accID']

# External Accession IDs

results = db.sql('select distinct s._Strain_key, a.accID, l.name ' + \
	'from #strains s, ACC_Accession a, ACC_LogicalDB l ' + \
	'where s._Strain_key = a._Object_key ' + \
	'and a._LogicalDB_key != 1 ' + \
	'and a._MGIType_key = 10 ' + \
	'and a._LogicalDB_key = l._LogicalDB_key', 'auto')
extIDs = {}
for r in results:
	key = r['_Strain_key']
	value = '%s (%s)' % (r['accID'], r['name'])
	if not extIDs.has_key(key):
		extIDs[key] = []
	extIDs[key].append(value)

# Process

rows = 0
results = db.sql('select * from #strains order by strain', 'auto')
for r in results:
    key = r['_Strain_key']

    if mgiIDs.has_key(key) or extIDs.has_key(key):
        fp.write(string.ljust(r['strain'], 75))

        if mgiIDs.has_key(key):
            fp.write(string.ljust(mgiIDs[key], 25))
	else:
	    fp.write(string.ljust('', 25))

	if extIDs.has_key(key):
	    fp.write(string.join(extIDs[key], ', '))
	fp.write(reportlib.CRT)

	rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

