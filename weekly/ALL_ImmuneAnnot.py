#!/usr/local/bin/python

'''
#
# TR 4706 - Alleles with Immune System Annotations
#
# Usage:
#       ALL_ImmuneAnnot.py
#
# Notes:
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
#
# lec	04/14/2003
#	- created
#
'''
 
import sys 
import os
import db
import mgi_utils
import reportlib

#
# Main
#

if len(sys.argv) > 2:
	currentDate = sys.argv[2]
else:
	currentDate = mgi_utils.date('%m/%d/%Y')

fp = reportlib.init(sys.argv[0], title = 'Alleles of Genotype Annotations with Header Term: immune system', \
    outputdir = os.environ["QCOUTPUTDIR"], fileExt = '.' + os.environ['DATE'], isHTML = 1)
fp.write('symbol' + reportlib.CRT)
fp.write('' + '-' * 50 + reportlib.CRT)

db.sql('select distinct a.symbol, a._Allele_key ' + \
	'into #alleles ' + \
	'from ALL_Allele a, GXD_AlleleGenotype g, VOC_AnnotHeader v, VOC_Term t ' + \
	'where a._Allele_key = g._Allele_key ' + \
	'and g._Genotype_key = v._Object_key ' + \
	'and v._AnnotType_key = 1002 ' + \
	'and v._Term_key = t._Term_key ' + \
	'and t.term = "immune system phenotype" ' + \
	'and v.creation_date between dateadd(day, -7, "%s") ' % (currentDate) + \
	'and dateadd(day, 1, "%s") ' % (currentDate), None)

db.sql('create index idex1 on #alleles(_Allele_key)', None)

results = db.sql('select a.symbol, l.accID ' + \
	'from #alleles a, ACC_Accession l ' + \
	'where a._Allele_key = l._Object_key ' + \
	'and l._MGIType_key = 11 ' + \
	'and l._LogicalDB_key = 1 ' + \
	'and l.prefixPart = "MGI:" ' + \
	'and l.preferred = 1 ' + \
	'order by a.symbol', 'auto')

for r in results:
	fp.write(r['symbol'] + reportlib.CRT)

fp.write(reportlib.CRT + '(%d rows affected)' % (len(results)) + reportlib.CRT)

reportlib.trailer(fp)
reportlib.finish_nonps(fp)	# non-postscript file

