#!/usr/local/bin/python

'''
#
# GXD_Images.py
#
# Report:
#       Produce a report of all J numbers from the journal Development
#	or Dev Dyn that are included in the GXD database but do not have images
#       attached to them.
#
# Usage:
#       GXD_Images.py
#
# Notes:
#
# History:
#
# lec	09/16/2004
#	- TR 6205; added Dev Dyn
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

fp = reportlib.init(sys.argv[0], 'Papers Requiring Images (Development, Dev Dyn)', outputdir = os.environ['QCREPORTOUTPUTDIR'])

cmd = 'select b.jnumID ' + \
      'from GXD_Assay a, BIB_All_View b, ACC_Accession ac, ' + \
           'IMG_Image i, IMG_ImagePane p ' + \
      'where a._ImagePane_key = p._ImagePane_key and ' + \
            'p._Image_key = i._Image_key and ' + \
            'i.xDim is NULL and ' + \
            'a._Refs_key = b._Refs_key and ' + \
            'b.journal in ("Development", "Dev Dyn") and ' + \
            'a._AssayType_key not in (1, 5, 7) and ' + \
            'a._Assay_key = ac._Object_key and ' + \
            'ac._MGIType_key = 8 ' + \
      'union ' + \
      'select b.jnumID ' + \
      'from GXD_Assay a, BIB_All_View b, ACC_Accession ac, ' + \
           'GXD_Specimen g, GXD_ISResultImage_View r ' + \
      'where g._Assay_key = a._Assay_key and ' + \
            'g._Specimen_key = r._Specimen_key and ' + \
            'r.xDim is NULL and ' + \
            'a._Refs_key = b._Refs_key and ' + \
            'b.journal in ("Development", "Dev Dyn") and ' + \
            'a._Assay_key = ac._Object_key and ' + \
            'ac._MGIType_key = 8 ' + \
      'order by b.jnumID'

results = db.sql(cmd, 'auto')

for r in results:
	fp.write(r['jnumID'] + CRT)

fp.write(CRT + 'Total J numbers: ' + str(len(results)) + CRT)

reportlib.finish_nonps(fp)
