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
# dbm	06/01/2007
#	- new
#
'''

import sys
import os
import string
import re
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'Markers annotated to index records and/or assays whose name=withdrawn', outputdir = os.environ['QCOUTPUTDIR'])

fp.write(2*CRT)
fp.write(string.ljust('Symbol', 50))
fp.write(SPACE)
fp.write(string.ljust('Acc ID', 30))
fp.write(CRT)
fp.write(50*'-')
fp.write(SPACE)
fp.write(30*'-')
fp.write(CRT)

results = db.sql('select distinct m.symbol, a.accID ' + \
                 'from MRK_Marker_View m, ACC_Accession a ' + \
                 'where m._Marker_Status_key = 2 and ' + \
                       'm._Marker_key = a._Object_key and ' + \
                       'a._MGIType_key = 2 and ' + \
                       'a._LogicalDB_key = 1 and ' + \
                       'a.preferred = 1 and ' + \
                       'a.prefixPart = "MGI:" and ' + \
                       '(exists (select 1 from GXD_Index gi ' + \
                                'where m._Marker_key = gi._Marker_key) or ' + \
                        'exists (select 1 from GXD_Assay ga ' + \
                                'where m._Marker_key = ga._Marker_key))', 'auto')

for r in results:
    fp.write(string.ljust(r['symbol'], 50))
    fp.write(SPACE)
    fp.write(string.ljust(r['accID'], 30))
    fp.write(SPACE)
    fp.write(CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)