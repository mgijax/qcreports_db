#!/usr/local/bin/python

'''
#
# MRK_GOIEA.py 01/08/2002
#
# Report:
#       TR 3269 - Report 1
#
#	Report 2A
#	Title = Genes Not RIKEN or 'expressed' or 'EST' with only GO Associations w/ IEA evidence
#	Select markers of type 'gene' 
#		where 'current' name does not contain 'RIKEN' or 'expressed' or 'EST'
#               where the marker has 'GO' association w/ IEA only
#               where the reference count exludes J:23000, J:57747, J:63103, J:57656, J:51368, 
#               J:67225, J:67226, or any reference that has "Genbank Submission"  in 
#               the Journal title
#
#       Report in a tab delimited file with the following columns:
#
#    		MGI:ID
#    		symbol
#    		name
#    		number of references
#    		human or rat ortholog?    'yes'
#
#    	Report 2B
#	Title = Genes Not RIKEN or 'expressed' or 'EST' with only GO Associations w/ IEA evidence
#    	Select markers of type 'gene'
#    		where 'current' name does not contain 'RIKEN' or 'expressed' or 'EST'
#               where the marker has 'GO' association w/ IEA only
#
#    	Report in a tab delimited file with same columns as 1A
#
#	Report 2C
#	Title = Genes Not RIKEN or 'expressed' or 'EST' with only GO Associations w/ IEA evidence
#	Select markers of type 'gene' 
#		where 'current' name does not contain 'RIKEN' or 'expressed' or 'EST'
#               where the marker has 'GO' association w/ IEA only
#               where the reference count includes J:23000, J:57747, J:63103, J:57656, J:51368, 
#               J:67225, J:67226, or any reference that has "Genbank Submission"  in 
#               the Journal title
#
#    	Report in a tab delimited file with same columns as 1A
#
#	Report 2D
#	Title = Gene Not RIKEN or 'expressed' or 'EST' with only GO Assocations w/ IEA evidence
#               with references that are selected for GO but have not been used
#
#    	Report in a tab delimited/html file:
#		J:
#		PubMed ID (with HTML link)
#		MGI:ID
#		Y/N (has reference been selected for GXD)
#		symbol
#		name
#
#	Sort by:
#		MGI:ID
#
# Usage:
#       MRK_GOIEA.py
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
# lec	02/23/2004
#	- exclude Gene Model markers, DNA Segments (already excluded), Pseudogenes (already excluded),
#	  genes whose symbol is a GenBank # (AFXXXXX, BCXXXXX, etc.),
#	  ORFs, genes with only J:81149, J:77944 as a reference.
#
# lec	01/08/2002
#	- created
#
'''
 
import sys 
import os
import regsub
import db
import reportlib
import mgi_utils

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

PUBMED = 29
url = ''

def writeRecord(fp, r):

	fp.write(r['mgiID'] + TAB)
	fp.write(r['symbol'] + TAB)
	fp.write(r['name'] + TAB)
	fp.write(`r['numRefs']` + TAB)

	if hasHomology.has_key(r['_Marker_key']):
		fp.write('yes' + CRT)
	else:
		fp.write('no' + CRT)

def writeRecordD(fp, r):

	fp.write(r['jnumID'] + TAB)

	if pubMedIDs.has_key(r['_Refs_key']):
		purl = regsub.gsub('@@@@', pubMedIDs[r['_Refs_key']], url)
		fp.write('<A HREF="%s">%s</A>' % (purl, pubMedIDs[r['_Refs_key']]))
	fp.write(TAB)

	if r['_Refs_key'] in gxd:
		fp.write('Y' + TAB)
	else:
		fp.write('N' + TAB)

	fp.write(r['mgiID'] + TAB + \
	         r['symbol'] + TAB + \
	         r['name'] + CRT)

#
# Main
#

db.useOneConnection(1)
fpA = reportlib.init("MRK_GOIEA_A", printHeading = 0, outputdir = os.environ['QCOUTPUTDIR'])
fpB = reportlib.init("MRK_GOIEA_B", printHeading = 0, outputdir = os.environ['QCOUTPUTDIR'])
fpC = reportlib.init("MRK_GOIEA_C", printHeading = 0, outputdir = os.environ['QCOUTPUTDIR'])
fpD = reportlib.init("MRK_GOIEA_D", printHeading = 0, outputdir = os.environ['QCOUTPUTDIR'], isHTML = 1)

results = db.sql('select url from ACC_ActualDB where _LogicalDB_key = %d ' % (PUBMED), 'auto')
for r in results:
	url = r['url']

# select markers with GO Associations of evidence IEA only

print 'query 1 begin...%s' % (mgi_utils.date())
cmds = []
cmds.append('select m._Marker_key, m.symbol, m.name, mgiID = a.accID, a.numericPart ' + \
	'into #markers ' + \
	'from MRK_Marker m, ACC_Accession a ' + \
	'where m._Marker_Type_key = 1 ' + \
	'and m._Marker_Status_key in (1,3) ' + \
	'and m.name not like "%RIKEN%" ' + \
	'and m.name not like "%expressed%" ' + \
	'and m.name not like "EST %" ' + \
	'and m.name not like "gene model %" ' + \
	'and m.symbol not like "[A-Z][0-9][0-9][0-9][0-9][0-9]" ' + \
	'and m.symbol not like "[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]" ' + \
	'and m.symbol not like "ORF%" ' + \
	'and m._Marker_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1 ' + \
	'and exists (select 1 from  VOC_Annot a, VOC_Evidence e ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._EvidenceTerm_key = 115) ' + \
	'and not exists (select 1 from  VOC_Annot a, VOC_Evidence e ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._EvidenceTerm_key != 115) ')
cmds.append('create index idx1 on #markers(_Marker_key)')
db.sql(cmds, None)
print 'query 1 end...%s' % (mgi_utils.date())

# orthologies

print 'query 2 begin...%s' % (mgi_utils.date())
results = db.sql('select distinct m._Marker_key ' + \
	'from #markers m ' + \
	'where exists (select 1 from HMD_Homology h1, HMD_Homology_Marker hm1, ' + \
	'HMD_Homology h2, HMD_Homology_Marker hm2, MRK_Marker m2 ' + \
	'where hm1._Marker_key = m._Marker_key ' + \
	'and hm1._Homology_key = h1._Homology_key ' + \
	'and h1._Class_key = h2._Class_key ' + \
	'and h2._Homology_key = hm2._Homology_key ' + \
	'and hm2._Marker_key = m2._Marker_key ' + \
	'and m2._Organism_key = 2) ' + \
	'union ' + \
	'select distinct m._Marker_key ' + \
	'from #markers m ' + \
	'where exists (select 1 from HMD_Homology h1, HMD_Homology_Marker hm1, ' + \
	'HMD_Homology h2, HMD_Homology_Marker hm2, MRK_Marker m2 ' + \
	'where hm1._Marker_key = m._Marker_key ' + \
	'and hm1._Homology_key = h1._Homology_key ' + \
	'and h1._Class_key = h2._Class_key ' + \
	'and h2._Homology_key = hm2._Homology_key ' + \
	'and hm2._Marker_key = m2._Marker_key ' + \
	'and m2._Organism_key = 40) ', 'auto')
hasHomology = {}
for r in results:
	hasHomology[r['_Marker_key']] = 1
print 'query 2 end...%s' % (mgi_utils.date())

##

print 'query 3 begin...%s' % (mgi_utils.date())
cmds = []
cmds.append('select distinct m.*, r._Refs_key ' + \
	'into #references1 ' + \
	'from #markers m , MRK_Reference r ' + \
	'where m._Marker_key = r._Marker_key ')
cmds.append('create index index_refs_key on #references1(_Refs_key)')
db.sql(cmds, None)
print 'query 3 end...%s' % (mgi_utils.date())

print 'query 4 begin...%s' % (mgi_utils.date())
cmds = []
cmds.append('select r.*, b.jnum, b.jnumID, b.short_citation ' + \
	'into #references ' + \
	'from #references1 r, BIB_All_View b ' + \
	'where r._Refs_key = b._Refs_key')
cmds.append('create index index_refs_key on #references(_Refs_key)')
db.sql(cmds, None)
print 'query 4 end...%s' % (mgi_utils.date())

# select PubMed IDs for references

print 'query 5 begin...%s' % (mgi_utils.date())
results = db.sql('select distinct r._Refs_key, a.accID ' + \
	'from #references r, ACC_Accession a ' + \
	'where r._Refs_key = a._Object_key ' + \
	'and a._MGIType_key = 1 ' + \
	'and a._LogicalDB_key = %d ' % (PUBMED) + \
	'and a.preferred = 1', 'auto')
pubMedIDs = {}
for r in results:
	pubMedIDs[r['_Refs_key']] = r['accID']
print 'query 5 end...%s' % (mgi_utils.date())

# has reference been chosen for GXD
print 'query 6 begin...%s' % (mgi_utils.date())
results = db.sql('select distinct r._Refs_key ' + \
	'from #references r, BIB_DataSet_Assoc ba, BIB_DataSet bd ' + \
	'where r._Refs_key = ba._Refs_key ' + \
	'and ba._DataSet_key = bd._DataSet_key ' + \
	'and bd.dataSet = "Expression" ' + \
	'and ba.isNeverUsed = 0', 'auto')
gxd = []
for r in results:
	gxd.append(r['_Refs_key'])
print 'query 6 end...%s' % (mgi_utils.date())

print 'query 7 begin...%s' % (mgi_utils.date())
results = db.sql('select distinct _Marker_key, symbol, name, mgiID, numRefs = count(_Refs_key) ' + \
	'from #references ' + \
	'where jnum not in (23000, 57747, 63103, 57676, 67225, 67226, 81149, 77944) ' + \
	'and short_citation not like "%Genbank Submission%" ' + \
	'group by _Marker_key ' + \
	'order by symbol', 'auto')
for r in results:
	writeRecord(fpA, r)
print 'query 7 end...%s' % (mgi_utils.date())

print 'query 8 begin...%s' % (mgi_utils.date())
results = db.sql('select distinct _Marker_key, symbol, name, mgiID, numRefs = count(_Refs_key) ' + \
	'from #references group by _Marker_key ' + \
	'order by symbol', 'auto')
for r in results:
	writeRecord(fpB, r)
print 'query 8 end...%s' % (mgi_utils.date())

print 'query 9 begin...%s' % (mgi_utils.date())
results = db.sql('select distinct _Marker_key, symbol, name, mgiID, numRefs = count(_Refs_key) ' + \
	'from #references ' + \
	'where jnum in (23000, 57747, 63103, 57676, 67225, 67226, 81149, 77944) ' + \
	'and short_citation not like "%Genbank Submission%" ' + \
	'group by _Marker_key ' + \
	'order by symbol', 'auto')
for r in results:
	writeRecord(fpC, r)
print 'query 9 end...%s' % (mgi_utils.date())

print 'query 10 begin...%s' % (mgi_utils.date())
results = db.sql('select distinct r._Marker_key, r._Refs_key, r.symbol, r.name, r.mgiID, r.jnumID, r.numericPart ' + \
	'from #references r, BIB_DataSet_Assoc ba, BIB_DataSet bd ' + \
	'where r._Refs_key = ba._Refs_key ' + \
	'and ba._DataSet_key = bd._DataSet_key ' + \
	'and bd.dataSet = "Gene Ontology" ' + \
	'and ba.isNeverUsed = 0 ' + \
	'and not exists (select 1 from VOC_Evidence e, VOC_Annot a ' + \
	'where r._Refs_key = e._Refs_key ' + \
	'and e._Annot_key = a._Annot_key ' + \
	'and a._AnnotType_key = 1000) ' + \
	'order by numericPart', 'auto')
for r in results:
	writeRecordD(fpD, r)
print 'query 10 end...%s' % (mgi_utils.date())

reportlib.finish_nonps(fpA)	# non-postscript file
reportlib.finish_nonps(fpB)	# non-postscript file
reportlib.finish_nonps(fpC)	# non-postscript file
reportlib.finish_nonps(fpD, isHTML = 1)	# non-postscript file
db.useOneConnection(0)

