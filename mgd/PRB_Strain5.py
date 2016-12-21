#!/usr/local/bin/python

'''
#
# PRB_Strain5.py
#
# Report:
#       Tab-delimited file
#       Strains where any of their IDs contain an "O" (oooh)
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
import mgi_utils
import reportlib
import db

db.setTrace()

TAB = reportlib.TAB
CRT = reportlib.CRT

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], title = 'Strains where any of their IDs contain an "O"')

db.sql('''
	select distinct s._Strain_key, s.strain 
	into temporary table strains 
	from PRB_Strain s, ACC_Accession a 
	where s._Strain_key = a._Object_key 
	and a._MGIType_key = 10 
	and a._LogicalDB_key != 1 
	and a.accID like '%O%' 
	''', None)
db.sql('create index strains_idx on strains(_Strain_key)', None)

# external accession IDs

results = db.sql('''
	select distinct s._Strain_key, a.accID, l.name 
	from strains s, ACC_Accession a, ACC_LogicalDB l 
	where s._Strain_key = a._Object_key 
	and a._LogicalDB_key != 1 
	and a._MGIType_key = 10 
	and a._LogicalDB_key = l._LogicalDB_key
	''', 'auto')
externalIDs = {}
for r in results:
	key = r['_Strain_key']
	value = r['accID'] + ' (' + r['name'] + ')'
	if not externalIDs.has_key(key):
		externalIDs[key] =[]
	externalIDs[key].append(value)

# process

results = db.sql('select * from strains order by strain', 'auto')
for r in results:
    key = r['_Strain_key']
    fp.write(r['strain'] + TAB)
    fp.write(string.join(externalIDs[key], ',') + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)

