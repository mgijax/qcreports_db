#!/usr/local/bin/python

'''
#
# MRK_FeatureTypes.py
#
# Report:
#       TR 10429/marker feature types
#
# It is best to have the following columns that is similar to the load file for 
# Feature type update.
# 
#   1. MCV ID
#   2. Marker MGI ID
#   3. J: (J:#####)
#   4. Evidence Code Abbreviation (max length 5)
#   5. Inferred From 
#   6. Qualifier - may be blank
#   7. Editor user login
#   8. Date (MM/DD/YYYY) - may be blank, if so date of load is used.
#   9. Notes - may be blank (max length 255)
#  10. MCV term (For example, protein coding gene)
# 
# Usage:
#       MRK_FeatureTypes.py
#
# History:
#
# lec	10/26/2010
#	- TR 10429
#
'''
 
import sys 
import os
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

fp = reportlib.init(sys.argv[0], '', os.environ['QCOUTPUTDIR'], printHeading = None)

fp.write('MCVID\tMGI ID\tJNUM1\tEVIDENCE\tJNUM2\tBLANK\tNAME\tDATE\tBLANK\tMCV term\n')

results = db.sql('''
       select m._Marker_key, mgiID = a.accID, mcvID = va.accID, va.term,
	      ve.jnumID, ve.inferredFrom, ve.createdBy,
	      t1.abbreviation, 
	      cdate = convert(char(10), ve.creation_date, 101)
       from MRK_Marker m, ACC_Accession a, 
	    VOC_Annot_View va, VOC_Evidence_View ve, VOC_Term t1
       where m._Marker_Status_key in (1,3) 
       and m._Marker_key = a._Object_key 
       and a._MGIType_key = 2 
       and a._LogicalDB_key = 1 
       and a.prefixPart = "MGI:" 
       and a.preferred = 1 
       and m._Marker_key = va._Object_key 
       and va._AnnotType_key = 1011 
       and va._Annot_key = ve._Annot_key 
       and va._LogicalDB_key = 146
       and ve._EvidenceTerm_key = t1._Term_key
       order by mgiID
       ''', 'auto')

for r in results:
    fp.write(r['mcvID'] + TAB)
    fp.write(r['mgiID'] + TAB)
    fp.write(r['jnumID'] + TAB)
    fp.write(r['abbreviation'] + TAB)
    fp.write(mgi_utils.prvalue(r['inferredFrom']) + TAB)
    fp.write(TAB)
    fp.write(r['createdBy'] + TAB)
    fp.write(r['cdate'] + TAB)
    fp.write(r['term'] + CRT)

reportlib.finish_nonps(fp)	# non-postscript file

