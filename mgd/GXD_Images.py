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
# lec	12/17/2004
#	- TR 6424; added journals beginning "PLoS%" and "BMC%"
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
import string
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

journals = ['Dev Biol', 'Development', 'Dev Dyn', 'Gene Expr Patterns', 'Mech Dev', 'PLoS Biol', 
'BMC Biochem', 'BMC Biol', 'BMC Biotechnol', 'BMC Cancer', 'BMC Cell Biol', 'BMC Complement Altern Med',
'BMC Dev Biol', 'BMC Evol Biol', 'BMC Genet', 'BMC Genomics', 'BMC Med', 'BMC Mol Biol', 'BMC Neurosci',
'BMC Ophthalmol']

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Papers Requiring Images', outputdir = os.environ['QCOUTPUTDIR'])
fp.write(TAB + 'Journals Checked:' + CRT)
for j in journals:
    fp.write(2*TAB + j + CRT)
fp.write(CRT)
fp.write(TAB + 'J#' + TAB + 'short_citation' + CRT)
fp.write(TAB + '--' + TAB + '--------------' + CRT)

db.sql('select distinct a._Refs_key ' + \
      'into #refs ' + \
      'from GXD_Assay a, BIB_Refs b, ACC_Accession ac, ' + \
           'IMG_Image i, IMG_ImagePane p ' + \
      'where a._ImagePane_key = p._ImagePane_key and ' + \
            'p._Image_key = i._Image_key and ' + \
            'i.xDim is NULL and ' + \
            'a._Refs_key = b._Refs_key and ' + \
	    'b.journal in ("' + string.join(journals, '","') + '") and ' + \
            'a._AssayType_key not in (1, 5) and ' + \
            'a._Assay_key = ac._Object_key and ' + \
            'ac._MGIType_key = 8 ' + \
      'union ' + \
      'select distinct a._Refs_key ' + \
      'from GXD_Assay a, BIB_Refs b, ACC_Accession ac, ' + \
           'GXD_Specimen g, GXD_ISResultImage_View r ' + \
      'where g._Assay_key = a._Assay_key and ' + \
            'g._Specimen_key = r._Specimen_key and ' + \
            'r.xDim is NULL and ' + \
            'a._Refs_key = b._Refs_key and ' + \
	    'b.journal in ("' + string.join(journals, '","') + '") and ' + \
            'a._Assay_key = ac._Object_key and ' + \
            'ac._MGIType_key = 8 ', None)

db.sql('create index idx1 on #refs(_Refs_key)', None)

results = db.sql('select b.jnumID, b.short_citation from #refs r, BIB_All_View b ' + \
	'where r._Refs_key = b._Refs_key ' + \
        'order by b.jnumID', 'auto')

for r in results:
	fp.write(TAB + r['jnumID'] + TAB + r['short_citation'] + CRT)

fp.write(CRT + 'Total J numbers: ' + str(len(results)) + CRT)

reportlib.trailer(fp)
reportlib.finish_nonps(fp)
