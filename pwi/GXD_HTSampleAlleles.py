'''
#
# GXD HT Sample Alleles
#
# which alleles are used to annotate GXDHT_Samples?
# excludes wild type
#
# Report name: GXD HT Index all alleles
#
# Sort:
#       Allele Symbol
#
'''
 
import sys 
import os
import db
import reportlib

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

def go (form) :
    #
    # Main
    #

    # Write header
    sys.stdout.write('MGI id of allele' + TAB)
    sys.stdout.write('Allele Symbol' + CRT)

    results = db.sql('''
        select distinct a.accid, aa._allele_key, aa.symbol
        from GXD_HTSample ht, GXD_Genotype g, GXD_AlleleGenotype ga, ALL_Allele aa, ACC_Accession a
        where ht._genotype_key = g._genotype_key
        and g._genotype_key = ga._genotype_key
        and ga._allele_key = aa._allele_key
        and aa.iswildtype = 0
        and aa._allele_key = a._object_key
        and a._mgitype_key = 11 
        and a._logicaldb_key = 1
        order by symbol
    ''', 'auto')

    for r in results:
        sys.stdout.write(r['accid'] + TAB)
        sys.stdout.write(r['symbol'] + CRT)

    sys.stdout.flush()
