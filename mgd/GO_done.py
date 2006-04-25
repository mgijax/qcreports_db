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
	   whose creation date is greater than the completion date.
#
# Usage:
#       GO_done.py
#
# History:
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

#
# select all Markers w/ GO Annotation Note that contains a Complete Date
#
results = db.sql('select distinct n._Object_key, note = rtrim(n.note), m.symbol ' + \
	'from MGI_Note_MRKGO_View n, MRK_Marker m ' + \
	'where n._Object_key = m._Marker_key ' + \
	'and n.note like "%<d>%"', 'auto')
gonote = {}
for r in results:
    key = r['_Object_key']
    value = r
    gonote[key] = r

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

    results = db.sql('select jnumID from BIB_GOXRef_View where _Marker_key = %s ' % (k) + \
	'and convert(char(10), creation_date, 101) > dateadd(day,1,"%s")' % (checkDate), 'auto')

    # no references meet criteria

    if len(results) == 0:
	fp.write(m['symbol'] + TAB + checkDate + TAB + CRT)
	continue

    # references that do meet criteria

    jnums = []
    for r in results: 
	jnums.append(r['jnumID'])
    fp.write(m['symbol'] + TAB + checkDate + TAB + string.joinfields(jnums, ',') + CRT)

reportlib.finish_nonps(fp)	# non-postscript file

