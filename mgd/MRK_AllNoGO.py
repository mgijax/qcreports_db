#!/usr/local/bin/python

'''
#
# MRK_AllNoGO.py 04/11/2003
#
# Report:
#	TR 4698
#	Title = Genes with References chosen for GO but not used for GO
#    	Select markers of type 'gene'
#
#	Report in a tab delimited/html file with the following columns:
#
#	J: of reference associated with the Marker, selected for GO but has not been used in annotation
#	PubMed ID of reference (with HTML link to PubMed)	(TR 4698)
#	Y/N (has reference been selected for GXD)
#	MGI:ID
#	Y/N (does gene have GO annotations)
#	symbol
#	name
#
# Usage:
#       MRK_AllNoGO.py
#
# Notes:
#	- all reports use mgireport directory for output file
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
#
# lec	04/11/2003
#	- TR 4698
#
'''
 
import sys 
import os
import regsub
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

PUBMED = 29
url = ''

def writeRecord(fp, r):

	fp.write(r['jnumID'] + TAB)

	if pubMedIDs.has_key(r['_Refs_key']):
		purl = regsub.gsub('@@@@', pubMedIDs[r['_Refs_key']], url)
		fp.write('<A HREF="%s">%s</A>' % (purl, pubMedIDs[r['_Refs_key']]))
	fp.write(TAB)

	if r['_Refs_key'] in gxd:
		fp.write('Y' + TAB)
	else:
		fp.write('N' + TAB)

	fp.write(r['mgiID'] + TAB)

	if r['_Marker_key'] in annotations:
		fp.write('Y' + TAB)
	else:
		fp.write('N' + TAB)

	fp.write(r['symbol'] + TAB + \
	         r['name'] + CRT)

#
# Main
#

fp = reportlib.init("MRK_AllNoGO", printHeading = 0, outputdir = os.environ['QCREPORTOUTPUTDIR'], isHTML = 1)

cmds = []

cmds.append('select url from ACC_ActualDB where _LogicalDB_key = %d ' % (PUBMED))

# select all genes

cmds.append('select m._Marker_key, m.symbol, m.name, mgiID = a.accID, a.numericPart ' + \
'into #markers ' + \
'from MRK_Marker m, MRK_Acc_View a ' + \
'where m._Marker_Type_key = 1 ' + \
'and m._Marker_Status_key = 1 ' + \
'and m._Marker_key = a._Object_key ' + \
'and a._LogicalDB_key = 1 ' + \
'and a.prefixPart = "MGI:" ' + \
'and a.preferred = 1')

cmds.append('create nonclustered index index_marker_key on #markers(_Marker_key)')

# select all genes with references selected for GO

cmds.append('select distinct m.*, r._Refs_key, r.jnumID, b.dbs ' + \
'into #references ' + \
'from #markers m , MRK_Reference_View r, BIB_Refs b ' + \
'where m._Marker_key = r._Marker_key ' + \
'and r._Refs_key = b._Refs_key ' + \
'and b.dbs like "%GO%" and b.dbs not like "%GO*%"')

cmds.append('create nonclustered index index_refs_key on #references(_Refs_key)')

# select PubMed IDs for references

cmds.append('select distinct r._Refs_key, a.accID ' + \
'from #references r, BIB_Acc_View a ' + \
'where r._Refs_key = a._Object_key ' + \
'and a._LogicalDB_key = %d ' % (PUBMED) + \
'and a.preferred = 1')

# has reference been selected for GXD

cmds.append('select distinct r._Refs_key ' + \
'from #references r ' + \
'where r.dbs like "%Expression%" and r.dbs not like "%Expression*%"')

# does marker have GO annotations

cmds.append('select distinct r._Marker_key ' + \
'from #references r, VOC_Annot a ' + \
'where a._AnnotType_key = 1000 ' + \
'and r._Marker_key = a._Object_key')

cmds.append('select distinct r._Marker_key, r._Refs_key, r.symbol, r.name, r.mgiID, r.jnumID, r.numericPart ' + \
'from #references r ' + \
'order by r.numericPart')

results = db.sql(cmds, 'auto')

for r in results[0]:
	url = r['url']

pubMedIDs = {}
for r in results[-4]:
	pubMedIDs[r['_Refs_key']] = r['accID']

gxd = []
for r in results[-3]:
	gxd.append(r['_Refs_key'])

annotations = []
for r in results[-2]:
	annotations.append(r['_Marker_key'])

for r in results[-1]:
	writeRecord(fp, r)

reportlib.finish_nonps(fp, isHTML = 1)	# non-postscript file

