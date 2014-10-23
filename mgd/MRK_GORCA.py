#!/usr/local/bin/python

'''
#
# MRK_GORCA.py 07/13/2007
#
# Report:
#       TR 8382 
#
#	Report 1A
#	Title = Gene with only 
#               GO Associations w/ RCA evidence with references that are 
#               selected for GO but have not been used
#
#    	Report in a tab delimited/html file:
#		J:
#		PubMed ID (with HTML link)
#		MGI:ID of Gene
#		Y/N (has reference been selected for GXD)
#		symbol
#		name
#       Sort By: MGI:ID of Gene
#
# Usage:
#       MRK_GORCA.py
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
# lec	09/17/2008
#	- TR 9265; remove RIKEN, exporessed, EST restrictions
#
# lec	07/09/2008
#	- TR 8945
#
# sc	07/13/2007
#	- created
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

PUBMED = 29
url = ''
jfileurl = 'http://prodwww.informatics.jax.org/usrlocalmgi/jfilescanner/current/get.cgi?jnum='

def writeRecordA(fp, r):

	fp.write('<A HREF="%s%s">%s</A>' %(jfileurl, r['jnum'], r['jnumID']) + TAB)

	if r['pubmedID'] != None:
		purl = string.replace(url, '@@@@', r['pubmedID'])
		fp.write('<A HREF="%s">%s</A>' % (purl, r['pubmedID']))
	fp.write(TAB)

	if r['_Refs_key'] in gxd:
		fp.write('Y' + TAB)
	else:
		fp.write('N' + TAB)

	fp.write(r['mgiID'] + TAB + \
	         r['symbol'] + TAB + \
	         r['name'] + TAB)

	fp.write(CRT)


#
# Main
#

fpA = reportlib.init("MRK_GORCA", printHeading = None, outputdir = os.environ['QCOUTPUTDIR'], isHTML = 1)
fpA.write('jnum ID' + TAB + \
	 'pubMed ID' + TAB + \
	 'ref in GXD?' + TAB + \
	 'mgi ID' + TAB + \
	 'symbol' + TAB + \
	 'name' + CRT*2)

results = db.sql('select url from ACC_ActualDB where _LogicalDB_key = %d ' % (PUBMED), 'auto')
for r in results:
	url = r['url']

# select genes with GO Associations of evidence RCA only

db.sql('select m._Marker_key, m.symbol, m.name, mgiID = a.accID, a.numericPart ' + \
	'into #markers ' + \
	'from MRK_Marker m, ACC_Accession a ' + \
	'where m._Marker_Type_key = 1 ' + \
	'and m._Marker_Status_key in (1,3) ' + \
	'and m.symbol not like "[A-Z][0-9][0-9][0-9][0-9][0-9]" ' + \
	'and m.symbol not like "[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]" ' + \
	'and m._Marker_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1 ' + \
	'and exists (select 1 from  VOC_Annot a, VOC_Evidence e ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._EvidenceTerm_key = 514597) ' + \
	'and not exists (select 1 from  VOC_Annot a, VOC_Evidence e ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._EvidenceTerm_key != 514597) ', None)

db.sql('create index markers_idx1 on #markers(_Marker_key)', None)

db.sql('select distinct m.*, r._Refs_key, r.pubmedID ' + \
	'into #references1 ' + \
	'from #markers m , MRK_Reference r ' + \
	'where m._Marker_key = r._Marker_key ', None)

db.sql('create index index_refs1_key on #references1(_Refs_key)', None)

db.sql('select r.*, b.jnum, b.jnumID, b.short_citation ' + \
	'into #references2 ' + \
	'from #references1 r, BIB_All_View b ' + \
	'where r._Refs_key = b._Refs_key', None)

db.sql('create index index_refs_key on #references2(_Refs_key)', None)

# has reference been chosen for GXD
results = db.sql('select distinct r._Refs_key ' + \
	'from #references2 r, BIB_DataSet_Assoc ba, BIB_DataSet bd ' + \
	'where r._Refs_key = ba._Refs_key ' + \
	'and ba._DataSet_key = bd._DataSet_key ' + \
	'and bd.dataSet = "Expression" ' + \
	'and ba.isNeverUsed = 0', 'auto')
gxd = []
for r in results:
	gxd.append(r['_Refs_key'])

db.sql('select distinct r._Marker_key, r._Refs_key, r.symbol, r.name, r.mgiID, ' + \
	'r.jnumID, r.jnum, r.numericPart, r.pubmedID ' + \
	'into #fpA ' + \
	'from #references2 r, BIB_DataSet_Assoc ba, BIB_DataSet bd ' + \
	'where r._Refs_key = ba._Refs_key ' + \
	'and ba._DataSet_key = bd._DataSet_key ' + \
	'and bd.dataSet = "Gene Ontology" ' + \
	'and ba.isNeverUsed = 0 ' + \
	'and not exists (select 1 from VOC_Evidence e, VOC_Annot a ' + \
	'where r._Refs_key = e._Refs_key ' + \
	'and e._Annot_key = a._Annot_key ' + \
	'and a._AnnotType_key = 1000)', None)

# number of unique MGI gene
results = db.sql('select distinct _Marker_key from #fpA', 'auto')
fpA.write('Number of unique MGI Gene IDs:  %s\n' % (len(results)))

# number of unique J:
results = db.sql('select distinct _Refs_key from #fpA', 'auto')
fpA.write('Number of unique J: IDs:  %s\n' % (len(results)))

# total number of rows
results = db.sql('select * from #fpA', 'auto')
fpA.write('Total number of rows:  %s\n\n' % (len(results)))

results = db.sql('select * from #fpA order by numericPart', 'auto')
for r in results:
	writeRecordA(fpA, r)

reportlib.finish_nonps(fpA, isHTML = 1)	# non-postscript file

