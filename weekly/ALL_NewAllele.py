#!/usr/local/bin/python

'''
#
# ALL_NewAllele.py
#
# Report:
#       Weekly New Alleles Report
#
# Usage:
#       ALL_NewAllele.py
#
# History:
#
# 10/4/2011	sc
# Alicia has asked for some modifications:
# 1. Add columns for Allele Type and Synonyms.
# 2. Create an archive for the report. 
#	(This may already exist but please add a link to the archive 
#	from the qcreport page.)
#
# 08/25/2011	lec
#	- TR10822
#
'''

import string 
import sys 
import os
import mgi_utils
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
TAB = reportlib.TAB

#
# Main
#

currentDate = mgi_utils.date('%m/%d/%Y')
fromDate = db.sql('select convert(char(10), dateadd(day, -7, "%s"), 101) ' % (currentDate), 'auto')[0]['']
toDate = db.sql('select convert(char(10), dateadd(day, -1, "%s"), 101) ' % (currentDate), 'auto')[0]['']
synonymDict = {}

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], fileExt = '.' + os.environ['DATE'] + '.rpt', printHeading = None)

results = db.sql('''select _Object_key as alleleKey, synonym
	from MGI_Synonym
	where _MGIType_key = 11''', 'auto')
for r in results:
    key = r['alleleKey']
    if not synonymDict.has_key(key):
	synonymDict[key] = []
    synonymDict[key].append(r['synonym'])

results = db.sql('''select a._Allele_key, a.symbol, 
	substring(a.name,1,60) as name, 
	substring(t1.term,1,15) as status, 
	substring(t2.term, 1, 60) as type,
	ac.accID
	from ALL_Allele a, VOC_Term t1, VOC_Term t2, MGI_Reference_Assoc r, ACC_Accession ac
	where a._Allele_Status_key = t1._Term_key
	and a._Allele_Type_key = t2._Term_key
	and a.creation_date between "%s" and "%s"
	and a._Allele_key = r._Object_key
	and r._MGIType_key = 11
	and r._RefAssocType_key = 1011
	and r._Refs_key = ac._Object_key 
	and ac._MGIType_key = 1
	and ac._LogicalDB_key = 1
	and ac.prefixPart = "J:"
	and ac.preferred = 1
	order by a.symbol
	''' % (fromDate, toDate), 'auto')

for r in results:
	alleleKey = r['_Allele_key']
	synonyms = ''
        if synonymDict.has_key(alleleKey):
	    synonyms = string.join(synonymDict[alleleKey])
	fp.write(r['symbol'] + TAB)
	fp.write(r['name'] + TAB)
	fp.write(synonyms + TAB)
	fp.write(r['type'] + TAB)
	fp.write(r['status'] + TAB)
	fp.write(r['accID'] + CRT)

reportlib.finish_nonps(fp)	# non-postscript file

