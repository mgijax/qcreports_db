#!/usr/local/bin/python

'''
#
# TR 7901
#
# Report:
#       Aleles that have Molecular Notes but no MP Annotations
#
#       Allele approval date
#	Allele MGI ID
#	Allele Type
#	Allele symbol
#       Number of References
#	J#'s (comma-separated, sorted by J#, highest first)
#
#	exclude non-approved Alleles
#	exclude not-applicable Alleles
#	exclude Alleles of type QTL
#	exclude Alleles of type "transgenic (cre/flp)"
#	exclude Alleles of type "transgenic (reporter)"
#
# Usage:
#       ALL_MolNotesNoMP.py
#
# Notes:
#
# History:
#
# 09/20/2006	lec
#       - created
#
# 08/08/2007	dbm
#       - added code to exclude rows with only J:94338 (TR8435)
#
# 08/10/2007	dbm
#       - added code to exclude rows with only J:94077 (TR8442)
#
# 10/23/2007
#	- TR 8553
#         exclude Not Applicable alleles
#	  add "number of references"
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

fp = reportlib.init(sys.argv[0], 'Alleles that have Molecular Notes but no MP Annotations', os.environ['QCOUTPUTDIR'])


fp.write(string.ljust('Approval', 15) + \
         string.ljust('Acc ID', 15) + \
         string.ljust('Allele Type', 45) + \
         string.ljust('Symbol', 35) + \
         string.ljust('References', 15) + CRT*2)

db.sql('select a._Allele_key, a.symbol, a.approval_date, alleleType = t.term ' + \
    'into #alleles  ' + \
    'from ALL_Allele a, VOC_Term t ' + \
    'where a.approval_date is not NULL ' + \
    'and a._Allele_Type_key not in (847130, 847128, 847129, 847127, 847131) ' + \
    'and a._Allele_Type_key = t._Term_key ' + \
    'and exists (select 1 from MGI_Note n, MGI_NoteType nt  ' + \
    'where a._Allele_key = n._Object_key  ' + \
    'and n._MGIType_key = 11  ' + \
    'and n._NoteType_key = nt._NoteType_key  ' + \
    'and nt.noteType = "Molecular")  ' + \
    'and not exists (select 1 from VOC_Annot t, GXD_AlleleGenotype g ' + \
    'where a._Allele_key = g._Allele_key ' + \
    'and g._Genotype_key = t._Object_key ' + \
    'and t._AnnotType_key = 1002)', None)
db.sql('create index idx1 on #alleles(_Allele_key)', None)

results = db.sql('select distinct a._Allele_key, a1.numericPart ' + \
    'from #alleles a, MGI_Reference_Assoc r, ACC_Accession a1 ' + \
    'where a._Allele_key = r._Object_key ' + \
    'and r._MGIType_key = 11 ' + \
    'and r._Refs_key = a1._Object_key ' + \
    'and a1._MGIType_key = 1 ' + \
    'and a1._LogicalDB_key = 1 ' + \
    'and a1.prefixPart = "J:" ' + \
    'and a1.preferred = 1', 'auto')

refs = {}
for r in results:
    key = r['_Allele_key']
    value = r['numericPart']

    if not refs.has_key(key):
        refs[key] = []
    refs[key].append(value)

results = db.sql('select a._Allele_key, cDate = convert(char(10), a.approval_date, 101), a1.accID, a.alleleType, a.symbol ' + \
    'from #alleles a, ACC_Accession a1 ' + \
    'where a._Allele_key = a1._Object_key ' + \
    'and a1._MGIType_key = 11 ' + \
    'and a1._LogicalDB_key = 1 ' + \
    'and a1.prefixPart = "MGI:" ' + \
    'and a1.preferred = 1 ' + \
    'order by a.approval_date desc, a.symbol', 'auto')

skipped = 0
for r in results:

    listOfRefs = refs[r['_Allele_key']]
    listOfRefs.sort()
    listOfRefs.reverse()

    # If the only reference is J:94077 or J:94338, exclude it from the report.
    #
    if (listOfRefs[0] == 94077 or listOfRefs[0] == 94338) and len(listOfRefs) == 1:
        skipped += 1
        continue

    fp.write(string.ljust(r['cDate'], 15) + \
             string.ljust(r['accID'], 15) + \
             string.ljust(r['alleleType'], 45) + \
             string.ljust(r['symbol'], 35))

    # total number of references associated with each alleles
    fp.write(string.ljust(str(len(listOfRefs)), 15))

    for l in listOfRefs:
        if l == listOfRefs[-1]:
            fp.write('J:' + str(l))
        else:
            fp.write('J:' + str(l) + ',')
    fp.write(CRT)

fp.write(CRT + 'Number of Alleles: ' + str(len(results) - skipped) + CRT)

reportlib.finish_nonps(fp)
