#!/usr/local/bin/python

'''
#
# HMD_MouseSeq1.py 05/16/2003
#
# Report:
#       Tab-delimited file (originally an SQL report)
#	Mouse Genes with Sequence ID but no Human Orthology
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

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

fp.write('Mouse Genes with Sequence ID but no Human Orthology' + CRT)
fp.write('(Excludes RIKEN genes, Expressed Sequence, EST, Hypothetical)' + 2*CRT)

fp.write('Symbol                     ')
fp.write('Status      ')
fp.write('Seq ID' + CRT)
fp.write(50 * '-' + '  ')
fp.write(10 * '-' + '  ')
fp.write(30 * '-' + CRT)

db.sql('select distinct m._Marker_key, m.symbol, s.status ' + \
	'into #markers ' + \
	'from MRK_Marker m, MRK_Status s ' + \
	'where m._Organism_key = 1 ' + \
	'and m._Marker_Type_key = 1 ' + \
	'and m.symbol not like "%Rik" ' + \
	'and m.name not like "%expressed%" ' + \
	'and m.name not like "EST %" ' + \
	'and m.name not like "%hypothetical%" ' + \
	'and m._Marker_Status_key = s._Marker_Status_key ' + \
	'and exists (select 1 from ACC_Accession a ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_Key in (9, 27)) ' + \
	'and not exists (select 1 from MRK_Homology_Cache h1, MRK_Homology_Cache h2 ' + \
	'where m._Marker_key = h1._Marker_key ' + \
	'and h1._Class_key = h2._Class_key ' + \
	'and h2._Organism_key = 2)', None)
db.sql('create index idx1 on #markers(_Marker_key)', None)
db.sql('create index idx2 on #markers(symbol)', None)

results = db.sql('select m._Marker_key, a.accID ' + 
	'from #markers m, ACC_Accession a ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_Key in (9, 27)', 'auto')
seqIDs = {}
for r in results:
	if seqIDs.has_key(r['_Marker_key']):
		seqIDs[r['_Marker_key']].append(r['accID'])
	else:
		seqIDs[r['_Marker_key']] = []
		seqIDs[r['_Marker_key']].append(r['accID'])

results = db.sql('select * from #markers order by symbol', 'auto')
for r in results:
	fp.write(string.ljust(r['symbol'], 27) + \
	        string.ljust(r['status'], 12) + \
		string.joinfields(seqIDs[r['_Marker_key']], ',') + CRT)

rows = len(results)
fp.write('\n(%d rows affected)\n' % (rows))

reportlib.finish_nonps(fp)

