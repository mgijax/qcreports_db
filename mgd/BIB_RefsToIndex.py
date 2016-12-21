#!/usr/local/bin/python

'''
#
# TR 8354
#
# Report:
#
# References with no marker associations that have been selected for
# any of the following categories (datasets):
#
#     - Mapping                (_DataSet_key = 1001)
#     - Expression             (_DataSet_key = 1004)
#     - Gene Ontology          (_DataSet_key = 1005)
#     - Nomenclature           (_DataSet_key = 1006)
#
# The report should be a tab-delimited grid with J numbers going down and
# the datasets going across.  An "X" under a dataset indicates that it
# has been selected for that J number.  An additional column at the end
# should indicate if the J number is a review article.
#
# Usage:
#       BIB_RefsToIndex.py
#
# Notes:
#
# History:
#
# lec	08/10/2015
#	- TR11979/change rules
#
# lec	07/29/2010
#	- TR10281/add pubmedid
#
# lec	02/02/2010
#	- TR10056/remove Mapping, Expression & Nomen
#
# dbm	06/20/2007
#	- new
#
# dbm	08/10/2007
#	- removed Alleles & Phenotypes and Tumor columns from report (TR8440)
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

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

fp.write('\nReferences where:\n')
fp.write('\tselected for GO, not used for GO, not selected for A&P\n')

fp.write('\nJ Number')
fp.write(TAB + 'PubMed ID')
fp.write(TAB + 'Review')
fp.write(CRT)

#
# selected for GO (1005) where:
# not selected for A&P (1002)
# not used
#
results = db.sql('''
	select s1._Refs_key, cc.jnumID, cc.pubmedID, cc.isReviewArticle
        from BIB_DataSet_Assoc s1, BIB_Citation_Cache cc
        where s1._DataSet_key in (1005)
	and s1._Refs_key = cc._Refs_key
	and cc.numericPart >= 121000
	and not exists (select 1 from BIB_DataSet_Assoc s2 
		where s1._Refs_key = s2._Refs_key and s2._DataSet_key = 1002)
	and not exists (select 1 from MRK_Reference r where s1._Refs_key = r._Refs_key)
	order by cc.jnumID
	''', 'auto')

for r in results:
    jnumID = r['jnumID']
    pubmedID = r['pubmedID']
    review = r['isReviewArticle']

    fp.write(jnumID)
    fp.write(TAB + str(pubmedID))

    if review:
        fp.write(TAB + 'Yes')
    else:
        fp.write(TAB + 'No')

    fp.write(CRT)

reportlib.finish_nonps(fp)

