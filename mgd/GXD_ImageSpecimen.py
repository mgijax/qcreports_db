#!/usr/local/bin/python

'''
#
# TR 11369
#
# Report:
#
# Image panes that are annotated to more than one specimen in the same assay.
# This was originally requested as a custom SQL (TR 10357).
#
# Usage:
#       GXD_ImageSpecimen.py
#
# Notes:
#
# History:
#
# lec   10/23/2014
#       - TR11750/postres complient
#
# lec   03/11/2014
#       - TR11597/sort by mgiID desc
#
# dbm	05/13/2013
#	- new
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

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

db.sql('''
    select distinct s._Assay_key,
                    s._Specimen_key,
                    iri._ImagePane_key,
                    ip._Image_key,
                    i._Refs_key,
                    i.figureLabel,
                    ip.paneLabel
    into #assays
    from GXD_InSituResultImage iri,
         GXD_InSituResult r,
         GXD_Specimen s,
         GXD_Assay a,
         IMG_Image i,
         IMG_ImagePane ip
    where iri._ImagePane_key = ip._ImagePane_key and
          ip._Image_key = i._Image_key and
          i.xDim is not null and
          iri._Result_key = r._Result_key and
          r._Specimen_key = s._Specimen_key and
          s._Assay_key = a._Assay_key and
          a._AssayType_key in (1,2,3,4,5,6,8,9) and
          a._Refs_key not in (92242)
	  ''', None)

db.sql('create index idx1_assay on #assays(_Assay_key)', None)

db.sql('''
    select *
    into #final
    from #assays a1
    where exists (select 1 from #assays a2
	where a2._assay_key = a1._assay_key and a2._imagepane_key = a1._imagepane_key
		and a2._specimen_key != a1._specimen_key
	) 
    ''', None)

db.sql('create index idx1_final on #final(_Image_key)', None)
db.sql('create index idx2_final on #final(_Assay_key)', None)
db.sql('create index idx3_final on #final(_Refs_key)', None)

results = db.sql('''
    select distinct assayID = a.accID,
           imageID = i.accID,
           jNumber = r.accID,
           figureLabel = f.figureLabel,
	   paneLabel = f.paneLabel
    from #final f,
         ACC_Accession i,
         ACC_Accession a,
         ACC_Accession r
    where f._Image_key = i._Object_key and
          i._MGIType_key = 9 and
          i._LogicalDB_key = 1 and
          i.prefixPart = "MGI:" and
          i.preferred = 1 and
          f._Assay_key = a._Object_key and
          a._MGIType_key = 8 and
          a._LogicalDB_key = 1 and
          a.prefixPart = "MGI:" and
          a.preferred = 1 and
          f._Refs_key = r._Object_key and
          r._MGIType_key = 1 and
          r._LogicalDB_key = 1 and
          r.prefixPart = "J:" and
          r.preferred = 1
    order by imageID desc
    ''', 'auto')

fp.write('(%d rows affected)' % (len(results)))
fp.write(2*CRT)

fp.write('Displayed Image Panes annotated to >1 specimen in the same assay.')
fp.write(CRT)
fp.write('Excludes J:91257 (Gray)')
fp.write(2*CRT)

fp.write(string.ljust('Assay ID',30))
fp.write(SPACE)
fp.write(string.ljust('Image ID',30))
fp.write(SPACE)
fp.write(string.ljust('J-Number',30))
fp.write(SPACE)
fp.write(string.ljust('Label',50))
fp.write(CRT)
fp.write(30*'-')
fp.write(SPACE)
fp.write(30*'-')
fp.write(SPACE)
fp.write(30*'-')
fp.write(SPACE)
fp.write(50*'-')
fp.write(CRT)

def xstr(s):
    """
    convert s to '' if it is NoneType
    """
    if s is None:
        return ''
    else:
        return str(s)

for r in results:
    fp.write(string.ljust(r['assayID'],30))
    fp.write(SPACE)
    fp.write(string.ljust(r['imageID'],30))
    fp.write(SPACE)
    fp.write(string.ljust(r['jNumber'],30))
    fp.write(SPACE)
    figureLabel = xstr(r['figureLabel'])
    paneLabel = xstr(r['paneLabel'])
    fp.write(string.ljust((figureLabel + paneLabel)[:50],50))
    fp.write(CRT)

reportlib.finish_nonps(fp)
