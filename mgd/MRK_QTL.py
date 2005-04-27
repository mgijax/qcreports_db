#!/usr/local/bin/python

'''
#
# MRK_QTL.py 07/18/2003
#
# Report:
#       QTL Mouse Markers that have been added since March 2002
#	and have no MP associations
#
# Usage:
#       MRK_QTL.py
#
# Used by:
#
# Notes:
#
# History:
#
# lec	07/18/2003
#	- TR 4992
#
'''

import sys
import os
import string
import db
import reportlib

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

fp.write('QTL Markers added to MGI since March 2002 with no MP annotations')
fp.write(reportlib.CRT*2)

fp.write(string.ljust('MGI ID', 30))
fp.write(reportlib.SPACE)
fp.write(string.ljust('Symbol', 50))
fp.write(reportlib.SPACE)
fp.write(string.ljust('References', 25))
fp.write(reportlib.CRT)

fp.write(string.ljust('------------------------', 30))
fp.write(reportlib.SPACE)
fp.write(string.ljust('-------------------', 50))
fp.write(reportlib.SPACE)
fp.write(string.ljust('-------------------', 25))
fp.write(reportlib.CRT)

# select all QTLs created since March 2002
# and not MP annotations
db.sql('select m._Marker_key, m.symbol, m.mgiID ' + \
	  'into #markers ' + \
	  'from MRK_Mouse_View m ' + \
	  'where m._Marker_Status_key in (1,3) ' + \
	  'and m._Marker_Type_key = 6 ' + \
	  'and m.creation_date >= "03/01/2002" ' + \
	  'and not exists (select 1 from GXD_AlleleGenotype g, VOC_Annot a ' + \
	  'where m._Marker_key = g._Marker_key ' + \
	  'and g._Genotype_key = a._Object_key ' + \
	  'and a._AnnotType_key = 1002)', None)
db.sql('create index idx1 on #markers(_Marker_key)', None)

# select all references for the set of markers
results = db.sql('select m._Marker_key, b.accID ' + \
	'from #markers m, MRK_Reference r, ACC_Accession b ' + \
	'where m._Marker_key = r._Marker_key ' + \
	'and r._Refs_key = b._Object_key ' + \
	'and b._MGIType_key = 1 ' + \
	'and b._LogicalDB_key = 1 ' + \
	'and b.prefixPart = "J:" ' + \
	'and b.preferred = 1 ', 'auto')
refs = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not refs.has_key(key):
	refs[key] = []
    refs[key].append(value)

results = db.sql('select * from #markers order by symbol', 'auto')
for r in results:
    fp.write(string.ljust(r['mgiID'], 30))
    fp.write(reportlib.SPACE)
    fp.write(string.ljust(r['symbol'], 50))
    fp.write(reportlib.SPACE)
    fp.write(string.ljust(string.join(refs[r['_Marker_key']], ','), 25))
    fp.write(reportlib.CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.trailer(fp)
reportlib.finish_nonps(fp)

