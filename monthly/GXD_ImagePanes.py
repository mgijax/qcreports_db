#!/usr/local/bin/python

'''
#
# Report:
#       TR10909/characteristics of all images panes in GXD
#
#
#	J# (of stub)
#	Figure Label (of stub)
#	Pane Label 
#	MGI id (of stub)
#	Pix id (associated w/ stub)
#	X Dim (associated w/ stub)
#	Y Dim (associated w/ stub)
#
# History:
#
'''
 
import sys 
import os
import string
import db
import reportlib
import mgi_utils

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

db.useOneConnection(1)

fp = reportlib.init(sys.argv[0], 'Characteristics of All Image Panes in GXD', outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

#
# assay types
#

assayType = {}

cmd = '''
	select distinct i._Image_key, t.assayType
	from IMG_Image i, IMG_ImagePane p,
	     GXD_InSituResultImage r, GXD_InSituResult rr, GXD_Specimen s, 
	     GXD_Assay aa, GXD_AssayType t
	where i._MGIType_key = 8
	and i._ImageType_key = 1072158
	and i._Image_key = p._Image_key
	and p._ImagePane_key = r._ImagePane_key
	and r._Result_key = rr._Result_key
	and rr._Specimen_key = s._Specimen_key
	and s._Assay_key = aa._Assay_key
	and aa._AssayType_key = t._AssayType_key
      '''

results = db.sql(cmd, 'auto')

for r in results:
    key = r['_Image_key']
    value = r['assayType']

    if not assayType.has_key(key):
	assayType[key] = []
    assayType[key].append(value)

cmd = '''
	select distinct i._Image_key, t.assayType
	from IMG_Image i, IMG_ImagePane p, GXD_Assay aa, GXD_AssayType t
	where i._MGIType_key = 8
	and i._ImageType_key = 1072158
	and i._Image_key = p._Image_key
	and p._ImagePane_key = aa._ImagePane_key
	and aa._Assay_key = aa._Assay_key
	and aa._AssayType_key = t._AssayType_key
      '''

results = db.sql(cmd, 'auto')

for r in results:
    key = r['_Image_key']
    value = r['assayType']

    if not assayType.has_key(key):
	assayType[key] = []
    assayType[key].append(value)

#
# pix id
#

cmd = ''' select i._Image_key, a.accID as pixID
	from IMG_Image i, ACC_Accession a
	where i._MGIType_key = 8
	and i._ImageType_key = 1072158
	and i._Image_key = a._Object_key
	and a._MGIType_key = 9
	and a._LogicalDB_key = 19
	and a.preferred = 1
      '''

pixID = {}
results = db.sql(cmd, 'auto')
for r in results:
    key = r['_Image_key']
    value = r['pixID']

    if not pixID.has_key(key):
	pixID[key] = []
	    
    if value != None:
        pixID[key].append(value)

#
# main query
#

cmd = ''' select i._Image_key, i.xDim, i.yDim, i.figureLabel, 
		p.paneLabel,
                a1.accID, 
		a2.accID as refID
	from IMG_Image i, IMG_ImagePane p, ACC_Accession a1, ACC_Accession a2
	where i._MGIType_key = 8
	and i._ImageType_key = 1072158
	and i._Image_key = p._Image_key
	and i._Image_key = a1._Object_key
	and a1._MGIType_key = 9
	and a1._LogicalDB_key = 1
	and a1.preferred = 1
	and i._Refs_key = a2._Object_key
	and a2._MGIType_key = 1
	and a2._LogicalDB_key = 1
	and a2.prefixPart = 'J:'
	and a2.preferred = 1
	order by i._Image_key, p.paneLabel
      '''

results = db.sql(cmd, 'auto')

for r in results:

    key = r['_Image_key']

    #
    # skip if image has no pix id
    #
    if not pixID.has_key(key):
	continue

    fp.write(r['refID'] + TAB)
    fp.write(r['figureLabel'] + TAB)
    fp.write(mgi_utils.prvalue(r['paneLabel']) + TAB)
    fp.write(r['accID'] + TAB)
    fp.write(string.join(pixID[key], '|') + TAB)
    fp.write(str(r['xDim']) + TAB)
    fp.write(str(r['yDim']) + TAB)

    if assayType.has_key(key):
        fp.write(string.join(assayType[key], '|'))
    fp.write(CRT)

reportlib.finish_nonps(fp)	# non-postscript file
db.useOneConnection(0)

