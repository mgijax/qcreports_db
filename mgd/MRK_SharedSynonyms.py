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

title = 'Markers w/ Shared Synonyms\n'
fp = reportlib.init(sys.argv[0], title = title, outputdir = os.environ['QCREPORTOUTPUTDIR'])

fp.write(string.ljust('synonym', 50) + \
 	 'symbols' + CRT)

fp.write('-' * 50 + '  ' + \
	 '-' * 50 + CRT)

cmds = []

cmds.append('select distinct name = substring(name,1,50) ' + \
	'into #shared ' + \
	'from MRK_Other ' + \
	'group by name having count(*) > 1')

cmds.append('select distinct sym1 = m1.symbol, sym2 = m2.symbol, s.name ' + \
	'from #shared s, MRK_Marker m1, MRK_Marker m2, MRK_Other o1, MRK_Other o2 ' + \
	'where s.name = o1.name ' + \
	'and s.name = o2.name ' + \
	'and o1._Marker_key = m1._Marker_key ' + \
	'and o2._Marker_key = m2._Marker_key ' + \
	'and m1._Marker_key != m2._Marker_key ' + \
	'order by s.name')

results = db.sql(cmds, 'auto')

# store dictionary of synonyms
syns = {}
for r in results[1]:
	key = r['name']
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
reportlib.trailer(fp)
reportlib.finish_nonps(fp)	# non-postscript file

