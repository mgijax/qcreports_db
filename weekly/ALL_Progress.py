#!/usr/local/bin/python

'''
#
# ALL_Progress.py
#
# Report:
#       Weekly Allele Progress Report
#
# Usage:
#       ALL_Progress.py
#
# Notes:
#	- all reports use mgireport directory for output file
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- use proper case for all table and column names e.g. 
#         use MRK_Marker not mrk_marker
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
#
# lec   07/14/2009
#	- in "Allele category"
#	- below "Targeted (all types)", add "in mice"
#	- below "Gene Trapped (all types)", add "in mice"
#	- below "Total", add "in mice"
#	- below "Total minus QTL", add "in mice"
#
#	- in "Number of Genes"
#	- below "Total Genes with Alleles", add "in mice"
#	- below "Genes with targeted alleles", add "in mice"
#	- below "Genes with gene trapped alleles", add "in mice"
#	- below "Genes with both targeted and gene trapped alleles", add "in mice"
#
# lec	11/14/2005
#	- created, originally a simple isql script
#	- TR 7284
#
'''
 
import sys 
import os
import string
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
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

transgenicKeys = '847128,847127,847126,847129'
targetedKeys = '847118,847117,847116,847120,847119'
trappedKeys = '847121'
qtlKeys = '847130'
spontKeys = '847115'
chemicalKeys = '847122'
otherKeys = '847124,847123,847131,847132,847125'

def alleleCounts():

    fp.write('Allele Counts (excluding wild types)' + 2*CRT)
    fp.write(string.ljust('Allele category',  35))
    fp.write(string.rjust('Total',  15))
    fp.write(string.rjust('Previous Month Total',  25) + CRT)
    fp.write(string.ljust('---------------',  35))
    fp.write(string.rjust('-----',  15))
    fp.write(string.rjust('--------------------',  25) + CRT)

    db.sql('select _Allele_key, _Allele_Type_key, _Marker_key ' + \
	'into #alleles from ALL_Allele where isWildType = 0 ', None)

    db.sql('select _Allele_key, _Allele_Type_key, _Marker_key ' + \
	'into #allelesmice from ALL_Allele where isWildType = 0 and _Transmission_key != 3982953', None)

    db.sql('select _Allele_key, _Allele_Type_key into #amonthly from ALL_Allele ' + \
	'where isWildType = 0 ' + \
	'and datepart(year, creation_date) = %d ' % (year) + \
	'and datepart(month, creation_date) = %d ' % (month), None)

    db.sql('select _Allele_key, _Allele_Type_key into #amonthlymice from ALL_Allele ' + \
	'where isWildType = 0 ' + \
	'and _Transmission_key != 3982953 ' + \
	'and datepart(year, creation_date) = %d ' % (year) + \
	'and datepart(month, creation_date) = %d ' % (month), None)

    total = db.sql('select count(*) from #alleles', 'auto')[0]['']
    totalM = db.sql('select count(*) from #amonthly', 'auto')[0]['']

    totalMice = db.sql('select count(*) from #allelesmice', 'auto')[0]['']
    totalMiceM = db.sql('select count(*) from #amonthlymice', 'auto')[0]['']

    transgenic = db.sql('select count(*) from #alleles where _Allele_Type_key in (%s)' % (transgenicKeys), 'auto')[0]['']
    transgenicM = db.sql('select count(*) from #amonthly where _Allele_Type_key in (%s)' % (transgenicKeys), 'auto')[0]['']

    targeted = db.sql('select count(*) from #alleles where _Allele_Type_key in (%s)' % (targetedKeys), 'auto')[0]['']
    targetedM = db.sql('select count(*) from #amonthly where _Allele_Type_key in (%s)' % (targetedKeys), 'auto')[0]['']

    targetedMice = db.sql('select count(*) from #allelesmice where _Allele_Type_key in (%s)' % (targetedKeys), 'auto')[0]['']
    targetedMiceM = db.sql('select count(*) from #amonthlymice where _Allele_Type_key in (%s)' % (targetedKeys), 'auto')[0]['']

    trapped = db.sql('select count(*) from #alleles where _Allele_Type_key in (%s)' % (trappedKeys), 'auto')[0]['']
    trappedM = db.sql('select count(*) from #amonthly where _Allele_Type_key in (%s)' % (trappedKeys), 'auto')[0]['']

    trappedMice = db.sql('select count(*) from #allelesmice where _Allele_Type_key in (%s)' % (trappedKeys), 'auto')[0]['']
    trappedMiceM = db.sql('select count(*) from #amonthlymice where _Allele_Type_key in (%s)' % (trappedKeys), 'auto')[0]['']

    qtl = db.sql('select count(*) from #alleles where _Allele_Type_key in (%s)' % (qtlKeys), 'auto')[0]['']
    qtlM = db.sql('select count(*) from #amonthly where _Allele_Type_key in (%s)' % (qtlKeys), 'auto')[0]['']

    spont = db.sql('select count(*) from #alleles where _Allele_Type_key in (%s)' % (spontKeys), 'auto')[0]['']
    spontM = db.sql('select count(*) from #amonthly where _Allele_Type_key in (%s)' % (spontKeys), 'auto')[0]['']

    chemical = db.sql('select count(*) from #alleles where _Allele_Type_key in (%s)' % (chemicalKeys), 'auto')[0]['']
    chemicalM = db.sql('select count(*) from #amonthly where _Allele_Type_key in (%s)' % (chemicalKeys), 'auto')[0]['']

    other = db.sql('select count(*) from #alleles where _Allele_Type_key in (%s)' % (otherKeys), 'auto')[0]['']
    otherM = db.sql('select count(*) from #amonthly where _Allele_Type_key in (%s)' % (otherKeys), 'auto')[0]['']

    nonqtl = db.sql('select count(*) from #alleles where _Allele_Type_key not in (%s)' % (qtlKeys), 'auto')[0]['']
    nonqtlM = db.sql('select count(*) from #amonthly where _Allele_Type_key not in (%s)' % (qtlKeys), 'auto')[0]['']

    nonqtlMice = db.sql('select count(*) from #allelesmice where _Allele_Type_key not in (%s)' % (qtlKeys), 'auto')[0]['']
    nonqtlMiceM = db.sql('select count(*) from #amonthlymice where _Allele_Type_key not in (%s)' % (qtlKeys), 'auto')[0]['']

    fp.write(string.ljust('Transgeneic (all types)', 35))
    fp.write(string.rjust(str(transgenic), 15))
    fp.write(string.rjust(str(transgenicM), 25))
    fp.write(CRT)

    fp.write(string.ljust('Targeted (all types)', 35))
    fp.write(string.rjust(str(targeted), 15))
    fp.write(string.rjust(str(targetedM), 25))
    fp.write(CRT)

    fp.write(string.ljust('Targeted (all types - in mice)', 35))
    fp.write(string.rjust(str(targetedMice), 15))
    fp.write(string.rjust(str(targetedMiceM), 25))
    fp.write(CRT)

    fp.write(string.ljust('Gene Trapped', 35))
    fp.write(string.rjust(str(trapped), 15))
    fp.write(string.rjust(str(trappedM), 25))
    fp.write(CRT)

    fp.write(string.ljust('Gene Trapped (in mice)', 35))
    fp.write(string.rjust(str(trappedMice), 15))
    fp.write(string.rjust(str(trappedMiceM), 25))
    fp.write(CRT)

    fp.write(string.ljust('QTL', 35))
    fp.write(string.rjust(str(qtl), 15))
    fp.write(string.rjust(str(qtlM), 25))
    fp.write(CRT)

    fp.write(string.ljust('Spontaneous', 35))
    fp.write(string.rjust(str(spont), 15))
    fp.write(string.rjust(str(spontM), 25))
    fp.write(CRT)

    fp.write(string.ljust('Chemical (ENU)', 35))
    fp.write(string.rjust(str(chemical), 15))
    fp.write(string.rjust(str(chemicalM), 25))
    fp.write(CRT)

    fp.write(string.ljust('All Other', 35))
    fp.write(string.rjust(str(other), 15))
    fp.write(string.rjust(str(otherM), 25))
    fp.write(CRT)

    fp.write(string.ljust('Total', 35))
    fp.write(string.rjust(str(total), 15))
    fp.write(string.rjust(str(totalM), 25))
    fp.write(CRT)

    fp.write(string.ljust('Total (in mice)', 35))
    fp.write(string.rjust(str(totalMice), 15))
    fp.write(string.rjust(str(totalMiceM), 25))
    fp.write(CRT)

    fp.write(string.ljust('Total minus QTL', 35))
    fp.write(string.rjust(str(nonqtl), 15))
    fp.write(string.rjust(str(nonqtlM), 25))
    fp.write(CRT)

    fp.write(string.ljust('Total minus QTL (in mice)', 35))
    fp.write(string.rjust(str(nonqtlMice), 15))
    fp.write(string.rjust(str(nonqtlMiceM), 25))
    fp.write(CRT)

def genotypeCounts():

    fp.write(2*CRT + '#########################' + 2*CRT)
    fp.write('Genotypes Associated with at least one MP Term' + 2*CRT)
    fp.write(string.ljust('Category',  35))
    fp.write(string.rjust('Total',  15))
    fp.write(string.rjust('Previous Month Total',  25) + CRT)
    fp.write(string.ljust('---------------',  35))
    fp.write(string.rjust('-----',  15))
    fp.write(string.rjust('--------------------',  25) + CRT)

    db.sql('select g._Genotype_key, a._Annot_key, a.creation_date into #genotypes ' + \
	'from GXD_Genotype g, VOC_Annot a ' + \
	'where a._AnnotType_key = 1002 ' + \
	'and g._Genotype_key = a._Object_key ', None)
    db.sql('create index geneoytpes_idx1 on #genotypes(_Genotype_key)', None)

    db.sql('select _Genotype_key, _Annot_key into #gmonthly ' + \
	'from #genotypes ' + \
	'where datepart(year, creation_date) = %d ' % (year) + \
	'and datepart(month, creation_date) = %d ' % (month), None)
    db.sql('create index gmonthly_idx1 on #gmonthly(_Genotype_key)', None)

    db.sql('select g._Genotype_key, g._Annot_key, g.creation_date, a._Allele_key, a._Marker_key ' + \
	'into #noqtl ' + \
	'from #genotypes g, GXD_AlleleGenotype a, MRK_Marker m ' + \
	'where g._Genotype_key = a._Genotype_key ' + \
	'and a._Marker_key = m._Marker_key ' + \
	'and m._Marker_Type_key != 6', None)

    db.sql('select _Genotype_key, _Annot_key, _Allele_key, _Marker_key ' + \
	'into #noqtlmonthly ' + \
	'from #noqtl ' + \
	'where datepart(year, creation_date) = %d ' % (year) + \
	'and datepart(month, creation_date) = %d ' % (month), None)

    db.sql('select g._Genotype_key, g._Annot_key, g.creation_date, a._Allele_key, a._Marker_key ' + \
	'into #qtl ' + \
	'from #genotypes g, GXD_AlleleGenotype a, MRK_Marker m ' + \
	'where g._Genotype_key = a._Genotype_key ' + \
	'and a._Marker_key = m._Marker_key ' + \
	'and m._Marker_Type_key = 6', None)

    db.sql('select _Genotype_key, _Annot_key, _Allele_key, _Marker_key ' + \
	'into #qtlmonthly ' + \
	'from #qtl ' + \
	'where datepart(year, creation_date) = %d ' % (year) + \
	'and datepart(month, creation_date) = %d ' % (month), None)

    allGenotypes = db.sql('select count(distinct _Genotype_key) from #genotypes', 'auto')[0]['']
    allGenotypesM = db.sql('select count(distinct _Genotype_key) from #gmonthly', 'auto')[0]['']

    noQTL = db.sql('select count(distinct _Genotype_key) from #noqtl', 'auto')[0]['']
    noQTLM = db.sql('select count(distinct _Genotype_key) from #noqtlmonthly', 'auto')[0]['']

    annotations = db.sql('select count(distinct _Annot_key) from #genotypes', 'auto')[0]['']
    annotationsM = db.sql('select count(distinct _Annot_key) from #gmonthly', 'auto')[0]['']

    annotnoQTL = db.sql('select count(distinct _Annot_key) from #noqtl', 'auto')[0]['']
    annotnoQTLM = db.sql('select count(distinct _Annot_key) from #noqtlmonthly', 'auto')[0]['']

    allelenoQTL = db.sql('select count(distinct _Allele_key) from #noqtl', 'auto')[0]['']
    allelenoQTLM = db.sql('select count(distinct _Allele_key) from #noqtlmonthly', 'auto')[0]['']

    genenoQTL = db.sql('select count(distinct _Marker_key) from #noqtl', 'auto')[0]['']
    genenoQTLM = db.sql('select count(distinct _Marker_key) from #noqtlmonthly', 'auto')[0]['']

    qtl = db.sql('select count(distinct _Marker_key) from #qtl', 'auto')[0]['']
    qtlM = db.sql('select count(distinct _Marker_key) from #qtlmonthly', 'auto')[0]['']

    fp.write(string.ljust('All Genotypes', 35))
    fp.write(string.rjust(str(allGenotypes), 15))
    fp.write(string.rjust(str(allGenotypesM), 25))
    fp.write(CRT)

    fp.write(string.ljust('Genotypes, excluding QTL', 35))
    fp.write(string.rjust(str(noQTL), 15))
    fp.write(string.rjust(str(noQTLM), 25))
    fp.write(CRT)

    fp.write(string.ljust('Annotations', 35))
    fp.write(string.rjust(str(annotations), 15))
    fp.write(string.rjust(str(annotationsM), 25))
    fp.write(CRT)

    fp.write(string.ljust('Annotations, excluding QTL', 35))
    fp.write(string.rjust(str(annotnoQTL), 15))
    fp.write(string.rjust(str(annotnoQTLM), 25))
    fp.write(CRT)

    fp.write(string.ljust('Alleles Annotated, excluding QTL', 35))
    fp.write(string.rjust(str(allelenoQTL), 15))
    fp.write(string.rjust(str(allelenoQTLM), 25))
    fp.write(CRT)

    fp.write(string.ljust('Genes Annotated, excluding QTL', 35))
    fp.write(string.rjust(str(genenoQTL), 15))
    fp.write(string.rjust(str(genenoQTLM), 25))
    fp.write(CRT)

    fp.write(string.ljust('QTL Annotated', 35))
    fp.write(string.rjust(str(qtl), 15))
    fp.write(string.rjust(str(qtlM), 25))
    fp.write(CRT)

def allelesnomp():

    fp.write(2*CRT + '#########################' + 2*CRT)
    fp.write('Alleles with NO MP Terms, but with other annotations' + 2*CRT)

    db.sql('select n._Object_key into #other ' + \
	'from MGI_Note n, MGI_NoteChunk nc ' + \
	'where n._MGIType_key = 11 ' + \
	'and n._Note_key = nc._Note_key ' + \
	'and n._NoteType_key = 1020 ' + \
	'and nc.note like "%J:%" ', None)

    other = db.sql('select count(distinct _Object_key) from #other', 'auto')[0]['']

    fp.write(string.ljust('J# in the Notes:', 60))
    fp.write(string.rjust(str(other), 10) + CRT)

def genesalleles():

    fp.write(2*CRT + '#########################' + 2*CRT)
    fp.write('Number of Genes with Alleles (excluding wild type)' + 2*CRT)

    # markers of type gene only

    db.sql('select distinct a._Marker_key, a._Allele_Type_key into #genes ' + \
	'from #alleles a, MRK_Marker m ' + \
	'where a._Marker_key = m._Marker_key and m._Marker_Type_key = 1', None)

    db.sql('select distinct a._Marker_key, a._Allele_Type_key into #genesMice ' + \
	'from #allelesmice a, MRK_Marker m ' + \
	'where a._Marker_key = m._Marker_key and m._Marker_Type_key = 1', None)

    genes = db.sql('select count(distinct _Marker_key) from #genes', 'auto')[0][''] 
    genesMice = db.sql('select count(distinct _Marker_key) from #genesMice', 'auto')[0]['']

    targeted = db.sql('select count(distinct _Marker_key) from #genes ' + \
	'where _Allele_Type_key in (%s)' % (targetedKeys), 'auto')[0]['']
    targetedMice = db.sql('select count(distinct _Marker_key) from #genesMice ' + \
	'where _Allele_Type_key in (%s)' % (targetedKeys), 'auto')[0]['']

    trapped = db.sql('select count(distinct _Marker_key) from #genes ' + \
	'where _Allele_Type_key in (%s)' % (trappedKeys), 'auto')[0]['']
    trappedMice = db.sql('select count(distinct _Marker_key) from #genesMice ' + \
	'where _Allele_Type_key in (%s)' % (trappedKeys), 'auto')[0]['']

    # markers that have both targeted and trapped alleles

    bothTargTrapped = db.sql('select count(distinct g1._Marker_key) from #genes g1, #genes g2 ' + \
	'where g1._Allele_Type_key in (%s) ' % (targetedKeys) + \
	'and g1._Marker_key = g2._Marker_key ' + \
	'and g2._Allele_Type_key in (%s)' % (trappedKeys), 'auto')[0]['']

    bothTargTrappedMice = db.sql('select count(distinct g1._Marker_key) from #genesMice g1, #genesMice g2 ' + \
	'where g1._Allele_Type_key in (%s) ' % (targetedKeys) + \
	'and g1._Marker_key = g2._Marker_key ' + \
	'and g2._Allele_Type_key in (%s)' % (trappedKeys), 'auto')[0]['']

    fp.write(string.ljust('Total Genes with Alleles:', 60))
    fp.write(string.rjust(str(genes), 10) + CRT)
    fp.write(string.ljust('Total Genes with Alleles in mice:', 60))
    fp.write(string.rjust(str(genesMice), 10) + CRT)

    fp.write(string.ljust('Genes with targeted alleles (all types):', 60))
    fp.write(string.rjust(str(targeted), 10) + CRT)
    fp.write(string.ljust('Genes with targeted alleles (all types - in mice):', 60))
    fp.write(string.rjust(str(targetedMice), 10) + CRT)

    fp.write(string.ljust('Genes with gene trapped alleles:', 60))
    fp.write(string.rjust(str(trapped), 10) + CRT)
    fp.write(string.ljust('Genes with gene trapped alleles in mice:', 60))
    fp.write(string.rjust(str(trappedMice), 10) + CRT)

    fp.write(string.ljust('Genes with both targeted and gene trapped alleles:', 60))
    fp.write(string.rjust(str(bothTargTrapped), 10) + CRT)
    fp.write(string.ljust('Genes with both targeted and gene trapped alleles in mice:', 60))
    fp.write(string.rjust(str(bothTargTrappedMice), 10) + CRT)

def vocab():

    fp.write(2*CRT + '#########################' + 2*CRT)
    fp.write('Vocab count' + 2*CRT)

    mp = db.sql('select count(_Term_key) from VOC_Term where _Vocab_key = 5 and isObsolete = 0', 'auto')[0]['']
    omim = db.sql('select count(_Term_key) from VOC_Term where _Vocab_key = 44 and isObsolete = 0', 'auto')[0]['']

    fp.write(string.ljust('MP terms (exclude obsolete):', 60))
    fp.write(string.rjust(str(mp), 10) + CRT)
    fp.write(string.ljust('OMIM terms (exclude obsolete):', 60))
    fp.write(string.rjust(str(omim), 10) + CRT)

def omim():

    fp.write(2*CRT + '#########################' + 2*CRT)
    fp.write('OMIM annotations' + 2*CRT)

    genotypes = db.sql('select count(distinct _Object_key) from VOC_Annot where _AnnotType_key = 1005', 'auto')[0]['']
    omim = db.sql('select count(distinct _Term_key) from VOC_Annot where _AnnotType_key = 1005', 'auto')[0]['']

    fp.write(string.ljust('Genotypes associated with at least one OMIM term:', 60))
    fp.write(string.rjust(str(genotypes), 10) + CRT)
    fp.write(string.ljust('OMIM terms that have one or more genotypes associated:', 60))
    fp.write(string.rjust(str(omim), 10) + CRT)

#
# Main
#

fp = reportlib.init(sys.argv[0], title = 'Weekly Allele Progress Report', outputdir = os.environ['QCOUTPUTDIR'],
	fileExt = '.' + os.environ['DATE'] + '.rpt')

currentDate = mgi_utils.date('%m/%d/%Y')
fromDate = db.sql('select convert(char(10), dateadd(day, -7, "%s"), 101) ' % (currentDate), 'auto')[0]['']
toDate = db.sql('select convert(char(10), dateadd(day, 1, "%s"), 101) ' % (currentDate), 'auto')[0]['']

year = db.sql('select datepart(year, getdate())', 'auto')[0]['']
month = db.sql('select datepart(month, getdate())', 'auto')[0]['']

if month == 1:
    month = 12
    year = year - 1
else:
    month = month - 1

alleleCounts()
genotypeCounts()
allelesnomp()
genesalleles()
vocab()
omim()

reportlib.finish_nonps(fp)	# non-postscript file

