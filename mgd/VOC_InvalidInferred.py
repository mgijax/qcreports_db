#!/usr/local/bin/python

'''
#
# VOC_InvalidInferred.py 10/17/2003
#
# Report:
#	TR 5311
#
#       Tab-delimited file
#       Annotation Evidence Inferred From Accession IDs
#	which are invalid.
#
# Usage:
#       VOC_InvalidInferred.py
#
# Used by:
#       Annotation Editors
#
# Notes:
#
# History:
#
# lec	11/14/2003
#	- new
#
'''
 
import sys
import os
import string
import regsub
import db
import mgi_utils
import reportlib

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)
fp.write('Invalid "Inferred From" Values in Annotations (MGI and InterPro only)' + 2 * reportlib.CRT)
rows = 0

results = db.sql('select distinct inferredFrom from VOC_Evidence where inferredFrom != null', 'auto')
for r in results:
    ids = r['inferredFrom']

    if string.find(ids, ', ') >= 0:
	delimiter = ', '
    elif string.find(ids, ',') >= 0:
	delimiter = ','
    elif string.find(ids, '; ') >= 0:
	delimiter = '; '
    elif string.find(ids, '|') >= 0:
	delimiter = '|'
    else:
	delimiter = ''

    if len(delimiter) > 0:
        idList = string.split(ids, delimiter)
    else:
	idList = [ids]

    for id in idList:
	id = regsub.gsub('"', '', id)

	if string.find(id, 'MGI:') >= 0:
	    idResult = db.sql('select _Object_key from ACC_Accession where accID = "%s"' % (id), 'auto')
	    if len(idResult) == 0:
		fp.write(id + reportlib.CRT)
		rows = rows + 1

	if string.find(id, 'INTERPRO:') >= 0:
	    [prefixPart, idPart] = string.split(id, 'INTERPRO:')
	    idResult = db.sql('select _Object_key from ACC_Accession where accID = "%s"' % (idPart), 'auto')
	    if len(idResult) == 0:
		fp.write(id + reportlib.CRT)
		rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))
reportlib.finish_nonps(fp)

