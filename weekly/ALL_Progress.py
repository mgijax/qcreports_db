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
# lec   10/22/2014
#       - TR11750/postres complient
#
# lnh   03/19/2014
#       TR 11361
#       - Only include Alleles with status "autoload",and "approved" to "Allele Counts"
#       - rename category name "Genes annotated, excluding QTL" to "Markers annotated, excluding QTL" 
#       - Add a new category called "Genes annotated, excluding QTL" for genes only 
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
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

transgenicKeys = '847126'
targetedKeys = '847116'
trappedKeys = '847121'
qtlKeys = '847130'
spontKeys = '847115'
chemicalKeys = '847122'
otherKeys = '847124,847123,847131,847132,847125'
#Including to the counts only alleles that have a "autoload" or "approved" status
statusKeys='847114,3983021'

def alleleCounts():

    fp.write('Allele Counts (excluding wild types and private data)' + 2*CRT)
    fp.write(string.ljust('Allele category',  35))
    fp.write(string.rjust('Total',  15))
    fp.write(string.rjust('Previous Month Total',  25) + CRT)
    fp.write(string.ljust('---------------',  35))
    fp.write(string.rjust('-----',  15))
    fp.write(string.rjust('--------------------',  25) + CRT)

    db.sql('''
	select _Allele_key, _Allele_Type_key, _Marker_key 
	into temporary table alleles from ALL_Allele where isWildType = 0 
        and _Allele_Status_key in (%s)
	''' % (statusKeys), None)

    db.sql('''
	select _Allele_key, _Allele_Type_key, _Marker_key 
	into temporary table allelesmice from ALL_Allele where isWildType = 0 and _Transmission_key != 3982953
        and _Allele_Status_key in (%s)
	''' % (statusKeys), None)

    db.sql('''
	select _Allele_key, _Allele_Type_key into temporary table amonthly from ALL_Allele 
	where isWildType = 0 
        and _Allele_Status_key in (%s)
	and date_part('year', creation_date) = %d 
	and date_part('month', creation_date) = %d 
	''' % (""+statusKeys+"",year, month), None)

    db.sql('''
	select _Allele_key, _Allele_Type_key into temporary table amonthlymice from ALL_Allele 
	where isWildType = 0 
        and _Allele_Status_key in (%s)
	and _Transmission_key != 3982953 
	and date_part('year', creation_date) = %d 
	and date_part('month', creation_date) = %d 
	''' % (""+statusKeys+"",year, month), None)

    total = db.sql('select count(*) as c from alleles', 'auto')[0]['c']
    totalM = db.sql('select count(*) as c from amonthly', 'auto')[0]['c']

    totalMice = db.sql('select count(*) as c from allelesmice', 'auto')[0]['c']
    totalMiceM = db.sql('select count(*) as c from amonthlymice', 'auto')[0]['c']

    transgenic = db.sql('select count(*) as c from alleles where _Allele_Type_key in (%s)' % (transgenicKeys), 'auto')[0]['c']
    transgenicM = db.sql('select count(*) as c from amonthly where _Allele_Type_key in (%s)' % (transgenicKeys), 'auto')[0]['c']

    targeted = db.sql('select count(*) as c from alleles where _Allele_Type_key in (%s)' % (targetedKeys), 'auto')[0]['c']
    targetedM = db.sql('select count(*) as c from amonthly where _Allele_Type_key in (%s)' % (targetedKeys), 'auto')[0]['c']

    targetedMice = db.sql('select count(*) as c from allelesmice where _Allele_Type_key in (%s)' % (targetedKeys), 'auto')[0]['c']
    targetedMiceM = db.sql('select count(*) as c from amonthlymice where _Allele_Type_key in (%s)' % (targetedKeys), 'auto')[0]['c']

    trapped = db.sql('select count(*) as c from alleles where _Allele_Type_key in (%s)' % (trappedKeys), 'auto')[0]['c']
    trappedM = db.sql('select count(*) as c from amonthly where _Allele_Type_key in (%s)' % (trappedKeys), 'auto')[0]['c']

    trappedMice = db.sql('select count(*) as c from allelesmice where _Allele_Type_key in (%s)' % (trappedKeys), 'auto')[0]['c']
    trappedMiceM = db.sql('select count(*) as c from amonthlymice where _Allele_Type_key in (%s)' % (trappedKeys), 'auto')[0]['c']

    qtl = db.sql('select count(*) as c from alleles where _Allele_Type_key in (%s)' % (qtlKeys), 'auto')[0]['c']
    qtlM = db.sql('select count(*) as c from amonthly where _Allele_Type_key in (%s)' % (qtlKeys), 'auto')[0]['c']

    spont = db.sql('select count(*) as c from alleles where _Allele_Type_key in (%s)' % (spontKeys), 'auto')[0]['c']
    spontM = db.sql('select count(*) as c from amonthly where _Allele_Type_key in (%s)' % (spontKeys), 'auto')[0]['c']

    chemical = db.sql('select count(*) as c from alleles where _Allele_Type_key in (%s)' % (chemicalKeys), 'auto')[0]['c']
    chemicalM = db.sql('select count(*) as c from amonthly where _Allele_Type_key in (%s)' % (chemicalKeys), 'auto')[0]['c']

    other = db.sql('select count(*) as c from alleles where _Allele_Type_key in (%s)' % (otherKeys), 'auto')[0]['c']
    otherM = db.sql('select count(*) as c from amonthly where _Allele_Type_key in (%s)' % (otherKeys), 'auto')[0]['c']

    nonqtl = db.sql('select count(*) as c from alleles where _Allele_Type_key not in (%s)' % (qtlKeys), 'auto')[0]['c']
    nonqtlM = db.sql('select count(*) as c from amonthly where _Allele_Type_key not in (%s)' % (qtlKeys), 'auto')[0]['c']

    nonqtlMice = db.sql('select count(*) as c from allelesmice where _Allele_Type_key not in (%s)' % (qtlKeys), 'auto')[0]['c']
    nonqtlMiceM = db.sql('select count(*) as c from amonthlymice where _Allele_Type_key not in (%s)' % (qtlKeys), 'auto')[0]['c']

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

    db.sql('''
	select g._Genotype_key, a._Annot_key, a.creation_date into temporary table genotypes 
	from GXD_Genotype g, VOC_Annot a 
	where a._AnnotType_key = 1002 
	and g._Genotype_key = a._Object_key 
	''', None)
    db.sql('create index geneoytpes_idx1 on genotypes(_Genotype_key)', None)

    db.sql('''
	select _Genotype_key, _Annot_key into temporary table gmonthly 
	from genotypes 
	where date_part('year', creation_date) = %d 
	and date_part('month', creation_date) = %d 
	''' % (year, month), None)
    db.sql('create index gmonthly_idx1 on gmonthly(_Genotype_key)', None)

    db.sql('''
	select g._Genotype_key, g._Annot_key, g.creation_date, a._Allele_key, a._Marker_key 
	into temporary table noqtl 
	from genotypes g, GXD_AlleleGenotype a, MRK_Marker m 
	where g._Genotype_key = a._Genotype_key 
	and a._Marker_key = m._Marker_key 
	and m._Marker_Type_key != 6
	''', None)
    
    db.sql('''
        select g._Genotype_key, g._Annot_key, g.creation_date, a._Allele_key, a._Marker_key 
        into temporary table genenoqtl 
        from genotypes g, GXD_AlleleGenotype a, MRK_Marker m 
        where g._Genotype_key = a._Genotype_key 
        and a._Marker_key = m._Marker_key 
        and m._Marker_Type_key = 1
        ''', None)

    db.sql('''
	select _Genotype_key, _Annot_key, _Allele_key, _Marker_key 
	into temporary table noqtlmonthly 
	from noqtl 
	where date_part('year', creation_date) = %d 
	and date_part('month', creation_date) = %d 
	''' % (year, month), None)
    
    db.sql('''
        select _Genotype_key, _Annot_key, _Allele_key, _Marker_key 
        into temporary table genenoqtlmonthly 
        from genenoqtl 
        where date_part('year', creation_date) = %d 
        and date_part('month', creation_date) = %d 
        ''' % (year, month), None)

    db.sql('''
	select g._Genotype_key, g._Annot_key, g.creation_date, a._Allele_key, a._Marker_key
	into temporary table qtl 
	from genotypes g, GXD_AlleleGenotype a, MRK_Marker m 
	where g._Genotype_key = a._Genotype_key 
	and a._Marker_key = m._Marker_key 
	and m._Marker_Type_key = 6
	''', None)

    db.sql('''
	select _Genotype_key, _Annot_key, _Allele_key, _Marker_key 
	into temporary table qtlmonthly 
	from qtl 
	where date_part('year', creation_date) = %d 
	and date_part('month', creation_date) = %d 
	''' % (year, month), None)

    allGenotypes = db.sql('select count(distinct _Genotype_key) as c from genotypes', 'auto')[0]['c']
    allGenotypesM = db.sql('select count(distinct _Genotype_key) as c from gmonthly', 'auto')[0]['c']

    noQTL = db.sql('select count(distinct _Genotype_key) as c from noqtl', 'auto')[0]['c']
    noQTLM = db.sql('select count(distinct _Genotype_key) as c from noqtlmonthly', 'auto')[0]['c']

    annotations = db.sql('select count(distinct _Annot_key) as c from genotypes', 'auto')[0]['c']
    annotationsM = db.sql('select count(distinct _Annot_key) as c from gmonthly', 'auto')[0]['c']

    annotnoQTL = db.sql('select count(distinct _Annot_key) as c from noqtl', 'auto')[0]['c']
    annotnoQTLM = db.sql('select count(distinct _Annot_key) as c from noqtlmonthly', 'auto')[0]['c']

    allelenoQTL = db.sql('select count(distinct _Allele_key) as c from noqtl', 'auto')[0]['c']
    allelenoQTLM = db.sql('select count(distinct _Allele_key) as c from noqtlmonthly', 'auto')[0]['c']

    markernoQTL = db.sql('select count(distinct _Marker_key) as c from noqtl', 'auto')[0]['c']
    markernoQTLM = db.sql('select count(distinct _Marker_key) as c from noqtlmonthly', 'auto')[0]['c']
    
    genenoQTL = db.sql('select count(distinct _Marker_key) as c from genenoqtl', 'auto')[0]['c']
    genenoQTLM = db.sql('select count(distinct _Marker_key) as c from genenoqtlmonthly', 'auto')[0]['c']

    qtl = db.sql('select count(distinct _Marker_key) as c from qtl', 'auto')[0]['c']
    qtlM = db.sql('select count(distinct _Marker_key) as c from qtlmonthly', 'auto')[0]['c']

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

    fp.write(string.ljust('Markers Annotated, excluding QTL', 35))
    fp.write(string.rjust(str(markernoQTL), 15))
    fp.write(string.rjust(str(markernoQTLM), 25))
    fp.write(CRT)
    
    fp.write(string.ljust('Genes Annotated, including HMP', 35))
    fp.write(string.rjust(str(genenoQTL), 15))
    fp.write(string.rjust(str(genenoQTLM), 25))
    fp.write(CRT)

    fp.write(string.ljust('QTL Annotated', 35))
    fp.write(string.rjust(str(qtl), 15))
    fp.write(string.rjust(str(qtlM), 25))
    fp.write(CRT)

def genesalleles():

    fp.write(2*CRT + '#########################' + 2*CRT)
    fp.write('Number of Genes with Alleles (excluding wild type)' + 2*CRT)

    # markers of type gene only

    db.sql('''
	select distinct a._Marker_key, a._Allele_Type_key into temporary table genes 
	from alleles a, MRK_Marker m 
	where a._Marker_key = m._Marker_key and m._Marker_Type_key = 1
	''', None)

    db.sql('''
	select distinct a._Marker_key, a._Allele_Type_key into temporary table genesMice 
	from allelesmice a, MRK_Marker m 
	where a._Marker_key = m._Marker_key and m._Marker_Type_key = 1
	''', None)

    genes = db.sql('select count(distinct _Marker_key) as c from genes', 'auto')[0]['c'] 
    genesMice = db.sql('select count(distinct _Marker_key) as c from genesMice', 'auto')[0]['c']

    targeted = db.sql('''
	select count(distinct _Marker_key) as c from genes 
	where _Allele_Type_key in (%s)
	''' % (targetedKeys), 'auto')[0]['c']
    targetedMice = db.sql('''
	select count(distinct _Marker_key) as c from genesMice 
	where _Allele_Type_key in (%s)
	''' % (targetedKeys), 'auto')[0]['c']

    trapped = db.sql('''
	select count(distinct _Marker_key) as c from genes 
	where _Allele_Type_key in (%s)
	''' % (trappedKeys), 'auto')[0]['c']
    trappedMice = db.sql('''
	select count(distinct _Marker_key) as c from genesMice 
	where _Allele_Type_key in (%s)
	''' % (trappedKeys), 'auto')[0]['c']

    # markers that have both targeted and trapped alleles

    bothTargTrapped = db.sql('''
	select count(distinct g1._Marker_key) as c from genes g1, genes g2 
	where g1._Allele_Type_key in (%s) 
	and g1._Marker_key = g2._Marker_key 
	and g2._Allele_Type_key in (%s)
	''' % (targetedKeys, trappedKeys), 'auto')[0]['c']

    bothTargTrappedMice = db.sql('''
	select count(distinct g1._Marker_key) as c from genesMice g1, genesMice g2 
	where g1._Allele_Type_key in (%s) 
	and g1._Marker_key = g2._Marker_key 
	and g2._Allele_Type_key in (%s)
	''' % (targetedKeys, trappedKeys), 'auto')[0]['c']

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

    mp = db.sql('select count(_Term_key) as c from VOC_Term where _Vocab_key = 5 and isObsolete = 0', 'auto')[0]['c']
    omim = db.sql('select count(_Term_key) as c from VOC_Term where _Vocab_key = 44 and isObsolete = 0', 'auto')[0]['c']
    diseaseont = db.sql('select count(_Term_key) as c from VOC_Term where _Vocab_key = 125 and isObsolete = 0', 'auto')[0]['c']

    fp.write(string.ljust('MP terms (exclude obsolete):', 60))
    fp.write(string.rjust(str(mp), 10) + CRT)
    fp.write(string.ljust('OMIM terms (exclude obsolete):', 60))
    fp.write(string.rjust(str(omim), 10) + CRT)
    fp.write(string.ljust('Disease Ontology (DO) terms (exclude obsolete):', 60))
    fp.write(string.rjust(str(diseaseont), 10) + CRT)

def diseaseontology():

    fp.write(2*CRT + '#########################' + 2*CRT)
    fp.write('DO annotations' + 2*CRT)

    genotypes = db.sql('select count(distinct _Object_key) as c from VOC_Annot where _AnnotType_key = 1020', 'auto')[0]['c']
    diseaseont = db.sql('select count(distinct _Term_key) as c from VOC_Annot where _AnnotType_key = 1020', 'auto')[0]['c']

    fp.write(string.ljust('Genotypes associated with at least one DO term:', 60))
    fp.write(string.rjust(str(genotypes), 10) + CRT)
    fp.write(string.ljust('DO terms that have one or more genotypes associated:', 60))
    fp.write(string.rjust(str(diseaseont), 10) + CRT)

#
# Main
#

fp = reportlib.init(sys.argv[0], title = 'Weekly Allele Progress Report', outputdir = os.environ['QCOUTPUTDIR'],
        fileExt = '.'+ os.environ['DATE'] + '.rpt')

year = db.sql('select date_part(\'year\', current_date) as thisyear', 'auto')[0]['thisyear']
month = db.sql('select date_part(\'month\', current_date) as thismonth', 'auto')[0]['thismonth']

if month == 1:
    month = 12
    year = year - 1
else:
    month = month - 1

alleleCounts()
genotypeCounts()
genesalleles()
vocab()
diseaseontology()

reportlib.finish_nonps(fp)	# non-postscript file

