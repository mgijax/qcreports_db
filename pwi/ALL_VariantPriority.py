
'''
#
# Curation prioritization reporr
#
# A list of alleles where: 
#    the allele has phenotypes annotations (is a phenotypic allele)
#    the allele has variants
#    none of the variants has curated genomic data (version may be 'Not Specified' 
#
# Columns: 
#       Allele MGI ID 
#       Allele symbol
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
    # alleles with phenotype annotations MP annot Type 1002 
    db.sql('''
    select distinct ap._Allele_key_1 as _Allele_key 
    into temporary table mp 
    from GXD_AllelePair ap, GXD_Genotype g, VOC_Annot va 
    where ap._Genotype_key = g._Genotype_key 
    and g._Genotype_key = va._Object_key 
    and va._Annottype_key = 1002
    ''', None)

    db.sql('create index idx1 on mp(_Allele_key)', None)

    # above that have variants 
    db.sql('''
    select distinct av._Variant_key, mp._Allele_key 
    into temporary table variants 
    from mp, ALL_Variant av 
    where mp._Allele_key = av._Allele_key 
    and av._SourceVariant_key is not null
    ''', None)

    db.sql('create index idx2 on variants(_Variant_key)', None)

    # above that have no curated genomic data 
    results = db.sql('''
    select distinct aa.accID, a.symbol 
    from variants v, ALL_Variant_Sequence s, ALL_Allele a, ACC_Accession aa 
    where v._Variant_key = s._Variant_key 
    and s.startCoordinate is null 
    and s.endCoordinate is null 
    and s.referencesequence is null 
    and s.variantsequence is null 
    and (s.version is null or s.version = 'Not Specified') 
    and v._Allele_key = a._Allele_key 
    and v._Allele_key = aa._Object_key 
    and aa._MGIType_key = 11 
    and aa._LogicalDB_key = 1 
    and aa.preferred = 1 
    and aa.prefixPart = 'MGI:' ;
    ''', 'auto')

    sys.stdout.write('accID' + TAB)
    sys.stdout.write('symbol' + CRT)

    for r in results:
            sys.stdout.write(r['accID'] + TAB)
            sys.stdout.write(r['symbol'] + CRT)

    sys.stdout.flush()

