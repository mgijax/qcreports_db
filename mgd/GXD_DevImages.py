#!/usr/local/bin/python

'''
#
# GXD_DevImages.py
#
# Report:
#       Produce a report of all J numbers from the journal Development
#       that are included in the GXD database that do not have images
#       attached to them.
#
# Usage:
#       GXD_DevImages.py
#
# Notes:
#
# History:
#
# lec	03/05/2004
#	- converted to QC (TR 5636)
#
# dbm   12/4/2002
#       - created (TR 4296)
#
'''
 
import sys
import os
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

db.useOneConnection(1)
fp = reportlib.init(sys.argv[0], '"Development" Papers Requiring Images', outputdir = os.environ['QCREPORTOUTPUTDIR'])

cmds = []
cmds.append('select a._Refs_key ' + \
      'into #assays ' + \
      'from GXD_Assay a, BIB_Refs b, IMG_Image i, IMG_ImagePane p ' + \
      'where a._ImagePane_key = p._ImagePane_key and ' + \
            'p._Image_key = i._Image_key and ' + \
            'i.xDim is NULL and ' + \
            'a._Refs_key = b._Refs_key and ' + \
            'b.journal = "Development" and ' + \
            'a._AssayType_key not in (1, 5, 7) ' + \
      'union ' + \
      'select a._Refs_key ' + \
      'from GXD_Assay a, BIB_Refs b, GXD_Specimen g, GXD_ISResultImage_View r ' + \
      'where g._Assay_key = a._Assay_key and ' + \
            'g._Specimen_key = r._Specimen_key and ' + \
            'r.xDim is NULL and ' + \
            'a._Refs_key = b._Refs_key and ' + \
            'b.journal = "Development"')

cmds.append('create index idx1 on #assays(_Refs_key)')
db.sql(cmds, None)

results = db.sql('select a.accID from #assays y, ACC_Accession a ' + \
	'where y._Refs_key = a._Object_key ' + \
	'and a._MGIType_key = 1 ' + \
	'and a.prefixPart = "J:" ' + \
	'and a.preferred = 1 ' + \
	'order by a.accID', 'auto')

for r in results:
	fp.write(r['accID'] + CRT)

fp.write(CRT + 'Total J numbers: ' + str(len(results)) + CRT)

reportlib.finish_nonps(fp)
db.useOneConnection(0)
