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
import string
import mgi_utils
import reportlib

try:
    if os.environ['DB_TYPE'] == 'postgres':
        import pg_db
        db = pg_db
        db.setTrace()
        db.setAutoTranslateBE()
    else:
        import db
except:
    import db


CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Create a list of dataset keys to be included in the report.
#
datasetKeys = [ 1005 ]
inClause = string.join(map(str,datasetKeys),',')

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

#
# Get the dataset abbreviations to be used for the report heading.
#
results = db.sql('''
	select _DataSet_key, abbreviation 
        from BIB_DataSet 
        where _DataSet_key in (%s)
        order by _DataSet_key
	''' % (inClause), 'auto')

#
# Write the report heading.
#
fp.write('J Number')
fp.write(TAB + 'PubMed ID')
for r in results:
    fp.write(TAB + r['abbreviation'])
fp.write(TAB + 'Review')
fp.write(CRT)

#
# Build a temp table with the review indicator and dataset keys for each
# reference that has no marker association.  Only select the datasets
# specified in the list of keys.
#
db.sql('''
	select cc.jnumID, cc.pubmedID, cc.isReviewArticle, da._DataSet_key 
        into #refds 
        from BIB_DataSet_Assoc da, BIB_Citation_Cache cc 
        where da._DataSet_key in (%s)
              and da._Refs_key = cc._Refs_key 
              and cc.numericPart >= 121000
              and not exists (select 1 from MRK_Reference r where da._Refs_key = r._Refs_key) 
	''' % (inClause), None)

#
# Get each J number/dataset pair needed to build the grid.
#
results = db.sql('select jnumID, pubmedID, _DataSet_key from #refds', 'auto')

#
# Build a dictionary where the key is the J number and the value is a list
# of datasets selected for that reference.
#
dict = {}
for r in results:
    jnumID = r['jnumID']
    dsKey = r['_DataSet_key']

    #
    # If there is already a dataset for the reference, append another one.
    #
    if dict.has_key(jnumID):
        dict[jnumID].append(dsKey)
    #
    # If this is a new reference, start a new dataset list.
    #
    else:
        dsKeyList = [dsKey]
        dict[jnumID] = dsKeyList


#
# Get the review indicator for each J number.
#
results = db.sql('''
	select distinct jnumID, pubmedID, isReviewArticle 
        from #refds 
        order by jnumID
	''', 'auto')

#
# For each J number, get its review indicator and list of datasets.
#
for r in results:
    jnumID = r['jnumID']
    pubmedID = r['pubmedID']
    review = r['isReviewArticle']
    dsKeyList = dict[jnumID]

    #
    # Write the J number in the first column.
    #
    fp.write(jnumID)
    fp.write(TAB + mgi_utils.prvalue(pubmedID))

    #
    # Write an "X" under each dataset in the heading if the J number has
    # been selected for that dataset.
    #
    for dsKey in datasetKeys:
        if dsKey in dsKeyList:
            fp.write(TAB + 'X')
        else:
            fp.write(TAB)

    #
    # Write "Yes" or "No" under the review column, depending on whether
    # the J number is a review article.
    #
    if review:
        fp.write(TAB + 'Yes')
    else:
        fp.write(TAB + 'No')
    fp.write(CRT)

reportlib.finish_nonps(fp)
