#!/usr/local/bin/python

'''
#
# TR 7879
#
# Report:
#       A report of gene trap allele lab codes and their max sequence number
#
#	Lab Code
#	Max Sequence Number
#
#	Lab Codes w/ Duplicate Sequence Numbers (if any exist)
#
# Usage:
#       ALL_GeneTrap.py
#
# Notes:
#
# History:
#
# 08/28/2006	lec
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

maxlabcodes = {}
alllabcodes = {}

fp = reportlib.init(sys.argv[0], 'Gene Trap Allele Lab Codes and their Max Sequence Number', os.environ['QCOUTPUTDIR'])

#
# select all gene trap alleles where name has given format.
# categorize records by those entered within the last year (yearOK = 1)
# and those entered more than one year ago (yearOK = 0)
#
# 'gene trap% ##, provider'
#

db.sql('select symbol, name, yearOK = 1 ' + \
       'into #allele ' + \
       'from ALL_Allele where _Allele_Type_key = 847121 and name like "gene trap%,%" ' + \
       'and creation_date >= dateadd(year, -1, getdate()) ' + \
       'union ' + \
       'select symbol, name, yearOK = 0 ' + \
       'from ALL_Allele where _Allele_Type_key = 847121 and name like "gene trap%,%" ' + \
       'and creation_date < dateadd(year, -1, getdate())', None)

#
# order by yearOK descending (1 before 0)
#

results = db.sql('select * from #allele order by yearOK desc', 'auto')
for r in results:

    name = r['name']
    yearOK = int(r['yearOK'])

    #
    # split name first by comma + space
    #
    # "gene trap 1, Lexcion Genetics" ==> "gene trap 1", "Lexicon Genetics"
    #

    tokens1 = string.split(name, ', ')
    labcode = tokens1[1]

    #
    # split first token by space
    #
    # "gene trap 1" ==> "gene" "trap" "1"
    #

    tokens2 = string.split(tokens1[0], ' ')

    #
    # find first token that is entirely digits
    # if none found, then set lab seq number to 0
    #

    labseq = 0
    for t in tokens2:
	if t.isdigit():
	    labseq = int(t)
            break

    #
    # skip records where lab seq number cannot be determined
    #

    if labseq == 0:
	continue

    if labcode == 'Lexicon Genetics Inc':
	labcode = 'Lexicon Genetics'

    #
    # cache the max lab sequence number
    #

    if not maxlabcodes.has_key(labcode):
	maxlabcodes[labcode] = labseq
    else:
	if labseq > maxlabcodes[labcode]:
	    maxlabcodes[labcode] = labseq

    allkey = (labcode, labseq)

    #
    # there must be a least one creation date within the past year
    # for this statistic to be printed.
    #
    # yearOK = 1 records are processed first and cached.
    # (records are sorted by yearOK descending above)
    #
    # when yearOK = 0 records are processed, if there is a cached value 
    # for the corresponding yearOK = 1 record, then continue to increment the counter.
    # else, do not increment the counter.
    #

    if yearOK:
        if not alllabcodes.has_key(allkey):
	    alllabcodes[allkey] = 0
        alllabcodes[allkey] = alllabcodes[allkey] + 1
    else:
	if alllabcodes.has_key(allkey):
	    alllabcodes[allkey] = alllabcodes[allkey] + 1

#
# sort by lab code
#

labcodeKeys = maxlabcodes.keys()
labcodeKeys.sort()

#
# print out lab codes and max sequence numbers
#

recs = 0
for c in labcodeKeys:

    fp.write(string.ljust(c, 50))
    fp.write(string.ljust(str(maxlabcodes[c]), 25) + CRT)

    recs = recs + 1

fp.write('\n(%d rows affected)\n' % (recs))

#
# print out lab codes and sequence numbers that are duplicates
#

fp.write(CRT)
fp.write('Duplicate numbers' + 2*CRT)

labcodeKeys = alllabcodes.keys()
labcodeKeys.sort()

recs = 0
for c in labcodeKeys:
    if alllabcodes[c] > 1:
        fp.write(string.ljust(c[0], 50))
        fp.write(string.ljust(str(c[1]), 25) + CRT)
        recs = recs + 1
fp.write('\n(%d rows affected)\n' % (recs))

reportlib.finish_nonps(fp)

