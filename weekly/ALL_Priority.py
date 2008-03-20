#!/usr/local/bin/python

'''
#
# TR 8554
#
# Report:
#       Aleles that have 5 or more Priority References
#
#       Allele approval date
#	Allele MGI ID
#	Allele Type
#	Allele symbol
#       Number of References
#	J#'s (comma-separated, sorted by J#, highest first)
#
# Usage:
#       ALLPriority.py
#
# Notes:
#
# History:
#
# 10/30/2007	lec
#       - created
#
'''
 
import sys 
import os 
import string
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Alleles that have 5 or more Priority References', os.environ['QCOUTPUTDIR'])


fp.write(string.ljust('Approval', 15) + \
         string.ljust('Acc ID', 15) + \
         string.ljust('Allele Type', 45) + \
         string.ljust('Symbol', 35) + \
         string.ljust('References', 15) + CRT*2)

#
# select allele with >= 5 Priority references
#

db.sql('select r._Object_key, r._Refs_key, r._MGIType_key ' + \
    'into #refs1 ' + \
    'from MGI_Reference_Assoc r ' + \
    'where r._MGIType_key = 11 ' + \
    'and r._RefAssocType_key = 1021 ', None)
db.sql('create index idx1 on #refs1(_Object_key)', None)

db.sql('select * into #refs2 from #refs1 group by _Object_key having count(*) >= 5', None)
db.sql('create index idx1 on #refs2(_Object_key)', None)

db.sql('select _Object_key, numRefs = count(*) into #refs3 from #refs2 group by _Object_key', None)
db.sql('create index idx1 on #refs3(_Object_key)', None)

#
# select distince alleles that contain Prioriy references
#

db.sql('select distinct a._Allele_key, a.symbol, a.approval_date, alleleType = t.term, r.numRefs ' + \
    'into #alleles ' + \
    'from ALL_Allele a, VOC_Term t, #refs3 r ' + \
    'where a.approval_date is not NULL ' + \
    'and a._Allele_Type_key = t._Term_key ' + \
    'and a._Allele_key = r._Object_key ' + \
    'order by r.numRefs', None)
db.sql('create index idx1 on #alleles(_Allele_key)', None)

#
# select references J: for each allele
#

results = db.sql('select distinct a._Allele_key, a1.numericPart, a1.accID ' + \
    'from #alleles a, #refs2 r, ACC_Accession a1 ' + \
    'where a._Allele_key = r._Object_key ' + \
    'and r._MGIType_key = 11 ' + \
    'and r._Refs_key = a1._Object_key ' + \
    'and a1._MGIType_key = 1 ' + \
    'and a1._LogicalDB_key = 1 ' + \
    'and a1.prefixPart = "J:" ' + \
    'and a1.preferred = 1 ' + 
    'order by _Allele_key, numericPart', 'auto')

refs = {}
for r in results:
    key = r['_Allele_key']
    value = r['accID']

    if not refs.has_key(key):
        refs[key] = []
    refs[key].append(value)

#
# select allele, approval date, reference, symbol, and number of references
# sort by number of references highest to lowest
#

results = db.sql('select a._Allele_key, cDate = convert(char(10), a.approval_date, 101), a1.accID, a.alleleType, a.symbol, a.numRefs ' + \
    'from #alleles a, ACC_Accession a1 ' + \
    'where a._Allele_key = a1._Object_key ' + \
    'and a1._MGIType_key = 11 ' + \
    'and a1._LogicalDB_key = 1 ' + \
    'and a1.prefixPart = "MGI:" ' + \
    'and a1.preferred = 1 ' + \
    'order by a.numRefs desc, a.symbol', 'auto')

for r in results:

    listOfRefs = refs[r['_Allele_key']]
    listOfRefs.sort()
    listOfRefs.reverse()

    fp.write(string.ljust(r['cDate'], 15) + \
             string.ljust(r['accID'], 15) + \
             string.ljust(r['alleleType'], 45) + \
             string.ljust(r['symbol'], 35))

    # total number of references associated with each alleles
    fp.write(string.ljust(str(r['numRefs']), 15))

    for l in listOfRefs:
        if l == listOfRefs[-1]:
            fp.write(str(l))
        else:
            fp.write(str(l) + ',')
    fp.write(CRT)

fp.write(CRT + 'Number of Alleles: ' + str(len(results)) + CRT)

reportlib.finish_nonps(fp)

