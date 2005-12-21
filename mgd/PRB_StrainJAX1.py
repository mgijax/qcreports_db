#!/usr/local/bin/python

'''
#
# PRB_StrainJRS1.py 12/20/2005
#
# Report:
#       Public Strains that have a JRS ID and no genotype association
#
# Usage:
#       PRB_StrainJRS1.py
#
# Used by:
#       Internal Report
#
# Notes:
#
# History:
#
# lec	12/20/2005
#	- TR 7342
#
'''
 
import sys
import os
import string
import db
import mgi_utils
import reportlib

#
# Main
#

title = 'Public JAX strains with no exact/inexact genotype matches'
fp = reportlib.init(sys.argv[0], title, outputdir = os.environ['QCOUTPUTDIR'])

fp.write(string.ljust('JR#', 10))
fp.write(string.ljust('Strain', 75))
fp.write(string.ljust('Alleles', 50))
fp.write(reportlib.CRT)
fp.write(string.ljust('------', 10))
fp.write(string.ljust('--------------------------------------------------', 75))
fp.write(string.ljust('----------------------------------------', 50))
fp.write(reportlib.CRT)

# Retrieve all Strains that have a JRS ID and no genotype association

db.sql('select s._Strain_key, strain = substring(s.strain,1,70), jrs = substring(a.accID,1,6) ' + \
	'into #strains ' + \
	'from PRB_Strain s, ACC_Accession a ' + \
	'where s.private = 0 ' + \
	'and s._Strain_key = a._Object_key ' + \
	'and a._MGIType_key = 10 ' + \
	'and a._LogicalDB_key = 22 ' + \
	'and not exists (select 1 from PRB_Strain_Genotype g where s._Strain_key = g._Strain_key)', None)

db.sql('create index idx1 on #strains(_Strain_key)', None)

alleles = {}
results = db.sql('select s._Strain_key, a.symbol from #strains s, PRB_Strain_Marker sm, ALL_Allele a ' + \
	'where s._Strain_key = sm._Strain_key ' + \
	'and sm._Qualifier_key = 615427 ' + \
	'and sm._Allele_key = a._Allele_key ' + \
	'and a._Allele_Type_key != 847130', 'auto')
for r in results:
    key = r['_Strain_key']
    value = r['symbol']
    if not alleles.has_key(key):
	alleles[key] = []
    alleles[key].append(value)

results = db.sql('select * from #strains order by strain', 'auto')
for r in results:
    fp.write(string.ljust(r['jrs'], 10))
    fp.write(string.ljust(r['strain'], 75))

    if alleles.has_key(r['_Strain_key']):
        fp.write(string.join(alleles[r['_Strain_key']], ','))
    fp.write(reportlib.CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

