
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
# sc 01/28/2014
#	- TR11347 remove DO column
#
# lec	08/06/2012
#	- copied from GXD_FullCodeable.py
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

fp = reportlib.init(sys.argv[0], 'Indexed-Full-Coded gene list', outputdir = os.environ['QCOUTPUTDIR'])

fp.write(str.ljust('acc id', 25))
fp.write(SPACE)
fp.write(str.ljust('symbol', 35))
fp.write(SPACE)
fp.write(str.ljust('index records', 20))
fp.write(SPACE)
fp.write(str.ljust('full-coded', 20))
fp.write(SPACE)
fp.write(CRT)
fp.write(str.ljust('------', 25))
fp.write(SPACE)
fp.write(str.ljust('------', 35))
fp.write(SPACE)
fp.write(str.ljust('----', 8))
fp.write(SPACE)
fp.write(str.ljust('-------------', 20))
fp.write(SPACE)
fp.write(str.ljust('----------', 20))
fp.write(SPACE)
fp.write(CRT)

#
# count: all genes in the GXD index
#
db.sql('''
        select _Marker_key, count(*) as idx_count 
        into temporary table indexcount
        from GXD_Index
        group by _Marker_key
        ''', None)
db.sql('create index indexed_idx1 on indexcount(_Marker_key)', None)

#
# all genes in the GXD index
#

db.sql('''
        select distinct g._Marker_key, m.symbol, a.accID, g.idx_count
        into temporary table allgenes
        from indexcount g, MRK_Marker m, ACC_Accession a
        where g._Marker_key = m._Marker_key
        and g._Marker_key = a._Object_key
        and a._MGIType_key = 2
        and a._LogicalDB_key = 1
        and a.preferred = 1
        ''', None)

db.sql('create index allgenes_idx1 on allgenes(_Marker_key)', None)

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
    if key not in fullcodedrecords:
        fullcodedrecords[key] = []
    fullcodedrecords[key].append(value)

#
# to print...
#
results = db.sql('select * from allgenes order by idx_count, symbol', 'auto')

for r in results:

    key = r['_Marker_key']

    fp.write(str.ljust(r['accID'], 25))
    fp.write(SPACE)
    fp.write(str.ljust(r['symbol'], 35))
    fp.write(SPACE)

    fp.write(str.ljust(str(r['idx_count']), 20))
    fp.write(SPACE)

    if key in fullcodedrecords:
        fp.write(str.ljust(str(len(fullcodedrecords[key])), 20))
    else:
        fp.write(str.ljust('0', 20))
    fp.write(CRT)
        
fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)
