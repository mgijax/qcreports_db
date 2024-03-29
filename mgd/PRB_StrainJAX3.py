
'''
#
# Report:
#       Tab-delimited file
#
#	All Strains w/ Genotype Associations (via PRB_Strain_Genotype)
#	where the Markers/Alleles of the Strain record do not exactly match
#	the Markers/Alleles of the Genotype record.
#
# Usage:
#       PRB_StrainJAX3.py
#
# Used by:
#       Internal Report
#
# Notes:
#
# History:
#
# lec   10/24/2014
#       - TR11750/postres complient
#
# 07/22/2010	lec
#	- TR10136 revisited; retrieve all MMRRC not just Mmnc subset
#
# 04/06/2010	lec
#	- TR10136/add MMNC/MMRRC report
#
# 05/08/2006	lec
#	- TR 7614
#
'''
 
import sys
import os
import reportlib
import db

db.setTrace()

#
# Main
#

def jrs():

    jrsfp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], fileExt = '.jrs.rpt')

    title = 'JAX Strains w/ Genotype Associations where the Markers/Alleles of the Strain record\n' + \
            'do not exactly match the Markers/Alleles of the Genotype record.'

    jrsfp.write(title + '\n\n')
    jrsfp.write('JR#' + reportlib.TAB)
    jrsfp.write('Strain' + reportlib.TAB)
    jrsfp.write('Genotypes' + reportlib.TAB)
    jrsfp.write(reportlib.CRT)

    # JR Strains w/ Genotype Associations; exclude wild type alleles
    db.sql('''
            select distinct sa.accID, s.strain, g._Genotype_key, g._Strain_key, a._Marker_key, a._Allele_key
            into temporary table strains
            from PRB_Strain s, PRB_Strain_Genotype g, GXD_AlleleGenotype a, ALL_Allele aa, ACC_Accession sa 
            where s._Strain_key = g._Strain_key 
            and g._Genotype_key = a._Genotype_key 
            and a._Allele_key = aa._Allele_key 
            and aa.isWildType = 0 
            and s._Strain_key = sa._Object_key 
            and sa._MGIType_key = 10 
            and sa._LogicalDB_key = 22 
            and sa.preferred = 1 
            ''', None)
    db.sql('create index strains_idx1 on strains(_Strain_key)', None)

    printReport(jrsfp)

def printReport(fp):

    # Same Strains and the Marker/Allele associations
    db.sql('''
        select s._Strain_key, a._Marker_key, a._Allele_key 
        into temporary table strains2 
        from strains s, PRB_Strain_Marker a 
        where s._Strain_key = a._Strain_key
        ''', None)
    db.sql('create index strains2_idx1 on strains2(_Strain_key)', None)

    # Strains that do not have the same Allele
    
    db.sql('''
        select s.* into temporary table strainsToProcess from strains s 
        where not exists (select 1 from strains2 ss where s._Strain_key = ss._Strain_key 
        and s._Allele_key = ss._Allele_key)
        ''', None)

    # Retrieve MGI ids of the Genotypes

    mgiIDs = {}
    results = db.sql('''
        select s._Strain_key, a.accID 
        from strainsToProcess s, ACC_Accession a 
        where s._Genotype_key = a._Object_key 
        and a._MGIType_key = 12 
        and a._LogicalDB_key = 1 
        and a.preferred = 1
        ''', 'auto')
    for r in results:
        key = r['_Strain_key']
        value = r['accID']
        if key not in mgiIDs:
            mgiIDs[key] = []
        mgiIDs[key].append(value)

    # Process

    rows = 0
    results = db.sql('select distinct _Strain_key, accID, strain from strainsToProcess order by strain', 'auto')
    for r in results:
        key = r['_Strain_key']
        fp.write(r['accID'] + reportlib.TAB)
        fp.write(r['strain'] + reportlib.TAB)
        fp.write(','.join(mgiIDs[key]) + reportlib.CRT)

    fp.write('\n(%d rows affected)\n' % (len(results)))

    db.sql('drop table strains', None)
    db.sql('drop table strains2', None)
    db.sql('drop table strainsToProcess', None)

    reportlib.finish_nonps(fp)

#
# main
#

jrs()
