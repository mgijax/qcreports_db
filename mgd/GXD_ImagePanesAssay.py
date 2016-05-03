#!/usr/local/bin/python

'''
#
# Report:
#       TR11717/Image panes annotationed to > 1 Assay
#
# History:
#
# 05/04/2016    lec 
#       - TR11717
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
fp.write('pixID' + TAB)
fp.write('assayID' + TAB)
fp.write('symbol' + TAB)
fp.write('atype' + TAB)
fp.write('specimenLabel' + TAB)
fp.write('hybridization' + TAB)
fp.write('_Specimen_key' + TAB)
fp.write('specimenNote' + TAB)
fp.write('label' + TAB)
fp.write('visualization/secondary' + 2*CRT)

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
and b.jnumID not in ('J:91257', 'J:93300', 'J:101679', 'J:122989', 'J:153498', 'J:162220', 'J:171409', 'J:228563')
group by ip._ImagePane_key having count(distinct s._Assay_key) > 1
'''

db.sql(cmd, None)

cmd = '''
select distinct aa.accID as jnumID, 
        substring(i.figureLabel,1,20) as figureLabel, 
        substring(ip.paneLabel,1,20) as paneLabel, 
        a.accID as imageID, 
	aaa.accID as pixID, 
	aaaa.accID as assayID, 
	m.symbol,
	ga._AssayType_key as atype,
	s.specimenLabel, s.hybridization, s._Specimen_key, s.specimenNote,
	ga._ProbePrep_key, 
	ga._AntibodyPrep_key
into temporary table assays2
from assays1 x, IMG_ImagePane ip, IMG_Image i, ACC_Accession aa, ACC_Accession a, ACC_Accession aaa,
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
and i._Image_key = aaa._Object_key
and aaa._MGIType_key = 9
and aaa._LogicalDB_key = 19
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
select x.jnumID, x.figureLabel, x.paneLabel, x.imageID, x.pixID, x.assayID, x.symbol, x.atype, 
	x.specimenLabel, x.hybridization, x._Specimen_key, x.specimenNote,
	l.label,
	v.visualization
from assays2 x,
	GXD_ProbePrep p,
	GXD_Label l,
	GXD_VisualizationMethod v
where x._ProbePrep_key = p._ProbePrep_key
and p._Label_key = l._Label_key
and p._Visualization_key = v._Visualization_key
order by imageID, figureLabel, paneLabel, symbol
''', 'auto')

for r in results:
    fp.write(r['jnumID'] + TAB)
    fp.write(r['figureLabel'] + TAB)
    fp.write(str(r['paneLabel']) + TAB)
    fp.write(r['imageID'] + TAB)
    fp.write(r['pixID'] + TAB)
    fp.write(r['assayID'] + TAB)
    fp.write(r['symbol'] + TAB)
    fp.write(str(r['atype']) + TAB)
    fp.write(r['specimenLabel'] + TAB)
    fp.write(r['hybridization'] + TAB)
    fp.write(str(r['_Specimen_key']) + TAB)
    fp.write(str(r['specimenNote']) + TAB)
    fp.write(r['label'] + TAB)
    fp.write(r['visualization'] + CRT)
	
results = db.sql('''
select x.jnumID, x.figureLabel, x.paneLabel, x.imageID, x.pixID, x.assayID, x.symbol, x.atype, 
	x.specimenLabel, x.hybridization, x._Specimen_key, x.specimenNote,
	l.label,
	s.secondary
from assays2 x,
	GXD_AntibodyPrep p,
	GXD_Label l,
	GXD_Secondary s
where x._AntibodyPrep_key = p._AntibodyPrep_key
and p._Label_key = l._Label_key
and p._Secondary_key = s._Secondary_key
order by imageID, figureLabel, paneLabel, symbol
''', 'auto')

for r in results:
    fp.write(r['jnumID'] + TAB)
    fp.write(r['figureLabel'] + TAB)
    fp.write(str(r['paneLabel']) + TAB)
    fp.write(r['imageID'] + TAB)
    fp.write(r['pixID'] + TAB)
    fp.write(r['assayID'] + TAB)
    fp.write(r['symbol'] + TAB)
    fp.write(str(r['atype']) + TAB)
    fp.write(r['specimenLabel'] + TAB)
    fp.write(r['hybridization'] + TAB)
    fp.write(str(r['_Specimen_key']) + TAB)
    fp.write(str(r['specimenNote']) + TAB)
    fp.write(r['label'] + TAB)
    fp.write(r['secondary'] + CRT)
	
results = db.sql('''
select x.jnumID, x.figureLabel, x.paneLabel, x.imageID, x.pixID, x.assayID, x.symbol, x.atype, 
	x.specimenLabel, x.hybridization, x._Specimen_key, x.specimenNote,
	null,
	null
from assays2 x
where x._ProbePrep_key is null
and x._AntibodyPrep_key is null
order by imageID, figureLabel, paneLabel, symbol
''', 'auto')

for r in results:
    fp.write(r['jnumID'] + TAB)
    fp.write(r['figureLabel'] + TAB)
    fp.write(str(r['paneLabel']) + TAB)
    fp.write(r['imageID'] + TAB)
    fp.write(r['pixID'] + TAB)
    fp.write(r['assayID'] + TAB)
    fp.write(r['symbol'] + TAB)
    fp.write(str(r['atype']) + TAB)
    fp.write(r['specimenLabel'] + TAB)
    fp.write(r['hybridization'] + TAB)
    fp.write(str(r['_Specimen_key']) + TAB)
    fp.write(str(r['specimenNote']) + TAB)
    fp.write(TAB + CRT)

reportlib.finish_nonps(fp)	# non-postscript file
db.useOneConnection(0)

