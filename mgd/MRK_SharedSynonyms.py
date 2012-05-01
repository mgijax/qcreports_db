#!/usr/local/bin/python

'''
#
# MRK_SharedSynonyms.py 12/29/2003
#
# Report:
#       TR 5449
#
#	Title = Markers w/ Shared Synonyms
#
#       Report in a tab delimited file with the following columns:
#
#    		synonyms
#		list of markers with that synonym
#
# Usage:
#       MRK_SharedSynonyms.py
#
# Notes:
#	- all reports use mgireport directory for output file
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
#
# lec	12/29/2003
#	- created
#
'''
 
import sys 
import os
import string
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

db.useOneConnection(1)

title = 'Markers with Shared Synonyms\n'
fp = reportlib.init(sys.argv[0], title = title, outputdir = os.environ['QCOUTPUTDIR'])

fp.write(string.ljust('synonym', 50) + \
 	 'symbols' + CRT)

fp.write('-' * 50 + '  ' + \
	 '-' * 50 + CRT)

db.sql('select s._Object_key, s._MGIType_key, synonym = substring(s.synonym,1,50) ' + \
	'into #synonyms1 ' + \
	'from MGI_Synonym s, MGI_SynonymType st ' + 
	'where s._MGIType_key = 2 ' + \
	'and s._SynonymType_key = st._SynonymType_key ' + \
	'and st._Organism_key = 1', None)
db.sql('create index syn1_idx1 on #synonyms1(synonym)', None)
db.sql('create index syn1_idx2 on #synonyms1(_Object_key)', None)
db.sql('create index syn1_idx3 on #synonyms1(_MGIType_key)', None)

db.sql('select synonym into #synonyms2 from #synonyms1 group by synonym having count(*) > 1', None)
db.sql('create index syn2_idx1 on #synonyms2(synonym)', None)

results = db.sql('select distinct sym1 = m1.symbol, sym2 = m2.symbol, s.synonym ' + \
	'from #synonyms1 s1, #synonyms1 s2, #synonyms2 s, MRK_Marker m1, MRK_Marker m2 ' + \
	'where s.synonym = s1.synonym ' + \
	'and s.synonym = s2.synonym ' + \
	'and s1._MGIType_key = 2 ' + \
	'and s2._MGIType_key = 2 ' + \
	'and s1._Object_key != s2._Object_key ' + \
	'and s1._Object_key = m1._Marker_key ' + \
	'and s2._Object_key = m2._Marker_key ' + \
	'order by s.synonym', 'auto')

# store dictionary of synonyms
syns = {}
for r in results:
	key = r['synonym']
	value1 = r['sym1']
	value2 = r['sym2']

	if not syns.has_key(key):
		syns[key] = []

	if value1 not in syns[key]:
		syns[key].append(value1)

	if value2 not in syns[key]:
		syns[key].append(value2)

rows = 0
synKeys = syns.keys()
synKeys.sort()

for s in synKeys:
	fp.write(string.ljust(s, 50) + \
	 	 string.joinfields(syns[s], ',') + CRT)
	rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))
reportlib.finish_nonps(fp)	# non-postscript file
db.useOneConnection(0)

