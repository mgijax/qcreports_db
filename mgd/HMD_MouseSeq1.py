#!/usr/local/bin/python

'''
#
# HMD_MouseSeq1.py 05/16/2003
#
# Report:
#       Tab-delimited file (originally an SQL report)
#	Mouse Genes with Sequence ID but no Human Homology
#	Excludes RIKEN genes, Expressed Sequence, EST, Hypothetical
#
#	symbol
#	comma-separated list of Seq IDs
#
# Usage:
#       HMD_MouseSeq1.py
#
# Used by:
#       Internal Report
#
# Notes:
#
# History:
#
# lec	05/16/2003
#	- TR 4815
#
'''
 
import sys
import os
import string
import db
import mgi_utils
import reportlib

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCREPORTOUTPUTDIR'])

fp.write('Mouse Genes with Sequence ID but no Human Homology' + CRT)
fp.write('(Excludes RIKEN genes, Expressed Sequence, EST, Hypothetical)' + 2*CRT)

fp.write('Symbol                     ')
fp.write('Status      ')
fp.write('Seq ID' + CRT)
fp.write(25 * '-' + '  ')
fp.write(10 * '-' + '  ')
fp.write(30 * '-' + CRT)

cmds = []

cmds.append('select distinct m._Marker_key, m.symbol, s.status ' + \
	'into #markers ' + \
	'from MRK_Marker m, MRK_Status s ' + \
	'where m._Species_key = 1 ' + \
	'and m._Marker_Type_key = 1 ' + \
	'and m.symbol not like "%Rik" ' + \
	'and m.name not like "%expressed%" ' + \
	'and m.name not like "EST %" ' + \
	'and m.name not like "%hypothetical%" ' + \
	'and m._Marker_Status_key = s._Marker_Status_key ' + \
	'and exists (select 1 from MRK_ACC_View a ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._LogicalDB_Key in (9, 27)) ' + \
	'and not exists (select 1 from HMD_Homology h1, HMD_Homology_Marker hm1, ' + \
	'HMD_Homology h2, HMD_Homology_Marker hm2, MRK_Marker m2 ' + \
	'where hm1._Marker_key = m._Marker_key ' + \
	'and hm1._Homology_key = h1._Homology_key ' + \
	'and h1._Class_key = h2._Class_key ' + \
	'and h2._Homology_key = hm2._Homology_key ' + \
	'and hm2._Marker_key = m2._Marker_key ' + \
	'and m2._Species_key = 2)')

cmds.append('select m._Marker_key, a.accID ' + 
	'from #markers m, MRK_ACC_View a ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._LogicalDB_Key in (9, 27)')

cmds.append('select * from #markers order by symbol')

results = db.sql(cmds, 'auto')

seqIDs = {}
for r in results[-2]:
	if seqIDs.has_key(r['_Marker_key']):
		seqIDs[r['_Marker_key']].append(r['accID'])
	else:
		seqIDs[r['_Marker_key']] = []
		seqIDs[r['_Marker_key']].append(r['accID'])
	
for r in results[-1]:

	fp.write(string.ljust(r['symbol'], 27) + \
	        string.ljust(r['status'], 12) + \
		string.joinfields(seqIDs[r['_Marker_key']], ',') + CRT)

rows = len(results[-1])
fp.write('\n(%d rows affected)\n' % (rows))

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

