#!/usr/local/bin/python

'''
#
# TR12862
#
# Report:
#	
#       Recombinase alleles that have  no driver gene
#	1)  Allele status not deleted
#	2)  Has recombinase attribute
#	3)  Does not have driver gene
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
import string
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

fp = reportlib.init(sys.argv[0], 'Recombinase Allele Without Driver Gene Check', os.environ['QCOUTPUTDIR'])
fp.write('\t\texcludes allele status: deleted\n')
fp.write('\t\tsorted by JNum, newest to oldest, then by allele name\n\n')

fp.write(string.ljust('JNum', 15) + \
        string.ljust('Allele ID', 15) + \
        string.ljust('Allele Symbol', 50) + CRT)

db.sql('''
	select a2.accid as alleleID, a._Allele_key, a.symbol, a.name, 
	    ra._Refs_key, a1.accid as jnumID
	into temporary table recomb
	from VOC_Annot v, ALL_Allele a, MGI_Reference_Assoc ra, 
	    MGI_RefAssocType at, ACC_Accession a1, ACC_Accession a2
	where v._AnnotType_key = 1014 --recombinase attribute
	and v._Term_key = 11025588 
	and v._Object_key = a._Allele_key
	and a._Allele_Status_key != 847112 --deleted
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
	and a2.prefixPart = 'MGI:' ''', None)
db.sql('''create index idx1 on recomb(_Allele_key)''', None)

results = db.sql('''select alleleID, symbol, name, jnumID
	from recomb r
	where not exists(select 1
	from MGI_Relationship mr
	where mr._Category_key = 1006
	and mr._Object_key_1 = r._Allele_key)
	order by r._Refs_key DESC, r.name''', 'auto')

for r in results:
    fp.write(string.ljust(r['jnumID'], 15) + \
             string.ljust(r['alleleID'], 15) + \
             string.ljust(r['symbol'], 50) + CRT)
fp.write(CRT + 'Number of Alleles: ' + str(len(results)) + CRT)

reportlib.finish_nonps(fp)

