'''
#
# GXD HT Sample JAX
#
# Report lists all alleles that are associated with genotypes used in the HT index
#
# Report name: GXD HT Index JAX
#
# Sort:
#       Allele Symbol
#
'''
 
import sys 
import os
import db
import reportlib

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

def go (form) :
    #
    # Main
    #

    # Write header
    sys.stdout.write('MGI id of allele'+ TAB)
    sys.stdout.write('Allele Symbol' + CRT)

    results = db.sql('''
        select a.accid, aa.symbol
        from ALL_Allele aa, ACC_Accession a
        where aa.iswildtype = 0
        and aa._allele_key = a._object_key
        and a._mgitype_key = 11 
        and a.preferred = 1
        and exists (select 1 from PRB_Strain s, ACC_Accession sa, GXD_Genotype g, GXD_AlleleGenotype ga, GXD_HTSample ht
            where s._strain_key = sa._object_key
            and sa._mgitype_key = 10
            and sa._logicaldb_key = 22
            and s._strain_key = g._strain_key
            and g._genotype_key = ga._genotype_key
            and ga._allele_key = aa._allele_key
            and g._genotype_key = ht._genotype_key
        )
        order by aa.symbol
    ''', 'auto')

    for r in results:
        sys.stdout.write(r['accid'] + TAB)
        sys.stdout.write(r['symbol'] + CRT)

    sys.stdout.flush()
