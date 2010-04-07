#!/usr/local/bin/python

'''
#
# PRB_StrainJRS3.py 03/20/2006
#
# Report:
#	Public Strains with JRS or MMNC/MMRRC IDs whose Alleles are used in a Genotype
#	but there is nod corresponding strain/genotype association.
#       
#
# Usage:
#       PRB_StrainJRS3.py
#
# Used by:
#       Internal Report
#
# Notes:
#
# History:
#
# lec	04/06/2010
#	- TR10136/added MMNC/MMRRC report
#
# lec	03/20/2006
#	- new qc report
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

currentDate = mgi_utils.date('%m/%d/%Y')

def jrs():

    title = 'Public JAX strains whose Alleles are used in a Genotype'
    title = title + ' but there is no corresponding Strain/Genotype association\n'
    title = title + '(where Genotypes have been created within the last week)'


    jrsfp = reportlib.init(sys.argv[0], title, \
			outputdir = os.environ['QCOUTPUTDIR'], fileExt = '.jrs.' + os.environ['DATE'] + '.rpt')

    jrsfp.write('JR#' + TAB)
    jrsfp.write('Strain' + TAB)
    jrsfp.write('Genotypes' + CRT*2)
    
    # Retrieve all Strains that have a JRS ID and whose Alleles are used in a Genotype

    db.sql('''
	select distinct s._Strain_key, strain = substring(s.strain,1,70), accID = substring(a.accID,1,6), g._Genotype_key 
	into #strains 
	from PRB_Strain s, ACC_Accession a, PRB_Strain_Marker sm, GXD_Genotype g, GXD_AlleleGenotype ag 
	where s.private = 0 
	and s._Strain_key = a._Object_key 
	and a._MGIType_key = 10 
	and a._LogicalDB_key = 22 
	and s._Strain_key = sm._Strain_key 
	and sm._Allele_key = ag._Allele_key 
	and ag._Genotype_key = g._Genotype_key 
	''', None)
	#and g.creation_date between dateadd(day, -7, "%s") and "%s" 
	#''' % (currentDate, currentDate), None)

    printReport(jrsfp)

def mmnc():

    title = 'Public MMNC strains whose Alleles are used in a Genotype'
    title = title + ' but there is no corresponding Strain/Genotype association\n'
    title = title + '(where Genotypes have been created within the last week)'


    fp = reportlib.init(sys.argv[0], title, \
			outputdir = os.environ['QCOUTPUTDIR'], fileExt = '.mmnc.' + os.environ['DATE'] + '.rpt')

    fp.write('MMRRC' + TAB)
    fp.write('Strain' + TAB)
    fp.write('Genotypes' + CRT*2)
    
    # Retrieve all Strains that have a MMRRC ID and whose Alleles are used in a Genotype

    db.sql('''
	select distinct s._Strain_key, strain = substring(s.strain,1,70), a.accID, g._Genotype_key 
	into #strains 
	from PRB_Strain s, ACC_Accession a, PRB_Strain_Marker sm, GXD_Genotype g, GXD_AlleleGenotype ag 
	where s.private = 0 
	and s.strain like '%/Mmnc'
	and s._Strain_key = a._Object_key 
	and a._MGIType_key = 10 
	and a._LogicalDB_key = 38 
	and s._Strain_key = sm._Strain_key 
	and sm._Allele_key = ag._Allele_key 
	and ag._Genotype_key = g._Genotype_key 
	''', None)
	#and g.creation_date between dateadd(day, -7, "%s") and "%s" 
	#''' % (currentDate, currentDate), None)

    printReport(fp)

def printReport(fp):

    db.sql('create index idx1 on #strains(_Strain_key)', None)
    db.sql('create index idx2 on #strains(_Genotype_key)', None)

    genotypes = {}
    results = db.sql('''
	    select distinct s._Strain_key, a.accID 
	    from #strains s, ACC_Accession a 
	    where s._Genotype_key = a._Object_key 
	    and a._MGIType_key = 12 
	    and a._LogicalDB_key = 1 
	    and a.prefixPart = "MGI:" 
	    and a.preferred = 1''', 'auto')
    for r in results:
        key = r['_Strain_key']
        value = r['accID']
        if not genotypes.has_key(key):
	    genotypes[key] = []
        genotypes[key].append(value)

    results = db.sql('''
	    select distinct s._Strain_key, s.strain, s.accID
	    from #strains s
	    where not exists 
	    (select 1 from PRB_Strain_Genotype g 
		 where s._Strain_key = g._Strain_key and s._Genotype_key = g._Genotype_key)
	    order by s.accID''', 'auto')
    for r in results:
        fp.write(r['accID'] + TAB)
        fp.write(r['strain'] + TAB)
        fp.write(string.join(genotypes[r['_Strain_key']], ',') + CRT)

    fp.write('\n(%d rows affected)\n' % (len(results)))
    reportlib.finish_nonps(fp)


#
# main
#

db.useOneConnection(1)
jrs()
mmnc()
db.useOneConnection(0)

