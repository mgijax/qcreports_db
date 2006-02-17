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
# lec	02/17/2006
#	- TR 7495/convert to tab-delimited
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

TAB = reportlib.TAB
CRT = reportlib.CRT

#
# Main
#

title = 'Public JAX strains with exact/inexact genotype matches\nwhere genotype MP annotations have been modified within the last 7 days'
fp = reportlib.init(sys.argv[0], title, outputdir = os.environ['QCOUTPUTDIR'], fileExt = '.' + os.environ['DATE'] + '.rpt')

fp.write('JR#' + TAB)
fp.write('Strain' + TAB)
fp.write('Genotypes w/ MP Annotations modified within the last 7 days' + CRT)

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
db.sql('select distinct g._Object_key ' + \
	'into #geno1 from VOC_Annot g, VOC_Evidence e ' + \
	'where g._AnnotType_key = 1002 ' + \
	'and g._Annot_key = e._Annot_key ' + \
	'and e.modification_date between dateadd(day, -7, "%s") and "%s" ' % (currentDate, currentDate), None)
db.sql('create index idx1 on #geno1(_Object_key)', None)

db.sql('select distinct s._Strain_key, ag._Genotype_key ' + \
	'into #genotypes ' + \
	'from #strains s, PRB_Strain_Marker sm, GXD_AlleleGenotype ag, #geno1 g ' + \
	'where s._Strain_key = sm._Strain_key ' + \
	'and sm._Allele_key = ag._Allele_key ' + \
	'and ag._Genotype_key = g._Object_key ', 'auto')
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
    fp.write(r['jrs'] + TAB)
    fp.write(r['strain'] + TAB)
    fp.write(string.join(genotypes[r['_Strain_key']], ',') + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.finish_nonps(fp)

