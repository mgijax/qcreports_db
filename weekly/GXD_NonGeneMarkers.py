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
# lec	07/13/2010
#	- TR 6839/remove marker type 11
#
# lec	05/01/2008
#	- TR 8775; on select GXD assay types
#
# 01/09/2007	dbm
#       - created
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

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Non-gene markers with GXD annotations', os.environ['QCOUTPUTDIR'])

fp.write('DNA segments are excluded' + CRT*2)

#
# Find the distinct markers and marker types in the index.
# exclude 'gene' and 'dna segments'
#

fp.write(string.ljust('Symbol (in the index)', 40) + '  ' + \
         string.ljust('Marker Type', 35) + CRT)
fp.write('-'*40 + '  ' + '-'*35 + CRT)

results = db.sql('''
	select distinct m.symbol, mt.name 
        from GXD_Index gi, MRK_Marker m, MRK_Types mt 
        where gi._Marker_key = m._Marker_key and 
               m._Marker_type_key = mt._Marker_Type_key and 
               mt._Marker_Type_key not in (1,2) 
        order by mt.name, m.symbol
	''', 'auto')

for r in results:
    fp.write(string.ljust(r['symbol'], 40) + '  ' + \
             string.ljust(r['name'], 35) + CRT)
fp.write('\n(%d rows affected)\n\n' % (len(results)))

#
# Find the distinct markers and marker types in the expression cache.
#

fp.write(string.ljust('Symbol (in the expression cache)', 40) + '  ' + \
         string.ljust('Marker Type', 35) + CRT)
fp.write('-'*40 + '  ' + '-'*35 + CRT)

results = db.sql('''
	select distinct m.symbol, mt.name 
        from GXD_Expression ge, MRK_Marker m, MRK_Types mt 
        where ge.isForGXD = 1 and 
	       ge._Marker_key = m._Marker_key and 
               m._Marker_type_key = mt._Marker_Type_key and 
               mt._Marker_Type_key not in (1,2) 
        order by mt.name, m.symbol
	''', 'auto')

for r in results:
    fp.write(string.ljust(r['symbol'], 40) + '  ' + \
             string.ljust(r['name'], 35) + CRT)
fp.write('\n(%d rows affected)\n\n' % (len(results)))

reportlib.finish_nonps(fp)

