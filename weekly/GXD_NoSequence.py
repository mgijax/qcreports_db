#!/usr/local/bin/python

'''
#
# GXD_NoSequence.py 02/10/2003
#
# Report:
#       TR 10401
#
# similar to MRK_NoSequence.py
#
# For the GXD report, though, I would like the report to look at all markers that 
# lack sequence but have GXD index records.  Then I can decide if there are 
# certain marker types that would like to have excluded from this report.
# 
# Fields:
#   Marker symbol
#   Marker type
#   GXD Refs
# 
# Sort by:
#   marker type, then marker symbol
# 
# Usage:
#       GXD_NoSequence.py
#
# History:
#
# lec   10/22/2014
#       - TR11750/postres complient
#
# lec	10/26/2010
#	- TR10401
#
'''
 
import sys 
import os
import string
import reportlib

try:
    if os.environ['DB_TYPE'] == 'postgres':
        import pg_db
        db = pg_db
        db.setTrace()
        db.setAutoTranslateBE()
    else:
        import db
except:
    import db


CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

title = 'Genes without Sequence with GXD Annotations'
fp = reportlib.init(sys.argv[0], title = title, outputdir = os.environ['QCOUTPUTDIR'])

fp.write('    includes "official", "interim""\n')
fp.write('    excludes "DNA Segment"\n\n')

fp.write(string.ljust('Gene Symbol', 30) + \
 	 string.ljust('Marekr Type', 30) + \
	 string.ljust('GXD Refs', 30) + \
 	 CRT)

fp.write(string.ljust('-----------', 30) + \
 	 string.ljust('-----------', 30) + \
	 string.ljust('--------', 30) + \
 	 CRT)

#
# select genes with no sequences that exist in GXD index
#
db.sql('''
       select m._Marker_key, m.symbol, t.name as markerType
       into #markers 
       from MRK_Marker m, MRK_Types t
       where m._Organism_key = 1 
       and m._Marker_Status_key in (1,3) 
       and m._Marker_Type_key not in (2)
       and m._Marker_Type_key = t._Marker_Type_key
       and not exists (select 1 from ACC_Accession a 
       where m._Marker_key = a._Object_key 
       and a._MGIType_key = 2 
       and a._LogicalDB_Key in (9, 13, 27, 41, 59, 60, 85)) 
       and exists (select 1 from GXD_Index i where m._Marker_key = i._Marker_key)
       ''', None)
db.sql('create index idx1 on #markers(_Marker_key)', None)

#
# select number of GXD index references for each marker
#
results = db.sql('''select m._Marker_key, count(i._Refs_key) as gxd
        from #markers m, GXD_Index i 
        where m._Marker_key = i._Marker_key 
        group by m._Marker_key
	''', 'auto')
gxd = {}
for r in results:
        key = r['_Marker_key']
        value = str(r['gxd'])
        gxd[key] = value

results = db.sql('select * from #markers order by markerType, symbol', 'auto')
for r in results:
	key = r['_Marker_key']
	fp.write(string.ljust(r['symbol'], 30))
	fp.write(string.ljust(r['markerType'], 30))
	fp.write(string.ljust(gxd[key], 30) + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)	# non-postscript file
