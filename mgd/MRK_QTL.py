#!/usr/local/bin/python

'''
#
# MRK_QTL.py 07/18/2003
#
# Report:
#       Tab-delimited file of MGI Mouse Markers
#	of type QTL that have been added since March 2002
#	and with no PhenoSlim associations
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

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCREPORTOUTPUTDIR'])

fp.write('QTL Markers added to MGI since March 2002 with no PhenoSlim annotations')
fp.write(reportlib.CRT*2)

fp.write(string.ljust('MGI ID', 30))
fp.write(reportlib.SPACE)
fp.write(string.ljust('Symbol', 25))
fp.write(reportlib.SPACE)
fp.write(string.ljust('References', 25))
fp.write(reportlib.CRT)

fp.write(string.ljust('------------------------', 30))
fp.write(reportlib.SPACE)
fp.write(string.ljust('-------------------', 25))
fp.write(reportlib.SPACE)
fp.write(string.ljust('-------------------', 25))
fp.write(reportlib.CRT)

cmds = []

# select all QTLs created since March 2002
# and not phenoslim annotations
cmds.append('select m._Marker_key, m.symbol, m.mgiID ' + \
	  'into #markers ' + \
	  'from MRK_Mouse_View m ' + \
	  'where m._Marker_Status_key = 1 ' + \
	  'and m._Marker_Type_key = 6 ' + \
	  'and m.creation_date >= "03/01/2002" ' + \
	  'and not exists (select 1 from GXD_AlleleGenotype g, VOC_Annot a ' + \
	  'where m._Marker_key = g._Marker_key ' + \
	  'and g._Genotype_key = a._Object_key ' + \
	  'and a._AnnotType_key = 1001)')

cmds.append('select m._Marker_key, b.accID ' + \
	'from #markers m, MRK_Reference r, BIB_Acc_View b ' + \
	'where m._Marker_key = r._Marker_key ' + \
	'and r._Refs_key = b._Object_key ' + \
	'and b._LogicalDB_key = 1 ' + \
	'and b.prefixPart = "J:" ' + \
	'and b.preferred = 1 ')

cmds.append('select * from #markers order by symbol')

results = db.sql(cmds, 'auto')

refs = {}
for r in results[-2]:
    key = r['_Marker_key']
    value = r['accID']
    if not refs.has_key(key):
	refs[key] = []
    refs[key].append(value)

rows = 0
for r in results[-1]:
    fp.write(string.ljust(r['mgiID'], 30))
    fp.write(reportlib.SPACE)
    fp.write(string.ljust(r['symbol'], 25))
    fp.write(reportlib.SPACE)
    fp.write(string.ljust(string.join(refs[r['_Marker_key']], ','), 25))
    fp.write(reportlib.CRT)
    rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))
reportlib.trailer(fp)
reportlib.finish_nonps(fp)

