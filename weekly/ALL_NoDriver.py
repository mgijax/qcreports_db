'''
#
# Report:
#	
#       Alleles that have:
#	1)  Allele status not deleted
#	2)  Attribute in "inserted expressed sequence", "reporter" but not "recombinase"
#
#	Columns:
#       JNum of allele
#	Allele MGI ID
#	Allele symbol
#
#	Sort: JNum newest to oldest, allele name alpha
#
# Usage:
#       ALL_NoDriver.py
#
# Notes:
#
# History:
#
#	05/23/2023 lec
#	wts2-1187/fl2-362/Missing driver QC report
#
'''
 
import sys 
import os 
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Allele Missing Driver Relationship', os.environ['QCOUTPUTDIR'])
fp.write('\t\tattribute in "inserted expressed sequence", "reporter" but not "recombinase"\n')
fp.write('\t\texcludes allele status: deleted\n')
fp.write('\t\tsorted by JNum, newest to oldest, then by allele name\n\n')

fp.write(str.ljust('JNum', 15) + \
        str.ljust('Allele ID', 15) + \
        str.ljust('Allele Symbol', 60) + \
        str.ljust('Allele Status', 20) + \
        str.ljust('Allele Generation', 25) + \
        str.ljust('Attributes', 75) + CRT*2)

results = db.sql('''
        select a2.accid as alleleID, a._Allele_key, a.symbol, a.name, ra._Refs_key, a1.accid as jnumID, 
		t1.term as allelestatus, t2.term as alleletype,
		array_to_string(array_agg(distinct t3.term),',') as attributeTypes
        from ALL_Allele a, MGI_Reference_Assoc ra, ACC_Accession a1, ACC_Accession a2, VOC_Term t1, VOC_Term t2, VOC_Annot v, VOC_Term t3
        where a._Allele_Status_key != 847112 --deleted
        and a._Allele_key = ra._Object_key
        and ra._MGIType_key = 11
        and ra._refassocType_key = 1011 --general
        and ra._Refs_key = a1._Object_key
        and a1._MGIType_key = 1
        and a1._LogicalDB_key = 1
        and a1.preferred = 1
        and a1.prefixPart = 'J:'
        and a._Allele_key = a2._Object_key
        and a2._MGIType_key = 11
        and a2._LogicalDB_key = 1
        and a2.preferred = 1
        and a2.prefixPart = 'MGI:'
	and a._allele_status_key = t1._term_key
	and a._allele_type_key = t2._term_key
	and a._allele_key = v._object_key
        and v._annotType_key = 1014
	and v._term_key = t3._term_key

        -- attribute exists
        and exists (select 1 from VOC_Annot v 
                where a._Allele_key = v._object_key
                and v._AnnotType_key = 1014
                and v._term_key in (11025597,11025589))

        -- attribute does not exist
        and not exists (select 1 from VOC_Annot v 
                where a._Allele_key = v._object_key
                and v._AnnotType_key = 1014
                and v._term_key = 11025588)

        -- driver gene does not exist
        and not exists(select 1 from MGI_Relationship mr
                where a._Allele_key = mr._Object_key_1
                and mr._Category_key = 1006)

        group by alleleID, a._Allele_key, a.symbol, a.name, ra._Refs_key, jnumID, allelestatus, alleletype

        order by ra._Refs_key DESC, a.name
        ''', 'auto')

for r in results:
    fp.write(str.ljust(r['jnumID'], 15) + \
             str.ljust(r['alleleID'], 15) + \
             str.ljust(r['symbol'], 60) + \
             str.ljust(r['allelestatus'], 20) + \
             str.ljust(r['alleletype'], 25) + \
             str.ljust(r['attributeTypes'], 75) + CRT)

fp.write(CRT + 'Number of Alleles: ' + str(len(results)) + CRT*2)

reportlib.finish_nonps(fp)
