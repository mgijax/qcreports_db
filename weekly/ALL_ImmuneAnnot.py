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

if len(sys.argv) > 1:
	currentDate = sys.argv[2]
else:
	currentDate = mgi_utils.date('%m/%d/%Y')

fp = reportlib.init(sys.argv[0], title = 'Alleles with Immune System Annotations', outputdir = os.environ["QCREPORTOUTPUTDIR"])
fp.write(' symbol' + reportlib.CRT)
fp.write(' ' + '-' * 25 + reportlib.CRT)

cmd = 'select distinct a.symbol ' + \
'from ALL_Allele a, ALL_Note_General_View n ' + \
'where a._Allele_key = n._Allele_key ' + \
'and n.note like "%immune system:%" ' + \
'and n.creation_date between dateadd(day, -7, "%s") ' % (currentDate) + \
'and dateadd(day, 1, "%s") ' % (currentDate) + \
'union ' + \
'select distinct a.symbol ' + \
'from ALL_Allele a, GXD_AlleleGenotype g, VOC_Annot_View v ' + \
'where a._Allele_key = g._Allele_key ' + \
'and g._Genotype_key = v._Object_key ' + \
'and v._AnnotType_key = 1001 ' + \
'and v.term like "%immune system:%" ' + \
'and v.creation_date between dateadd(day, -7, "%s") ' % (currentDate) + \
'and dateadd(day, 1, "%s") ' % (currentDate) + \
'union ' + \
'select distinct a.symbol ' + \
'from ALL_Allele a, GXD_AlleleGenotype g, VOC_Annot_View v ' + \
'where a._Allele_key = g._Allele_key ' + \
'and g._Genotype_key = v._Object_key ' + \
'and v._AnnotType_key = 1002 ' + \
'and v.term like "%immune system:%" ' + \
'and v.creation_date between dateadd(day, -7, "%s") ' % (currentDate) + \
'and dateadd(day, 1, "%s") ' % (currentDate) + \
'order by a.symbol'

results = db.sql(cmd, 'auto')

for r in results:

	fp.write(' ' + r['symbol'] + reportlib.CRT)

fp.write(reportlib.CRT + '(%d rows affected)' % (len(results)) + reportlib.CRT)

reportlib.trailer(fp)
reportlib.finish_nonps(fp)	# non-postscript file

