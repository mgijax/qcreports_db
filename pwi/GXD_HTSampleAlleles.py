'''
#
# GXD HT Sample Alleles
#
# which alleles are used to annotate GXDHT_Samples?
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
    sys.stdout.write('Allele Symbol' + TAB)
    sys.stdout.write('JR strain association yes/no' + CRT)

    results = db.sql('''
        WITH alleles AS (
        select distinct a.accid, aa._allele_key, aa.symbol, 'yes' as hasJR
        from GXD_HTSample ht, GXD_Genotype g, GXD_AlleleGenotype ga, ALL_Allele aa, ACC_Accession a
        where ht._genotype_key = g._genotype_key
        and g._genotype_key = ga._genotype_key
        and ga._allele_key = aa._allele_key
        and aa.iswildtype = 0
        and aa._allele_key = a._object_key
        and a._mgitype_key = 11 
        and a._logicaldb_key = 1
        and exists (select 1 from ACC_Accession sa 
            where g._strain_key = sa._object_key
            and sa._mgitype_key = 10
            and sa._logicaldb_key = 22
            )
        )
        select * from alleles
        union
        select distinct a.accid, aa._allele_key, aa.symbol, 'no' as hasJR
        from GXD_HTSample ht, GXD_Genotype g, GXD_AlleleGenotype ga, ALL_Allele aa, ACC_Accession a
        where ht._genotype_key = g._genotype_key
        and g._genotype_key = ga._genotype_key
        and ga._allele_key = aa._allele_key
        and aa.iswildtype = 0
        and aa._allele_key = a._object_key
        and a._mgitype_key = 11 
        and a._logicaldb_key = 1
        and not exists (select 1 from ACC_Accession sa 
            where g._strain_key = sa._object_key
            and sa._mgitype_key = 10
            and sa._logicaldb_key = 22
            )
        and not exists (select 1 from alleles where aa._allele_key = alleles._allele_key)
        order by symbol
    ''', 'auto')

    for r in results:
        sys.stdout.write(r['accid'] + TAB)
        sys.stdout.write(r['symbol'] + TAB)
        sys.stdout.write(r['hasJR'] + CRT)

    sys.stdout.flush()
