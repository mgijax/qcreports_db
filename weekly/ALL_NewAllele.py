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
# 08/25/2011	lec
#	- TR10822
#
'''
 
import sys 
import os
import db
import reportlib
import mgi_utils

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#

currentDate = mgi_utils.date('%m/%d/%Y')
fromDate = db.sql('select convert(char(10), dateadd(day, -7, "%s"), 101) ' % (currentDate), 'auto')[0]['']
toDate = db.sql('select convert(char(10), dateadd(day, -1, "%s"), 101) ' % (currentDate), 'auto')[0]['']

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], fileExt = '.' + os.environ['DATE'] + '.rpt', printHeading = None)

results = db.sql('''select a.symbol, 
	substring(a.name,1,60) as name, 
	substring(t.term,1,15) as status, 
	ac.accID
	from ALL_Allele a, VOC_Term t, MGI_Reference_Assoc r, ACC_Accession ac
	where a._Allele_Status_key = t._Term_key
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
	fp.write(r['symbol'] + TAB)
	fp.write(r['name'] + TAB)
	fp.write(r['status'] + TAB)
	fp.write(r['accID'] + CRT)

reportlib.finish_nonps(fp)	# non-postscript file

