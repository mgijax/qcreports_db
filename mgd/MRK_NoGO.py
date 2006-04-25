#!/usr/local/bin/python

'''
#
# MRK_NoGO.py 01/08/2002
#
# Report:
#       TR 3269 - Report 1
#
#	Report 1A
#	Title = Genes Not RIKEN or 'expressed' or 'EST' with no GO associations
#	Select markers of type 'gene' 
#		where 'current' name does not contain 'RIKEN' or 'expressed' or 'EST'
#               where the marker has no 'GO' association
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
#    	Report 1B
#    	Title = Genes Not RIKEN or 'expressed' or 'EST' with no GO associations
#    	Select markers of type 'gene'
#    		where 'current' name does not contain 'RIKEN' or 'expressed' or 'EST'
#               where the marker has no 'GO' association.
#
#    	Report in a tab delimited file with same columns as 1A
#
#	Report 1C
#	Title = Genes Not RIKEN or 'expressed' or 'EST' with no GO associations
#	Select markers of type 'gene' 
#		where 'current' name does not contain 'RIKEN' or 'expressed' or 'EST'
#               where the marker has no 'GO' association
#               where the reference count includes J:23000, J:57747, J:63103, J:57656, J:51368, 
#               J:67225, J:67226, or any reference that has "Genbank Submission"  in 
#               the Journal title
#
#    	Report in a tab delimited file with same columns as 1A
#
#	TR 4491
#	Report 1D
#	Title = Genes Not RIKEN or 'expressed' or 'EST' with no GO associations
#    	Select markers of type 'gene'
#    		where 'current' name does not contain 'RIKEN' or 'expressed' or 'EST'
#               where the marker has no 'GO' association.
#
#	Report in a tab delimited/html file with the following columns:
#
#	J: of reference associated with the Marker, selected for GO but has not been used in annotation
#	PubMed ID of reference (with HTML link to PubMed)	(TR 4698)
#	Y/N (has the reference been selected for GXD)
#	MGI:ID
#	symbol
#	name
#
# Usage:
#       MRK_NoGO.py
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
# lec	07/22/2004
#	- TR 6053
#
# lec	02/23/2004
#	- exclude Gene Model markers, DNA Segments (already excluded), Pseudogenes (already excluded),
#	  genes whose symbol is a GenBank # (AFXXXXX, BCXXXXX, etc.),
#	  ORFs, genes with only J:81149, J:77944 as a reference.
#
# lec	04/11/2003
#	- TR 4698; added PubMed ID to 1D
#
# lec	02/11/2003
#	- TR 4491; added Report 1D
#
# lec	01/08/2002
#	- created
#
'''
 
import sys 
import os
import re
import db
import reportlib
import mgi_utils

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

PUBMED = 29
url = ''
jfileurl = 'http://shire.informatics.jax.org/usrlocalmgi/jfilescanner/current/get.cgi?jnum='
hasOrthology = {}
gxd = []

fpA = None
fpB = None
fpC = None
fpD = None

def reportOpen():
    global fpA, fpB, fpC, fpD

    fpA = reportlib.init("MRK_NoGO_A", printHeading = 0, outputdir = os.environ['QCOUTPUTDIR'])
    fpB = reportlib.init("MRK_NoGO_B", printHeading = 0, outputdir = os.environ['QCOUTPUTDIR'])
    fpC = reportlib.init("MRK_NoGO_C", printHeading = 0, outputdir = os.environ['QCOUTPUTDIR'])
    fpD = reportlib.init("MRK_NoGO_D", printHeading = 0, outputdir = os.environ['QCOUTPUTDIR'], isHTML = 1)

def reportClose():
    global fpA, fpB, fpC, fpD

    reportlib.finish_nonps(fpA)
    reportlib.finish_nonps(fpB)
    reportlib.finish_nonps(fpC)
    reportlib.finish_nonps(fpD, isHTML = 1)

def runQueries():

    global hasOrthology, gxd, url

    results = db.sql('select url from ACC_ActualDB where _LogicalDB_key = %d ' % (PUBMED), 'auto')
    for r in results:
	    url = r['url']

    db.sql('select m._Marker_key, m.symbol, m.name, mgiID = a.accID, a.numericPart ' + \
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
	    'and not exists (select 1 from  VOC_Annot a ' + \
	    'where m._Marker_key = a._Object_key ' + \
	    'and a._AnnotType_key = 1000 ) ', None)
    db.sql('create index idx1 on #markers(_Marker_key)', None)

    # orthologies

    results = db.sql('select m._Marker_key ' + \
	'from #markers m ' + \
	'where exists (select 1 from HMD_Homology h1, HMD_Homology_Marker hm1, ' + \
	'HMD_Homology h2, HMD_Homology_Marker hm2, MRK_Marker m2 ' + \
	'where hm1._Marker_key = m._Marker_key ' + \
	'and hm1._Homology_key = h1._Homology_key ' + \
	'and h1._Class_key = h2._Class_key ' + \
	'and h2._Homology_key = hm2._Homology_key ' + \
	'and hm2._Marker_key = m2._Marker_key ' + \
	'and m2._Organism_key = 2) ', 'auto')
    for r in results:
	hasOrthology[r['_Marker_key']] = 1

    results = db.sql('select m._Marker_key ' + \
	'from #markers m ' + \
	'where exists (select 1 from HMD_Homology h1, HMD_Homology_Marker hm1, ' + \
	'HMD_Homology h2, HMD_Homology_Marker hm2, MRK_Marker m2 ' + \
	'where hm1._Marker_key = m._Marker_key ' + \
	'and hm1._Homology_key = h1._Homology_key ' + \
	'and h1._Class_key = h2._Class_key ' + \
	'and h2._Homology_key = hm2._Homology_key ' + \
	'and hm2._Marker_key = m2._Marker_key ' + \
	'and m2._Organism_key = 40) ', 'auto')
    for r in results:
	hasOrthology[r['_Marker_key']] = 1

    db.sql('select m._Marker_key, m.symbol, m.name, m.mgiID, m.numericPart, ' + \
	'r._Refs_key, r.jnumID, r.jnum, r.pubmedID, b.journal ' + \
	'into #references ' + \
	'from #markers m , MRK_Reference r, BIB_Refs b ' + \
	'where m._Marker_key = r._Marker_key ' + \
	'and r._Refs_key = b._Refs_key', None)
    db.sql('create index idx1 on #references(_Refs_key)', None)
    db.sql('create index idx2 on #references(_Marker_key)', None)
    db.sql('create index idx3 on #references(symbol)', None)
    db.sql('create index idx4 on #references(numericPart)', None)

    # has reference been chosen for GXD

    results = db.sql('select distinct r._Refs_key ' + \
	'from #references r, BIB_DataSet_Assoc ba, BIB_DataSet bd ' + \
	'where r._Refs_key = ba._Refs_key ' + \
	'and ba._DataSet_key = bd._DataSet_key ' + \
	'and bd.dataSet = "Expression" ' + \
	'and ba.isNeverUsed = 0', 'auto')
    for r in results:
	gxd.append(r['_Refs_key'])

def writeRecord(fp, r):

	fp.write(r['mgiID'] + TAB + \
	         r['symbol'] + TAB + \
	         r['name'] + TAB + \
	         `r['numRefs']` + TAB)

	if hasOrthology.has_key(r['_Marker_key']):
		fp.write('yes' + CRT)
	else:
		fp.write('no' + CRT)

def writeRecordD(fp, r):

	fp.write('<A HREF="%s%s">%s</A>' %(jfileurl, r['jnum'], r['jnumID']) + TAB)

	if r['pubmedID'] != None:
		purl = re.sub('@@@@', r['pubmedID'], url)
		fp.write('<A HREF="%s">%s</A>' % (purl, r['pubmedID']))
	fp.write(TAB)

	if r['_Refs_key'] in gxd:
		fp.write('Y' + TAB)
	else:
		fp.write('N' + TAB)

	fp.write(r['mgiID'] + TAB + \
	         r['symbol'] + TAB + \
	         r['name'] + CRT)

def reportA():

    fpA.write('mgi ID' + TAB + \
	     'symbol' + TAB + \
	     'name' + TAB + \
	     '# of refs' + TAB + \
	     'has orthology?' + CRT*2)

    results = db.sql('select distinct _Marker_key, symbol, name, mgiID, numRefs = count(_Refs_key) ' + \
	'from #references ' + \
	'where jnum not in (23000, 57747, 63103, 57676, 67225, 67226, 81149, 77944) ' + \
	'and journal != "Genbank Submission" ' + \
	'group by _Marker_key ' + \
	'order by symbol', 'auto')
    for r in results:
	    writeRecord(fpA, r)

def reportB():

    fpB.write('mgi ID' + TAB + \
	     'symbol' + TAB + \
	     'name' + TAB + \
	     '# of refs' + TAB + \
	     'has orthology?' + CRT*2)

    results = db.sql('select distinct _Marker_key, symbol, name, mgiID, numRefs = count(_Refs_key) ' + \
	'from #references group by _Marker_key ' + \
	'order by symbol', 'auto')
    for r in results:
	    writeRecord(fpB, r)

def reportC():

    fpC.write('mgi ID' + TAB + \
	     'symbol' + TAB + \
	     'name' + TAB + \
	     '# of refs' + TAB + \
	     'has orthology?' + CRT*2)

    db.sql('select distinct r1._Marker_key, r1.symbol, r1.name, r1.mgiID, r1._Refs_key ' + \
	'into #refC ' + \
	'from #references r1 ' + \
	'where r1.jnum in (23000, 57747, 63103, 57676, 67225, 67226, 81149, 77944) ' + \
	'or r1.journal = "Genbank Submission"', None)
    db.sql('create index idx1 on #refC(_Marker_key)', None)
    db.sql('create index idx2 on #refC(symbol)', None)

    results = db.sql('select distinct r1._Marker_key, r1.symbol, r1.name, r1.mgiID, ' + \
	'numRefs = count(r1._Refs_key) ' + \
	'from #refC r1 ' + \
	'where exists (select 1 from #references r2 where r1._Marker_key = r2._Marker_key ' + \
	'and r2._Refs_key not in (23000, 57747, 63103, 57676, 67225, 67226, 81149, 77944)) ' + \
	'group by r1._Marker_key ' + \
	'order by r1.symbol', 'auto')
    for r in results:
	writeRecord(fpC, r)

def reportD():

    fpD.write('jnum ID' + TAB + \
	     'pubMed ID' + TAB + \
	     'ref in GXD?' + TAB + \
	     'mgi ID' + TAB + \
	     'symbol' + TAB + \
	     'name' + CRT*2)

    results = db.sql('select distinct r._Marker_key, r._Refs_key, r.symbol, ' + \
	'r.name, r.mgiID, r.jnumID, r.jnum, r.numericPart, r.pubmedID ' + \
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
    fpD.write('\n(%d rows affected)\n' % (len(results)))

#
# Main
#

reportOpen()
runQueries()
reportA()
reportB()
reportC()
reportD()
reportClose()

