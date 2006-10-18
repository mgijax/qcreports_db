#!/usr/local/bin/python

'''
#
# GO_done.py
#
# Report:
#       
# A report of all markers with GO Annotations where the GO Annotation Note contains
# a completion date (format "<d>MM/DD/YYYY</d>).
#
# field 1: Gene Symbol
# field 2: Completion Date
# field 3: list of references that have not yet been annotated to the gene
#	   whose creation date is greater than the completion date.
#
# Usage:
#       GO_done.py
#
# History:
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

def outstandingrefs(key, cDate):
    # return list of jnumbers selected for GO that have not already been used in an annotation
    # return list of jnumbers selected for GO whose creation date is greater than the completion date
    # depending on whether there is a completion date, or not

    jnums = []

    if cDate == '':
	results = db.sql('select r.jnumID from BIB_GOXRef_View r where r._Marker_key = %s ' % (key) + \
		' and not exists (select 1 from VOC_Annot a, VOC_Evidence e ' + \
		' where a._AnnotType_key = 1000 ' + \
	        ' and a._Annot_key = e._Annot_key ' + \
	        ' and e._Refs_key = r._Refs_key) ', 'auto')
    else:
	results = db.sql('select jnumID from BIB_GOXRef_View where _Marker_key = %s ' % (key) + \
		'and convert(char(10), creation_date, 101) > dateadd(day,1,"%s")' % (cDate), 'auto')

    for r in results: 
	jnums.append(r['jnumID'])

    return jnums

def printResults(cmd, isReferenceGene):

    results = db.sql(cmd, 'auto')
    for r in results:

        key = r['_Object_key']
        cDate = ''

        if gorefs.has_key(key):
            numRefs = str(len(gorefs[key]))
        else:
	    numRefs = '0'
    
        if godone.has_key(key):
            m = godone[key]
            cDate = re.sub('<d>', '', m['note'])
            cDate = re.sub('\n', '', cDate)
            tokens = string.split(cDate, '<')
            cDate = tokens[0]

	    jnums = outstandingrefs(key, cDate)
        else:
	    jnums = outstandingrefs(key, cDate)

        fp.write(r['symbol'] + TAB)
        fp.write(r['accID'] + TAB)
        fp.write(isReferenceGene + TAB)
        fp.write(cDate + TAB)
        fp.write(numRefs + TAB)

	# if more than 5 references, just print out how many, else list them

	if len(jnums) > 5:
	    fp.write(str(len(jnums)))
        else:
	    fp.write(string.join(jnums, ','))
        fp.write(CRT)

#
# Main
#

fp = reportlib.init(sys.argv[0], fileExt = '.mgi', outputdir = os.environ['QCOUTPUTDIR'], printHeading = None, sqlLogging = 0)
fp.write('Gene Symbol' + TAB)
fp.write('MGI-ID' + TAB)
fp.write('reference gene status' + TAB)
fp.write('Date_complete' + TAB)
fp.write('#Refs_used' + TAB)
fp.write('outstanding_refs' + 2*CRT)

#
# select all Markers w/ GO Annotation that are Reference genes
#
db.sql('select distinct n._Object_key, note = rtrim(n.note), m.symbol, a.accID ' + \
	'into #goref ' + \
	'from MGI_Note_MRKGO_View n, MRK_Marker m, ACC_Accession a ' + \
	'where n._Object_key = m._Marker_key ' + \
	'and n.note like "%<rg>%" ' + \
	'and m._Marker_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1', None)
db.sql('create index idx1 on #goref(_Object_key)', None)

#
# select all Markers w/ GO Annotation Note that contains a Complete Date
#
db.sql('select distinct n._Object_key, note = rtrim(n.note), m.symbol, a.accID ' + \
	'into #godone ' + \
	'from MGI_Note_MRKGO_View n, MRK_Marker m, ACC_Accession a ' + \
	'where n._Object_key = m._Marker_key ' + \
	'and n.note like "%<d>%" ' + \
	'and m._Marker_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1 ', None)
db.sql('create index idx1 on #godone(_Object_key)', None)

results = db.sql('select * from #godone', 'auto')
godone = {}
for r in results:
    key = r['_Object_key']
    value = r
    godone[key] = r

#
# cache # of GO references per Marker
# exclude J:60000,J:73065,J:72245,J:80000,J:72247,J:99680
#

results = db.sql('select distinct m._Object_key, e._Refs_key ' + \
	'from #goref m, VOC_Annot a, VOC_Evidence e ' + \
	'where m._Object_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._Refs_key not in (61933,73197,73199,74017,80961,100707) ' + \
	'union ' + \
	'select distinct m._Object_key, e._Refs_key ' + \
	'from #godone m, VOC_Annot a, VOC_Evidence e ' + \
	'where m._Object_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._Refs_key not in (61933,73197,73199,74017,80961,100707)', 'auto')
gorefs = {}
for r in results:
    key = r['_Object_key']
    value = r['_Refs_key']
    if not gorefs.has_key(key):
	gorefs[key] = []
    gorefs[key].append(value)

# reference genes first
printResults('select * from #goref order by symbol', 'y')

# dones that are not reference genes
printResults('select d.* from #godone d ' + \
	'where not exists (select 1 from #goref r where d._Object_key = r._Object_key) ' + \
	'order by d.symbol', 'n')

referenceGenes = db.sql('select count(*) from #goref', 'auto')[0]['']
completedGenes = db.sql('select count(*) from #godone', 'auto')[0]['']
refcompletedGenes = db.sql('select count(r._Object_key) from #goref r, #godone d where r._Object_key = d._Object_key', 'auto')[0]['']

fp.write(CRT * 2)
fp.write('total number of completed genes: %s\n' % (completedGenes))
fp.write('total number of reference genes: %s\n' % (referenceGenes))
fp.write('total number of reference genes that are completed: %s\n' % (refcompletedGenes))

reportlib.finish_nonps(fp)

