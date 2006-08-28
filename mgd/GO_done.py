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

#
# Main
#

fp = reportlib.init(sys.argv[0], fileExt = '.mgi', outputdir = os.environ['QCOUTPUTDIR'], printHeading = 0)
fp.write('Gene Symbol' + TAB)
fp.write('Date_complete' + TAB)
fp.write('#Refs_used' + TAB)
fp.write('outstanding_refs' + 2*CRT)

#
# select all Markers w/ GO Annotation Note that contains a Complete Date
#
db.sql('select distinct n._Object_key, note = rtrim(n.note), m.symbol ' + \
	'into #gomarkers ' + \
	'from MGI_Note_MRKGO_View n, MRK_Marker m ' + \
	'where n._Object_key = m._Marker_key ' + \
	'and n.note like "%<d>%"', None)
db.sql('create index idx1 on #gomarkers(_Object_key)', None)

results = db.sql('select * from #gomarkers', 'auto')
gonote = {}
for r in results:
    key = r['_Object_key']
    value = r
    gonote[key] = r

#
# cache # of GO references per Marker
# exclude J:60000,J:73065,J:72245,J:80000,J:72247,J:99680
#

results = db.sql('select distinct m._Object_key, e._Refs_key ' + \
	'from #gomarkers m, VOC_Annot a, VOC_Evidence e ' + \
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

#
# for each Marker, compare the date in the note to the date of the references
# that have not yet been used to annotate this gene.
#
# if there are any such references with a creation date greater than the completion date, 
# then print out J# of that reference.
#
#

for k in gonote.keys():

    m = gonote[k]
    checkDate = re.sub('<d>', '', m['note'])
    checkDate = re.sub('\n', '', checkDate)
    tokens = string.split(checkDate, '<')
    checkDate = tokens[0]

    if string.count(checkDate, '/') != 2:
	fp.write(m['symbol'] + TAB + 'invalid date: %s' % (checkDate) + CRT)
	continue

    results = db.sql('select jnumID from BIB_GOXRef_View where _Marker_key = %s ' % (k) + \
	'and convert(char(10), creation_date, 101) > dateadd(day,1,"%s")' % (checkDate), 'auto')

    if gorefs.has_key(k):
        numRefs = str(len(gorefs[k]))
    else:
	numRefs = '0'
    
    # no references meet criteria

    if len(results) == 0:
	fp.write(m['symbol'] + TAB + checkDate + TAB + numRefs + TAB + CRT)
	continue

    # references that do meet criteria

    jnums = []
    for r in results: 
	jnums.append(r['jnumID'])
    fp.write(m['symbol'] + TAB + checkDate + TAB + numRefs + TAB + string.joinfields(jnums, ',') + CRT)

reportlib.finish_nonps(fp)	# non-postscript file

