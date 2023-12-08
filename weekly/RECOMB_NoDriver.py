
'''
#
# TR12862
#
# Report:
#	
#       Alleles that have attribute = Recombinase, but no driver gene
#	1)  Allele status not deleted
#	2)  Has recombinase attribute
#	3)  Does not have driver gene
#
#       Alleles that have driver gene but no attribute = Recombniase
#	1)  Allele status not deleted
#	2)  Does not have recombinase attribute
#	3)  Does have driver gene
#
#	Columns:
#       JNum of recombinase allele
#	Allele MGI ID
#	Allele symbol
#
#	Sort: JNum newest to oldest, allele name alpha
#
# Usage:
#       ALL_RecombNoDriver.py
#
# Notes:
#
# History:
#
#	TR12862 sc - created
#
'''
 
import sys 
import os 
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Allele Recombinase Check', os.environ['QCOUTPUTDIR'])
fp.write('\t\texcludes allele status: deleted\n')
fp.write('\t\tsorted by JNum, newest to oldest, then by allele name\n\n')

fp.write('Alleles with Recombinase Attribute tag Without Driver Gene' + CRT)
fp.write(str.ljust('JNum', 15) + \
        str.ljust('Allele ID', 15) + \
        str.ljust('Allele Symbol', 50) + CRT*2)

results = db.sql('''
        select a2.accid as alleleID, a._Allele_key, a.symbol, a.name, ra._Refs_key, a1.accid as jnumID
        from ALL_Allele a, MGI_Reference_Assoc ra, MGI_RefAssocType at, ACC_Accession a1, ACC_Accession a2
        where a._Allele_Status_key != 847112 --deleted
        and a._Allele_key = ra._Object_key
        and ra._MGIType_key = 11
        and ra._refassocType_key = 1011 --general
        and ra._refassocType_key = at._refassocType_key
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

        -- recombinase attribute exists
        and exists (select 1 from VOC_Annot v 
                where a._Allele_key = v._object_key
                and v._AnnotType_key = 1014
                and v._term_key = 11025588)

        -- driver gene does not exist
        and not exists(select 1 from MGI_Relationship mr
                where a._Allele_key = mr._Object_key_1
                and mr._Category_key = 1006)

        order by ra._Refs_key DESC, a.name
        ''', 'auto')

for r in results:
    fp.write(str.ljust(r['jnumID'], 15) + \
             str.ljust(r['alleleID'], 15) + \
             str.ljust(r['symbol'], 50) + CRT)
fp.write(CRT + 'Number of Alleles: ' + str(len(results)) + CRT*2)

fp.write('Alleles with Driver Gene Without Recombinase Attribute tag' + CRT)
fp.write(str.ljust('JNum', 15) + \
        str.ljust('Allele ID', 15) + \
        str.ljust('Allele Symbol', 50) + CRT*2)

results = db.sql('''
        select a2.accid as alleleID, a._Allele_key, a.symbol, a.name, ra._Refs_key, a1.accid as jnumID
        from ALL_Allele a, MGI_Reference_Assoc ra, MGI_RefAssocType at, ACC_Accession a1, ACC_Accession a2
        where a._Allele_Status_key != 847112 --deleted
        and a._Allele_key = ra._Object_key
        and ra._MGIType_key = 11
        and ra._refassocType_key = 1011 --general
        and ra._refassocType_key = at._refassocType_key
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

        -- recombinase attribute does not exist
        and not exists (select 1 from VOC_Annot v where a._Allele_key = v._object_key
                and v._AnnotType_key = 1014
                and v._term_key = 11025588)

        -- driver gene exists
        and exists(select 1 from MGI_Relationship mr
                where a._Allele_key = mr._Object_key_1
                and mr._Category_key = 1006)

        order by ra._Refs_key DESC, a.name
        ''', 'auto')

for r in results:
    fp.write(str.ljust(r['jnumID'], 15) + \
             str.ljust(r['alleleID'], 15) + \
             str.ljust(r['symbol'], 50) + CRT)
fp.write(CRT + 'Number of Alleles: ' + str(len(results)) + CRT)

reportlib.finish_nonps(fp)
