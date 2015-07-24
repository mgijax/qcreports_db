#!/usr/local/bin/python

'''
#
# VOC_GOObsolete.py
#
# Report:
#       
# A report of all markers with GO Annotations to an obsoleted GO Term
#
# field 1: Gene Accession ID
# field 2: Gene Symbol
# field 3: GO ID
#
# Usage:
#       VOC_GOObsolete.py
#
# History:
#
# 05/18/2011	lec
#	- TR 10720; "clustered" index removed; duplicates may appear
#
# 11/07/2006	lec
#	- TR 8014
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

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None, sqlLogging = 1)
fp.write('MGI-ID' + TAB)
fp.write('Gene Symbol' + TAB)
fp.write('GO ID' + 2*CRT)

db.sql('''
	select a.accID as goID, ta._Object_key 
	into temporary table obsolete  
	from VOC_Term_ACC_View a, VOC_Term t, VOC_Annot ta 
	where t._Vocab_key = 4  
	and t.isObsolete = 1  
	and t._Term_key = ta._Term_key 
	and ta._AnnotType_key = 1000 
	and t._Term_key = a._Object_key 
	and a._MGIType_key = 13 
	and a.preferred = 1
	''', None)

db.sql('create index obsolete_idx_key on obsolete(_Object_key)', None)

results = db.sql('''
	select goID, ma.accID, m.symbol 
	from obsolete o, ACC_Accession ma, MRK_Marker m 
	where o._Object_key = ma._Object_key 
	and ma._MGIType_key = 2 
	and ma._LogicalDB_key = 1 
	and ma.prefixPart = 'MGI:' 
	and ma.preferred = 1 
	and ma._Object_key = m._Marker_key 
	''', 'auto')

for r in results:
    fp.write(r['accID'] + TAB)
    fp.write(r['symbol'] + TAB)
    fp.write(r['goID'] + CRT)

reportlib.finish_nonps(fp)

