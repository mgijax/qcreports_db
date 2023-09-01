'''
#
# Report:
#
# Full-coded data only from adult specimens
#
#       List all markers where the only full-coded data for the marker is adult or postnatal
#
#       MGI ID of marker gene symbol
#
#       postnatal
#       postnatal day
#       postnatal week
#       postnatal month
#       postnatal year
#       postnatal adult
#       postnatal newborn
#
# History:
#
# lec	09/01/2023
#	wts2-1268/2 new GXD QC reports for fullcoding priority
#
'''

import sys
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'Full-coded data only from adult specimens', outputdir = os.environ['QCOUTPUTDIR'])

fp.write('''
        List all markers where the only full-coded data for the marker is adult or postnatal
''')

fp.write(str.ljust('acc id', 25))
fp.write(SPACE)
fp.write(str.ljust('symbol', 35))
fp.write(CRT*2)

results = db.sql('''
        select distinct g._Marker_key, m.symbol, a.accID
        from GXD_Expression g, MRK_Marker m, ACC_Accession a
        where g._assaytype_key not in (10,11)
        and g.age like 'postnatal%'
        and g._Marker_key = m._Marker_key
        and g._Marker_key = a._Object_key
        and a._MGIType_key = 2
        and a._LogicalDB_key = 1
        and a.preferred = 1
        and not exists (select gg._Marker_key from GXD_Expression gg
                where g._marker_key = gg._marker_key
                and gg._assaytype_key not in (10,11)
                and gg.age not like 'postnatal%'
                )
        order by m.symbol
        ''', 'auto')

for r in results:

    key = r['_Marker_key']

    fp.write(str.ljust(r['accID'], 25))
    fp.write(SPACE)
    fp.write(str.ljust(r['symbol'], 35))
    fp.write(CRT)
        
fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)

