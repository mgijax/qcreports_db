#!/usr/local/bin/python

'''
#
# GO_done.py
#
# Report:
#       
# A report of all markers with GO Annotations 
# where the GO marker is a reference gene
# OR
# the GO Annotation has a completion date.
#
# field 1: Gene Symbol
# field 2: Gene Accession ID
# field 3: Reference gene? (y/n)
# field 4: Completion Date
# field 5: # of outstanding references
# field 6: list of references that have not yet been annotated to the gene
#	   whose creation date is greater than the completion date.
#
# Usage:
#       GO_done.py
#
# History:
#
# 01/27/2010
#	- TR9612; reduced this report to 
#	  "completed annotations that contain new literature"
#
# 01/06/2010
#	- TR9996/modification to "more than 5 references"
#
# 10/24/2006	lec
#	- TR7533/7920; GO tracking
#
# 10/17/2006	lec
#	- TR 7976; added Reference genes; more columns
#
# 08/28/2006	lec
#	- TR 7876; added headings and Refs_used column
#
# 03/02/2006	lec
#	- TR 7532
#
'''
 
import sys 
import os
import re
import string
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

def printResults(cmd, isReferenceGene):

    global reportCount

    results = db.sql(cmd, 'auto')
    for r in results:

        key = r['_Marker_key']

	# skip if no literature
	if not jnums.has_key(key):
	   continue

        if gorefs.has_key(key):
           numRefs = str(len(gorefs[key]))
        else:
	   numRefs = '0'
     
        fp.write(r['symbol'] + TAB)
        fp.write(r['accID'] + TAB)
        fp.write(isReferenceGene + TAB)
        fp.write(r['cdate'] + TAB)
        fp.write(numRefs + TAB)
        fp.write(str(len(jnums[key])) + TAB)
	fp.write(string.join(jnums[key], ',') + CRT)

	reportCount = reportCount + 1

#
# Main
#

fp = reportlib.init(sys.argv[0], fileExt = '.mgi', outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)
fp.write('Gene Symbol' + TAB)
fp.write('MGI-ID' + TAB)
fp.write('reference gene status' + TAB)
fp.write('Date_complete' + TAB)
fp.write('#Refs_used' + TAB)
fp.write('outstanding_refs' + TAB)
fp.write('J numbers' + 2*CRT)

#
# select all Markers w/ GO Annotations that are Reference genes
# and that contains a completion date
#
db.sql('''select cdate = convert(char(10), t.completion_date, 101), m._Marker_key, m.symbol, a.accID
	  into #goref 
	  from GO_Tracking t, MRK_Marker m, ACC_Accession a 
	  where t.isReferenceGene = 1 
	  and t.completion_date is not null 
	  and t._Marker_key = m._Marker_key 
	  and m._Marker_key = a._Object_key 
	  and a._MGIType_key = 2 
	  and a._LogicalDB_key = 1 
	  and a.prefixPart = "MGI:" 
	  and a.preferred = 1''', None)
db.sql('create index idx1 on #goref(_Marker_key)', None)

#
# select all Markers w/ GO Annotations that contains a completion date
#
db.sql('''select cdate = convert(char(10), t.completion_date, 101), m._Marker_key, m.symbol, a.accID 
	  into #godone 
	  from GO_Tracking t, MRK_Marker m, ACC_Accession a 
	  where t.completion_date is not null 
	  and t._Marker_key = m._Marker_key 
	  and m._Marker_key = a._Object_key 
	  and a._MGIType_key = 2 
	  and a._LogicalDB_key = 1 
	  and a.prefixPart = "MGI:" 
	  and a.preferred = 1 ''', None)
db.sql('create index idx1 on #godone(_Marker_key)', None)

results = db.sql('select * from #godone', 'auto')
godone = {}
for r in results:
    key = r['_Marker_key']
    value = r
    godone[key] = r

#
# select all jnumbers that exist from both goref and godone
#
results = db.sql('''select b._Marker_key, b.jnumID 
		    from BIB_GOXRef_View b, #goref g
		    where b._Marker_key = g._Marker_key
	            and b.creation_date > dateadd(day,1,g.cdate)
		    union
                    select b._Marker_key, b.jnumID 
		    from BIB_GOXRef_View b, #godone g
		    where b._Marker_key = g._Marker_key
	            and b.creation_date > dateadd(day,1,g.cdate)
		    ''', 'auto')

jnums = {}
for r in results: 
    key = r['_Marker_key']
    value = r['jnumID']
    if not jnums.has_key(key):
        jnums[key] = []
    jnums[key].append(r['jnumID'])

#
# cache # of GO references per Marker
# exclude J:60000,J:73065,J:72245,J:80000,J:72247,J:99680
#

results = db.sql('select distinct m._Marker_key, e._Refs_key ' + \
	'from #goref m, VOC_Annot a, VOC_Evidence e ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._Refs_key not in (61933,73197,73199,74017,80961,100707) ' + \
	'union ' + \
	'select distinct m._Marker_key, e._Refs_key ' + \
	'from #godone m, VOC_Annot a, VOC_Evidence e ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._Refs_key not in (61933,73197,73199,74017,80961,100707)', 'auto')
gorefs = {}
for r in results:
    key = r['_Marker_key']
    value = r['_Refs_key']
    if not gorefs.has_key(key):
	gorefs[key] = []
    gorefs[key].append(value)

reportCount = 0

# reference genes first
printResults('select * from #goref order by symbol', 'y')

# dones that are not reference genes
printResults('select d.* from #godone d ' + \
	'where not exists (select 1 from #goref r where d._Marker_key = r._Marker_key) ' + \
	'order by d.symbol', 'n')

fp.write(CRT * 2)
fp.write('total number of genes: %s\n' % (reportCount))

reportlib.finish_nonps(fp)

