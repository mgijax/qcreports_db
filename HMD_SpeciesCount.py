#!/usr/local/bin/python

'''
#
# HMD_SpeciesCount.py 11/20/98
#
# Report:
#	Count of Mouse Homologies for each Species
#	Sorted by Count
#
# Usage:
#       HMD_SpeciesCount.py
#
# Generated from:
#       Nightly Reports
#
# Notes:
#
# History:
#
# lec	11/20/1998
#	- created
#
'''
 
import sys
import os
import string
import db
import reportlib

CRT = reportlib.CRT
TAB = reportlib.TAB
fp = reportlib.init(sys.argv[0], 'Counts of Mouse Homologies by Species', os.environ['QCREPORTOUTPUTDIR'])

speciesResults = []

species = db.sql('select _Species_key, name from MRK_Species where _Species_key > 1', 'auto')

for s in species:

	cmd = 'select count(distinct r1._Class_key) ' + \
	      'from HMD_Homology r1, HMD_Homology_Marker h1, ' + \
	      'HMD_Homology r2, HMD_Homology_Marker h2, MRK_Marker m1, MRK_Marker m2 ' + \
	      'where m1._Species_key = %s' % s['_Species_key'] + \
	      'and m1._Marker_key = h1._Marker_key ' + \
	      'and h1._Homology_key = r1._Homology_key ' + \
	      'and r1._Class_key = r2._Class_key ' + \
	      'and r2._Homology_key = h2._Homology_key ' + \
	      'and h2._Marker_key = m2._Marker_key ' + \
	      'and m2._Species_key = 1'

	results = db.sql(cmd, 'auto')

	for r in results:
		speciesResults.append(tuple([r[''], s['name'], s['_Species_key']]))

speciesResults.sort()
for s in speciesResults:
	fp.write(string.ljust(s[1], 50))
	fp.write(str(s[0]) + TAB)
	fp.write('(key = ' + str(s[2]) + ')' + CRT)

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

