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
    sys.stdout.write('JR strain association yes/no' + TAB)
    sys.stdout.write('JR ids' + TAB)
    sys.stdout.write('Strains' + CRT)

    results = db.sql('''
        WITH alleles AS (
        select distinct a.accid, aa._allele_key, aa.symbol, 
            string_agg(distinct sa.accid, '|') as jaxids, 'yes' as hasJR,
            string_agg(distinct s.strain, '|') as strains
        from GXD_HTSample ht, GXD_Genotype g, GXD_AlleleGenotype ga, ALL_Allele aa, ACC_Accession a,  
            PRB_Strain s, ACC_Accession sa
        where ht._genotype_key = g._genotype_key
        and g._genotype_key = ga._genotype_key
        and ga._allele_key = aa._allele_key
        and aa.iswildtype = 0
        and aa._allele_key = a._object_key
        and a._mgitype_key = 11 
        and a._logicaldb_key = 1
        and g._strain_key = sa._object_key
        and sa._mgitype_key = 10
        and sa._logicaldb_key = 22
        group by 1,2,3
        )
        select * from alleles
        union
        select distinct a.accid, aa._allele_key, aa.symbol, null, 'no' as hasJR, null
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
        sys.stdout.write(r['hasJR'] + TAB)
        sys.stdout.write(r['jaxids'] + TAB)
        sys.stdout.write(r['strains'] + CRT)

    sys.stdout.flush()
