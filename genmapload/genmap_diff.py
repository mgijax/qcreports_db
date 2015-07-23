#!/usr/local/bin/python

'''
#
# TR 9316
#
# Report:
#
#	DiffEqual.rpt
#	DiffFromNonSynToNonSyn.rpt
#	DiffFromNonSynToSyn.rpt
#	DiffFromSynToNonSyn.rpt
#	DiffNotEqual.rpt
#
# Usage:
#       genmap_diff.py
#
# Notes:
#
# History:
#
# lec	07/08/2010
#       - new
#
'''

import sys
import os
import string
import mgi_utils
import reportlib
import db

#db.setTrace()
db.setAutoTranslateBE()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

#
# create output files
#

fp1 = reportlib.init('DiffEqual.rpt', \
	       'old map offset equal to new map offset', \
	       os.environ['RPTDIR'])

fp2 = reportlib.init('DiffFromNonSynToNonSyn.rpt', \
	       'old map offset not equal to new map offset from non-syntenic to non-syntenic', \
	       os.environ['RPTDIR'])

fp3 = reportlib.init('DiffFromNonSynToSyn.rpt', \
	       'old map offset not equal to new map offset from non-syntenic to syntenic', \
	       os.environ['RPTDIR'])

fp4 = reportlib.init('DiffFromSynToNonSyn.rpt', \
	       'old map offset not equal to new map offset from syntenic to non-syntenic', \
	       os.environ['RPTDIR'])

fp5 = reportlib.init('DiffNotEqual.rpt', \
	       'old map offset not equal to new map offset', \
	       os.environ['RPTDIR'])

for fp in (fp1, fp2, fp3, fp4, fp5):
    fp.write(CRT)
    fp.write(string.ljust('chromosome', 15))
    fp.write(string.ljust('symbol', 40))
    fp.write(string.ljust('accID', 35))
    fp.write(string.ljust('old offset', 30))
    fp.write(string.ljust('new offset', 30))
    fp.write(CRT)

    fp.write(string.ljust('----------', 15))
    fp.write(string.ljust('------', 40))
    fp.write(string.ljust('-----', 35))
    fp.write(string.ljust('----------', 30))
    fp.write(string.ljust('----------', 30))
    fp.write(CRT)

#
# select old map data and new map data
#

db.sql('''
    select m._Marker_key, m.symbol, m.chromosome, o.offset, a.accID
    into #oldMap
    from MRK_Marker m, MRK_Offset o, ACC_Accession a
    where m._Organism_key = 1
    and m._Marker_key = o._Marker_key 
    and o.source = 3
    and m._Marker_key = a._Object_key
    and a._MGIType_key = 2
    and a._LogicalDB_key = 1
    and a.prefixPart = 'MGI:'
    and a.preferred = 1
    order by m.chromosome, m.symbol
    ''', None)

db.sql('''
    select m._Marker_key, m.symbol, m.chromosome, o.offset, a.accID
    into #newMap
    from MRK_Marker m, MRK_Offset o, ACC_Accession a
    where m._Organism_key = 1
    and m._Marker_key = o._Marker_key 
    and o.source = 0
    and m._Marker_Status_key in (1,3)
    and m.chromosome != 'UN'
    and m._Marker_key = a._Object_key
    and a._MGIType_key = 2
    and a._LogicalDB_key = 1
    and a.prefixPart = 'MGI:'
    and a.preferred = 1
    order by m.chromosome, m.symbol
    ''', None)

db.sql('create index oldMap_idx1 on #oldMap(_Marker_key)', None)
db.sql('create index oldMap_idx2 on #oldMap(offset)', None)
db.sql('create index newMap_idx1 on #newMap(_Marker_key)', None)
db.sql('create index newMap_idx2 on #newMap(offset)', None)

#
# old map offset equal to new map offset
#

results = db.sql('''
     select o.chromosome, o.symbol, o.accID, 
	    o.offset as oldOffset, n.offset as newOffset
     from #oldMap o, #newMap n
     where o._Marker_key = n._Marker_key
     and o.offset = n.offset
     ''', 'auto')

for r in results:
    fp1.write(string.ljust(r['chromosome'], 15))
    fp1.write(string.ljust(r['symbol'], 40))
    fp1.write(string.ljust(r['accID'], 35))
    fp1.write(string.ljust(str(r['oldOffset']), 30))
    fp1.write(string.ljust(str(r['newOffset']), 30) + CRT)

fp1.write('\n(%d rows affected)\n' % len(results))

#
# old map offset not equal to new map offset from non-syntenic to non-syntenic
#

results = db.sql('''
     select o.chromosome, o.symbol, o.accID, 
	    o.offset as oldOffset, n.offset as newOffset
     from #oldMap o, #newMap n
     where o._Marker_key = n._Marker_key
     and o.offset != n.offset
     and o.offset != -1
     and n.offset != -1
     ''', 'auto')

for r in results:
    fp2.write(string.ljust(r['chromosome'], 15))
    fp2.write(string.ljust(r['symbol'], 40))
    fp2.write(string.ljust(r['accID'], 35))
    fp2.write(string.ljust(str(r['oldOffset']), 30))
    fp2.write(string.ljust(str(r['newOffset']), 30) + CRT)

fp2.write('\n(%d rows affected)\n' % len(results))

#
# old map offset not equal to new map offset from non-syntenic to syntenic
#

results = db.sql('''
     select o.chromosome, o.symbol, o.accID, 
	    o.offset as oldOffset, n.offset as newOffset
     from #oldMap o, #newMap n
     where o._Marker_key = n._Marker_key
     and o.offset != n.offset
     and n.offset = -1
     ''', 'auto')

for r in results:
    fp3.write(string.ljust(r['chromosome'], 15))
    fp3.write(string.ljust(r['symbol'], 40))
    fp3.write(string.ljust(r['accID'], 35))
    fp3.write(string.ljust(str(r['oldOffset']), 30))
    fp3.write(string.ljust(str(r['newOffset']), 30) + CRT)

fp3.write('\n(%d rows affected)\n' % len(results))

#
# old map offset not equal to new map offset from syntenic to non-syntenic
#

results = db.sql('''
     select o.chromosome, o.symbol, o.accID, 
	    o.offset as oldOffset, n.offset as newOffset
     from #oldMap o, #newMap n
     where o._Marker_key = n._Marker_key
     and o.offset != n.offset
     and o.offset = -1
     ''', 'auto')

for r in results:
    fp4.write(string.ljust(r['chromosome'], 15))
    fp4.write(string.ljust(r['symbol'], 40))
    fp4.write(string.ljust(r['accID'], 35))
    fp4.write(string.ljust(str(r['oldOffset']), 30))
    fp4.write(string.ljust(str(r['newOffset']), 30) + CRT)

fp4.write('\n(%d rows affected)\n' % len(results))

#
# old map offset not equal to new map offset
#

results = db.sql('''
     select o.chromosome, o.symbol, o.accID, 
	    o.offset as oldOffset, n.offset as newOffset
     from #oldMap o, #newMap n
     where o._Marker_key = n._Marker_key
     and o.offset != n.offset
     ''', 'auto')

for r in results:
    fp5.write(string.ljust(r['chromosome'], 15))
    fp5.write(string.ljust(r['symbol'], 40))
    fp5.write(string.ljust(r['accID'], 35))
    fp5.write(string.ljust(str(r['oldOffset']), 30))
    fp5.write(string.ljust(str(r['newOffset']), 30) + CRT)

fp5.write('\n(%d rows affected)\n' % len(results))

#
# close files
#

reportlib.finish_nonps(fp1)
reportlib.finish_nonps(fp2)
reportlib.finish_nonps(fp3)
reportlib.finish_nonps(fp4)
reportlib.finish_nonps(fp5)

