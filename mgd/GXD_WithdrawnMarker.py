
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
# lec	01/31/2019
#	- removed accession id piece/withdrawn markers don't have accession ids
#
# sc	08/24/2018
#	- TR12940; remove Alan Brain Atlas
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

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'Withdrawn Markers (name = withdrawn) annotated to index records and/or assays', outputdir = os.environ['QCOUTPUTDIR'])

fp.write(2*CRT)
fp.write(str.ljust('Symbol', 50))
fp.write(CRT)
fp.write(50*'-')
fp.write(CRT)

# NOTE:  withdrawn markers do not have marker accession ids

results = db.sql('''
    select distinct m.symbol
    from MRK_Marker m
    where m._Marker_Status_key = 2 
    and (exists (select 1 from GXD_Index gi where m._Marker_key = gi._Marker_key)
         or 
         exists (select 1 from GXD_Assay ga 
                 where m._Marker_key = ga._Marker_key 
                 and ga._AssayType_key in (1,2,3,4,5,6,8,9)))
    ''', 'auto')

for r in results:
    fp.write(str.ljust(r['symbol'], 50))
    fp.write(CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
