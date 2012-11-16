#!/usr/local/bin/python

'''
#
# TR11107
#
# Report:
#
# Usage:
#       GXD_FullCodeableIndexed.py
#
# History:
#
# lec	08/06/2012
#	- copied from GXD_FullCodeable.py
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

fp = reportlib.init(sys.argv[0], 'Indexed-Full-Coded gene list', outputdir = os.environ['QCOUTPUTDIR'])

fp.write(string.ljust('acc id', 25))
fp.write(SPACE)
fp.write(string.ljust('symbol', 35))
fp.write(SPACE)
fp.write(string.ljust('OMIM', 8))
fp.write(SPACE)
fp.write(string.ljust('index records', 20))
fp.write(SPACE)
fp.write(string.ljust('full-coded', 20))
fp.write(SPACE)
fp.write(CRT)
fp.write(string.ljust('------', 25))
fp.write(SPACE)
fp.write(string.ljust('------', 35))
fp.write(SPACE)
fp.write(string.ljust('----', 8))
fp.write(SPACE)
fp.write(string.ljust('-------------', 20))
fp.write(SPACE)
fp.write(string.ljust('----------', 20))
fp.write(SPACE)
fp.write(CRT)

#
# count: all genes in the GXD index
#
db.sql('''
	select _Marker_key, count(*) as idx_count 
	into #indexcount
	from GXD_Index
	group by _Marker_key
	''', None)
db.sql('create index indexed_idx1 on #indexcount(_Marker_key)', None)

#
# all genes in the GXD index
#

db.sql('''
	select distinct g._Marker_key, m.symbol, a.accID, g.idx_count
	into #allgenes
	from #indexcount g, MRK_Marker m, ACC_Accession a
	where g._Marker_key = m._Marker_key
	and g._Marker_key = a._Object_key
	and a._MGIType_key = 2
	and a._LogicalDB_key = 1
	and a.preferred = 1
	''', None)

db.sql('create index allgenes_idx1 on #allgenes(_Marker_key)', None)

#
# count of total index records that have been full-coded
#

fullcodedrecords = {}
results = db.sql('''
	select distinct g._Marker_key, g._Refs_key 
	from GXD_Assay g
	where _AssayType_key not in (10,11)
	''', 'auto')
for r in results:
    key = r['_Marker_key']
    value = r['_Refs_key']
    if not fullcodedrecords.has_key(key):
        fullcodedrecords[key] = []
    fullcodedrecords[key].append(value)

#
#
# all markers with a human ortholog that has an OMIM annotation
#

omim = {}		# key = Marker key, value = 1
results = db.sql('''
	select distinct h1._Marker_key 
        from MRK_Homology_Cache h1
        where h1._Organism_key = 1 
	and exists (select 1 from MRK_Homology_Cache h2, 
             MRK_Marker m1, MRK_Marker m2, ACC_Accession a, 
             #allgenes g 
        where h1._Class_key = h2._Class_key 
        and h1._Marker_key = m1._Marker_key 
        and h2._Marker_key = m2._Marker_key 
        and m2._Marker_key = a._Object_key 
        and a._MGIType_key = 2 
        and a._LogicalDB_key = 15 
        and m1._Marker_key = g._Marker_key)
       ''', 'auto')

for r in results:
    omim[r['_Marker_key']] = 1

#
# to print...
#
results = db.sql('select * from #allgenes order by idx_count, symbol', 'auto')

for r in results:

    key = r['_Marker_key']

    fp.write(string.ljust(r['accID'], 25))
    fp.write(SPACE)
    fp.write(string.ljust(r['symbol'], 35))
    fp.write(SPACE)

    if omim.has_key(key):
        fp.write(string.ljust('Yes', 8))
    else:
        fp.write(string.ljust('No', 8))
    fp.write(SPACE)

    fp.write(string.ljust(str(r['idx_count']), 20))
    fp.write(SPACE)

    if fullcodedrecords.has_key(key):
        fp.write(string.ljust(str(len(fullcodedrecords[key])), 20))
    else:
        fp.write(string.ljust('0', 20))
    fp.write(CRT)
	
fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)
