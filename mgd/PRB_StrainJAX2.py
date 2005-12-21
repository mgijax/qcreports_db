#!/usr/local/bin/python

'''
#
# PRB_StrainJRS2.py 12/20/2005
#
# Report:
#	Public Strains with JRS IDs that have a genotype association
#       
#
# Usage:
#       PRB_StrainJRS2.py
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

title = 'Public JAX strains with exact/inexact genotype matches\nwhere genotype MP annotations have been modified within the last 7 days'
fp = reportlib.init(sys.argv[0], title, outputdir = os.environ['QCOUTPUTDIR'])

fp.write(string.ljust('JR#', 10))
fp.write(string.ljust('Strain', 75))
fp.write(string.ljust('Genotypes w/ MP Annotations modified within the last 7 days', 50))
fp.write(reportlib.CRT)
fp.write(string.ljust('------', 10))
fp.write(string.ljust('--------------------------------------------------', 75))
fp.write(string.ljust('-----------------------------------------------------------', 50))
fp.write(reportlib.CRT)

# Retrieve all Strains that have a JRS ID and a genotype association

db.sql('select s._Strain_key, strain = substring(s.strain,1,70), jrs = substring(a.accID,1,6), g._Genotype_key ' + \
	'into #strains ' + \
	'from PRB_Strain s, ACC_Accession a, PRB_Strain_Genotype g ' + \
	'where s.private = 0 ' + \
	'and s._Strain_key = a._Object_key ' + \
	'and a._MGIType_key = 10 ' + \
	'and a._LogicalDB_key = 22 ' + \
	'and s._Strain_key = g._Strain_key', None)

db.sql('create index idx1 on #strains(_Strain_key)', None)
db.sql('create index idx2 on #strains(_Genotype_key)', None)

# Genotypes w/ MP annotations within the last 7 days

currentDate = mgi_utils.date('%m/%d/%Y')
db.sql('select distinct s._Strain_key, ag._Genotype_key ' + \
	'into #genotypes ' + \
	'from #strains s, PRB_Strain_Marker sm, GXD_AlleleGenotype ag, VOC_Annot g, VOC_Evidence e ' + \
	'where s._Strain_key = sm._Strain_key ' + \
	'and sm._Allele_key = ag._Allele_key ' + \
	'and ag._Genotype_key = g._Object_key ' + \
	'and g._AnnotType_key = 1002 ' + \
	'and g._Annot_key = e._Annot_key ' + \
	'and e.modification_date between dateadd(day, -7, "%s") and "%s" ' % (currentDate, currentDate), None)
db.sql('create index idx1 on #genotypes(_Strain_key)', None)
db.sql('create index idx2 on #genotypes(_Genotype_key)', None)

genotypes = {}
results = db.sql('select distinct g._Strain_key, a.accID ' + \
	'from #genotypes g, ACC_Accession a ' + \
	'where g._Genotype_key = a._Object_key ' + \
	'and a._MGIType_key = 12 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1', 'auto')
for r in results:
    key = r['_Strain_key']
    value = r['accID']
    if not genotypes.has_key(key):
	genotypes[key] = []
    genotypes[key].append(value)

results = db.sql('select s.* from #strains s ' + \
	'where exists (select 1 from #genotypes g where s._Strain_key = g._Strain_key) ' + \
	'order by strain', 'auto')
for r in results:
    fp.write(string.ljust(r['jrs'], 10))
    fp.write(string.ljust(r['strain'], 75))
    fp.write(string.join(genotypes[r['_Strain_key']], ',') + reportlib.CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

