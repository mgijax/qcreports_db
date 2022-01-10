
'''
#
# PRB_StrainJAX2.py 03/20/2006
#
# Report:
#	Public Strains with JRS or MMNC/MMRRC IDs whose Alleles are used in a Genotype
#	but there is nod corresponding strain/genotype association.
#       
#
# Usage:
#       PRB_StrainJAX2.py
#
# Used by:
#       Internal Report
#
# Notes:
#
# History:
#
# lec   10/22/2014
#       - TR11750/postres complient
#
# lec	07/22/2010
#	- TR10136/revised; select all MMRRC
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
import reportlib
import db

db.setTrace()

TAB = reportlib.TAB
CRT = reportlib.CRT

fromDate = "current_date - interval '7 days'"

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
        select distinct s._Strain_key, 
                        substring(s.strain,1,70) as strain, 
                        substring(a.accID,1,6) as accID, 
                        a.numericPart,
                        g._Genotype_key 
        into temporary table strains 
        from PRB_Strain s, ACC_Accession a, PRB_Strain_Marker sm, 
             GXD_Genotype g, GXD_AlleleGenotype ag 
        where s.private = 0 
        and s._Strain_key = a._Object_key 
        and a._MGIType_key = 10 
        and a._LogicalDB_key = 22 
        and s._Strain_key = sm._Strain_key 
        and sm._Allele_key = ag._Allele_key 
        and ag._Genotype_key = g._Genotype_key 
        and g.creation_date between %s and current_date
        ''' % (fromDate), None)

    printReport(jrsfp)

def printReport(fp):

    db.sql('create index idx1 on strains(_Strain_key)', None)
    db.sql('create index idx2 on strains(_Genotype_key)', None)

    genotypes = {}
    results = db.sql('''
            select distinct s._Strain_key, a.accID, a.numericPart
            from strains s, ACC_Accession a 
            where s._Genotype_key = a._Object_key 
            and a._MGIType_key = 12 
            and a._LogicalDB_key = 1 
            and a.prefixPart = 'MGI:' 
            and a.preferred = 1
            order by a.numericPart''', 'auto')
    for r in results:
        key = r['_Strain_key']
        value = r['accID']
        if key not in genotypes:
            genotypes[key] = []
        genotypes[key].append(value)

    results = db.sql('''
            (
            select distinct s._Strain_key, s.strain, s.accID, s.numericPart
            from strains s
            where not exists (select 1 from PRB_Strain_Genotype g where s._Strain_key = g._Strain_key and s._Genotype_key = g._Genotype_key)
            and exists (select 1 from VOC_Annot va where va._AnnotType_key = 1002 and s._Genotype_key = va._Object_key)
            union
            select distinct s._Strain_key, s.strain, s.accID, s.numericPart
            from strains s
            where not exists (select 1 from PRB_Strain_Genotype g where s._Strain_key = g._Strain_key and s._Genotype_key = g._Genotype_key)
            and exists (select 1 from VOC_Annot va where va._AnnotType_key = 1020 and s._Genotype_key = va._Object_key)
            )
            order by numericPart''', 'auto')
    for r in results:
        fp.write(r['accID'] + TAB)
        fp.write(r['strain'] + TAB)
        fp.write(','.join(genotypes[r['_Strain_key']]) + CRT)

    fp.write('\n(%d rows affected)\n' % (len(results)))
    reportlib.finish_nonps(fp)


#
# main
#

jrs()
