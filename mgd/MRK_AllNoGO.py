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
# lec   10/23/2014
#       - TR11750/postres complient
#
# lec	07/08/2008
#	- TR 8945
#	show number of unique MGI gene ids
#	sort by "GO annotation?" by "Y" first
#	show numer of GO annotation "yes" and "no"
#	
# lec	04/11/2003
#	- TR 4698
#
'''
 
import sys 
import os
import string
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

PUBMED = 29
url = ''

def writeRecord(fp, r):

	fp.write(r['jnumID'] + TAB)

	if r['pubmedID'] != None:
		purl = string.replace(url, '@@@@', r['pubmedID'])
		fp.write('<A HREF="%s">%s</A>' % (purl, r['pubmedID']))
	fp.write(TAB)

	if r['_Refs_key'] in gxd:
		fp.write('Y' + TAB)
	else:
		fp.write('N' + TAB)

	fp.write(r['mgiID'] + TAB + \
	         r['hasAnnotations'] + TAB + \
	         r['symbol'] + TAB + \
	         r['name'] + CRT)

#
# Main
#

fp = reportlib.init("MRK_AllNoGO", printHeading = None, outputdir = os.environ['QCOUTPUTDIR'], isHTML = 1)

fp.write(CRT + 'jnumID' + TAB + \
	 'pubMedID' + TAB + \
	 'ref in GXD?' + TAB + \
	 'mgi ID' + TAB + \
	 'GO annotation?' + TAB + \
	 'symbol' + TAB + \
	 'name' + CRT*2)

results = db.sql('select url from ACC_ActualDB where _LogicalDB_key = %d ' % (PUBMED), 'auto')
for r in results:
	url = r['url']

##

# select all genes

db.sql('''
	select m._Marker_key, m.symbol, m.name, a.accID as mgiID, a.numericPart 
	into temporary table markers 
	from MRK_Marker m, ACC_Accession a 
	where m._Marker_Type_key = 1 
	and m._Marker_Status_key = 1
	and m._Marker_key = a._Object_key 
	and a._MGIType_key = 2 
	and a._LogicalDB_key = 1 
	and a.prefixPart = 'MGI:' 
	and a.preferred = 1
	''', None)
db.sql('create index idx1_marker_key on markers(_Marker_key)', None)

##

# select all genes with references selected for GO

db.sql('''
	select distinct m.*, r._Refs_key, r.jnumID, r.pubmedID, 'N' as hasAnnotations
	into temporary table references1 
	from markers m , MRK_Reference r, BIB_Refs b, BIB_DataSet_Assoc ba, BIB_DataSet bd 
	where m._Marker_key = r._Marker_key 
	and r._Refs_key = b._Refs_key 
	and b._Refs_key = ba._Refs_key 
	and ba._DataSet_key = bd._DataSet_key 
	and bd.dataSet = 'Gene Ontology' 
	and ba.isNeverUsed = 0
	''', None)
db.sql('create index idx2_refs_key on references1(_Refs_key)', None)
db.sql('create index idx2_marker_key on references1(_Marker_key)', None)

# has reference been selected for GXD

results = db.sql('''
	select distinct r._Refs_key 
	from references1 r, BIB_DataSet_Assoc ba, BIB_DataSet bd 
	where r._Refs_key = ba._Refs_key 
	and ba._DataSet_key = bd._DataSet_key 
	and bd.dataSet = 'Expression' 
	and ba.isNeverUsed = 0
	''', 'auto')
gxd = []
for r in results:
	gxd.append(r['_Refs_key'])

# does marker have GO annotations

db.sql('''
	update references1
	set hasAnnotations = 'Y'
	from VOC_Annot a
	where a._AnnotType_key = 1000 and references1._Marker_key = a._Object_key
	''', None)

db.sql('create index idx2_hasAnnotations on references1(hasAnnotations)', None)
db.sql('create index idx2_pubmedID on references1(pubmedID)', None)
db.sql('create index idx2_numericPart on references1(numericPart)', None)

# number of unique genes
c = db.sql('select count(distinct r._Marker_key) as c from references1 r', 'auto')[0]['c']
fp.write('Number of unique MGI Gene IDs:  %s\n' % (c))

# number of unique J:
c = db.sql('select count(distinct r._Refs_key) as c from references1 r', 'auto')[0]['c']
fp.write('Number of unique J: IDs:  %s\n' % (c))

# number of total rows
c = db.sql('select count(r._Marker_key) as c from references1 r', 'auto')[0]['c']
fp.write('Number of total rows:  %s\n' % (c))

# number of GO annotation "yes"
results = db.sql('''
	select distinct r._Marker_key, r._Refs_key, r.symbol, r.name, 
	       r.mgiID, r.jnumID, r.numericPart, r.pubmedID, r.hasAnnotations
	from references1 r 
	where r.hasAnnotations = 'Y'
	''', 'auto')
fp.write('Number of "GO annotation?" for Y:  %s\n' % (len(results)))

# number of GO annotation "no"
results = db.sql('''
	select distinct r._Marker_key, r._Refs_key, r.symbol, r.name, 
	       r.mgiID, r.jnumID, r.numericPart, r.pubmedID, r.hasAnnotations
	from references1 r 
	where r.hasAnnotations = 'N'
	''', 'auto')
fp.write('Number of "GO annotation?" for N:  %s\n\n' % (len(results)))

# records

results = db.sql('''
	select distinct r._Marker_key, r._Refs_key, r.symbol, r.name, 
	       r.mgiID, r.jnumID, r.numericPart, r.pubmedID, r.hasAnnotations 
	from references1 r 
	order by r.hasAnnotations desc, r.numericPart, r.pubmedID
	''', 'auto')

for r in results:
	writeRecord(fp, r)

reportlib.finish_nonps(fp, isHTML = 1)	# non-postscript file

