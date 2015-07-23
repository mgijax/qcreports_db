#!/usr/local/bin/python

'''
#
# TR 8212
#
# Report:
#
# Withdrawn markers associated with GXD index records or assays.  This was
# originally requested as a custom SQL (TR 8206).
#
# Usage:
#       GXD_WithdrawnMarker.py
#
# Notes:
#
# History:
#
# lec	09/23/2009
#	- TR 9846; add Allen Brain Atles (ldb = 107)
#
# lec	05/01/2008
#	- TR 8775; on select GXD assay types
#
# dbm	06/01/2007
#	- new
#
'''

import sys
import os
import string
import reportlib
import db

db.setTrace()
db.setAutoTranslateBE()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'Withdrawn Markers (name = withdrawn) annotated to index records and/or assays', outputdir = os.environ['QCOUTPUTDIR'])

fp.write(2*CRT)
fp.write(string.ljust('Symbol', 50))
fp.write(SPACE)
fp.write(string.ljust('Acc ID', 30))
fp.write(CRT)
fp.write(50*'-')
fp.write(SPACE)
fp.write(30*'-')
fp.write(CRT)

results = db.sql('''
    select distinct m.symbol, a.accID 
    from MRK_Marker_View m, ACC_Accession a 
    where m._Marker_Status_key = 2 
    and m._Marker_key = a._Object_key 
    and a._MGIType_key = 2 
    and a._LogicalDB_key = 1 
    and a.preferred = 1 
    and a.prefixPart = 'MGI:' 
    and (exists (select 1 from GXD_Index gi where m._Marker_key = gi._Marker_key)
         or 
         exists (select 1 from GXD_Assay ga 
                 where m._Marker_key = ga._Marker_key 
                 and ga._AssayType_key in (1,2,3,4,5,6,8,9)))
    ''', 'auto')

for r in results:
    fp.write(string.ljust(r['symbol'], 50))
    fp.write(SPACE)
    fp.write(string.ljust(r['accID'], 30))
    fp.write(SPACE)
    fp.write(CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))

#
# Allen Brain Atlas check
#

fp.write('\n\nWithdrawn Markers (name = withdrawn) that contain an Allen Brain Atlas ID\n')

fp.write(2*CRT)
fp.write(string.ljust('Symbol', 50))
fp.write(SPACE)
fp.write(string.ljust('Acc ID', 30))
fp.write(SPACE)
fp.write(string.ljust('ABA Acc ID', 30))
fp.write(CRT)
fp.write(50*'-')
fp.write(SPACE)
fp.write(30*'-')
fp.write(SPACE)
fp.write(30*'-')
fp.write(CRT)

results = db.sql('''
    select distinct m.symbol, a.accID, aa.accID as abaID
    from MRK_Marker_View m, ACC_Accession a , ACC_Accession aa
    where m._Marker_Status_key = 2 
    and m._Marker_key = a._Object_key 
    and a._MGIType_key = 2 
    and a._LogicalDB_key = 1 
    and a.preferred = 1 
    and a.prefixPart = 'MGI:' 
    and m._Marker_key = aa._Object_key 
    and aa._MGIType_key = 2 
    and aa._LogicalDB_key = 107
    ''', 'auto')

for r in results:
    fp.write(string.ljust(r['symbol'], 50))
    fp.write(SPACE)
    fp.write(string.ljust(r['accID'], 30))
    fp.write(SPACE)
    fp.write(string.ljust(r['abaID'], 30))
    fp.write(SPACE)
    fp.write(CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.finish_nonps(fp)
