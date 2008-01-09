#!/usr/local/bin/python

'''
#
# TR 8710
#
# Report:
#       List non-gene markers with GXD annotations. This excludes marker types
#       "gene", "DNA Segments" and "microRNAs". There are two part to the
#       report: non-gene markers in the index and non-gene marker in the
#       expression cache. Both parts of the report show the following fields:
#
#       1) Marker symbol
#       2) Marker type
#
#       Sort by marker type and then by marker symbol.
#
#       Show each marker/type once and provide a row count for each part of
#       the report.
#
# Usage:
#       GXD_NonGeneMarkers.py
#
# Notes:
#
# History:
#
# 01/09/2007	dbm
#       - created
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

fp = reportlib.init(sys.argv[0], 'Non-gene markers with GXD annotations', os.environ['QCOUTPUTDIR'])

fp.write('DNA segments and microRNAs are excluded' + CRT*2)

cmds = []

#
# Find the distinct markers and marker types in the index.
#
cmds.append('select distinct m.symbol, mt.name ' + \
            'from GXD_Index gi, MRK_Marker m, MRK_Types mt ' + \
            'where gi._Marker_key = m._Marker_key and ' + \
                  'm._Marker_type_key = mt._Marker_Type_key and ' + \
                  'mt._Marker_Type_key not in (1,2,11) ' + \
            'order by mt.name, m.symbol')

#
# Find the distinct markers and marker types in the expression cache.
#
cmds.append('select distinct m.symbol, mt.name ' + \
            'from GXD_Expression ge, MRK_Marker m, MRK_Types mt ' + \
            'where ge._Marker_key = m._Marker_key and ' + \
                  'm._Marker_type_key = mt._Marker_Type_key and ' + \
                  'mt._Marker_Type_key not in (1,2,11) ' + \
            'order by mt.name, m.symbol')

results = db.sql(cmds,'auto')

fp.write(string.ljust('Symbol (in the index)', 40) + '  ' + \
         string.ljust('Marker Type', 35) + CRT)
fp.write('-'*40 + '  ' + '-'*35 + CRT)

for r in results[0]:
    fp.write(string.ljust(r['symbol'], 40) + '  ' + \
             string.ljust(r['name'], 35) + CRT)

fp.write(CRT + 'Row count: ' + str(len(results[0])) + CRT*3)

fp.write(string.ljust('Symbol (in the expression cache)', 40) + '  ' + \
         string.ljust('Marker Type', 35) + CRT)
fp.write('-'*40 + '  ' + '-'*35 + CRT)

for r in results[1]:
    fp.write(string.ljust(r['symbol'], 40) + '  ' + \
             string.ljust(r['name'], 35) + CRT)

fp.write(CRT + 'Row count: ' + str(len(results[1])) + CRT)

reportlib.finish_nonps(fp)

