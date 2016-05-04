#!/usr/local/bin/python

'''
#
# Report:
#       TR12323 : Specimen Type (Hybridization) Conflict
#
# History:
#
# 05/03/2016	lec
#	- TR12323/TR11717
#
'''
 
import sys 
import os
import string
import reportlib
import db

db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

db.useOneConnection(1)

fp = reportlib.init(sys.argv[0], '', outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

fp.write('jnumID' + TAB)
fp.write('figureLabel' + TAB)
fp.write('paneLabel' + TAB)
fp.write('imageID' + TAB)
fp.write('assayID' + TAB)
fp.write('symbol' + TAB)
fp.write('specimenLabel' + TAB)
fp.write('hybridization' + 2*CRT)

cmd = '''
select distinct ip._ImagePane_key
into temporary table assays1
from IMG_Image i, IMG_ImagePane ip, GXD_InSituResultImage ia, 
	GXD_InSituResult r, GXD_Specimen s, GXD_Assay ga, BIB_Citation_Cache b
where i._ImageType_key = 1072158
and i._Image_key = ip._Image_key
and ip._ImagePane_key = ia._ImagePane_key
and ia._Result_key = r._Result_key
and r._Specimen_key = s._Specimen_key
and s._Assay_key = ga._Assay_key
and ga._AssayType_key in (1,6,9)
and ga._Refs_key = b._Refs_key
group by ip._ImagePane_key having count(distinct s.hybridization) > 1
'''

db.sql(cmd, None)

cmd = '''
select distinct aa.accID as jnumID, aa.numericPart as jnum,
        substring(i.figureLabel,1,20) as figureLabel, 
        substring(ip.paneLabel,1,20) as paneLabel, 
        a.accID as imageID, 
	aaaa.accID as assayID, 
	m.symbol,
	s.specimenLabel, 
	s.hybridization
into temporary table assays2
from assays1 x, IMG_ImagePane ip, IMG_Image i, ACC_Accession aa, ACC_Accession a,
	ACC_Accession aaaa, GXD_InSituResultImage ia, GXD_InSituResult r, GXD_Specimen s, 
	GXD_Assay ga,
	MRK_Marker m
where x._ImagePane_key = ip._ImagePane_key
and ip._Image_key = i._Image_key
and i._Refs_key = aa._Object_key
and aa._MGIType_key = 1
and aa._LogicalDB_key = 1
and aa.prefixPart = 'J:'
and i._Image_key = a._Object_key
and a._MGIType_key = 9
and a._LogicalDB_key = 1
and x._ImagePane_key = ia._ImagePane_key
and ia._Result_key = r._Result_key
and r._Specimen_key = s._Specimen_key
and s._Assay_key = ga._Assay_key
and ga._Marker_key = m._Marker_key
and ga._Assay_key = aaaa._Object_key
and aaaa._MGIType_key = 8
and aaaa._LogicalDB_key = 1
'''

db.sql(cmd, None)

results = db.sql('''
select x.jnumID, x.figureLabel, x.paneLabel, x.imageID, x.assayID, x.symbol,
	x.specimenLabel, 
	x.hybridization
from assays2 x
order by jnum, figureLabel, paneLabel, symbol
''', 'auto')

for r in results:
    fp.write(r['jnumID'] + TAB)
    fp.write(r['figureLabel'] + TAB)
    fp.write(str(r['paneLabel']) + TAB)
    fp.write(r['imageID'] + TAB)
    fp.write(r['assayID'] + TAB)
    fp.write(r['symbol'] + TAB)
    fp.write(str(r['specimenLabel']) + TAB)
    fp.write(r['hybridization'] + CRT)

reportlib.finish_nonps(fp)	# non-postscript file
db.useOneConnection(0)

