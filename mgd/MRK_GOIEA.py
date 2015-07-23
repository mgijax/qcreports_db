#!/usr/local/bin/python

'''
#
# MRK_GOIEA.py 01/08/2002
#
# Report:
#       TR 3269 - remove A,B,C,F
#
#	Report 2D
#	Title = Gene with only GO Assocations w/ IEA evidence
#               with references that are selected for GO but have not been used
#
#    	Report in a tab delimited/html file:
#		J:
#		PubMed ID (with HTML link)
#		MGI:ID
#		Y/N (has reference been selected for GXD)
#		symbol
#		name
#		OMIM (print "OMIM" if gene has a mouse model associated with an OMIM disease)
#
#	Report 2E (TR 7125)
#	Title = Genes that have OMIM annotations and either no GO annotations or only IEA GO annotations
#    	Select markers of type 'gene'
#               where the marker has 'OMIM' associations
#               where the marker has 'GO' association w/ IEA only or no GO annotations
#
#       Report in a tab delimited file with the following columns:
#
#    		MGI:ID
#    		symbol
#    		GO ("no" if no GO, "yes" if IEA)
#	Sort by:
#		symbol
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
# lec	08/22/2011
#	- TR10813; 2E; include feature type = 'protein coding genes' only
#
# lec	12/31/2009
#	- TR 9989; remove A,C,F
#
# lec	09/17/2008
#	- TR 9265; remove RIKEN, expressed, EST restrictions
#
# lec	07/08/2008
#	- TR 8945
#
# lec	02/12/2008
#	- TR 8774/remove report "B"
#	- TR 8774/"D": add number of unique mgi gene ids
#
# lec	10/26/2005
#	- TR 7190; exclude from Report 2F any Marker that has at most one Allele and
#	  that Allele has reference J:94338.
#
# lec	09/28/2005
#	- TR 7125; added Report 2E
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
import string
import mgi_utils
import reportlib
import db

db.setTrace()
db.setAutoTranslateBE()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

PUBMED = 29
url = ''
jfileurl = 'http://prodwww.informatics.jax.org/usrlocalmgi/jfilescanner/current/get.cgi?jnum='

def writeRecordD(fp, r):

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

	if r['_Marker_key'] in omim:
		fp.write('OMIM')
	fp.write(CRT)

def writeRecordF(fp, r):

	fp.write(r['mgiID'] + TAB + \
	         r['symbol'] + TAB + \
		 r['isGO'] + CRT)

#
# Main
#

fpD = reportlib.init("MRK_GOIEA_D", printHeading = None, outputdir = os.environ['QCOUTPUTDIR'], isHTML = 1)
fpD.write('jnum ID' + TAB + \
	 'pubMed ID' + TAB + \
	 'ref in GXD?' + TAB + \
	 'mgi ID' + TAB + \
	 'symbol' + TAB + \
	 'name' + TAB + \
	 'OMIM' + CRT*2)

fpE = reportlib.init("MRK_GOIEA_E", printHeading = None, outputdir = os.environ['QCOUTPUTDIR'])
fpE.write('mgi ID' + TAB + \
	 'symbol' + TAB + \
	 'GO?' + CRT*2)

results = db.sql('select url from ACC_ActualDB where _LogicalDB_key = %d ' % (PUBMED), 'auto')
for r in results:
	url = r['url']

# select non-ORF genes with GO Associations of evidence IEA only

db.sql('''select m._Marker_key, m.symbol, m.name, mgiID = a.accID, a.numericPart
	into #markers
	from MRK_Marker m, ACC_Accession a
	where m._Marker_Type_key = 1
	and m._Marker_Status_key in (1,3)
	and m.name !~ 'gene model %'
	and m.symbol !~ '[A-Z][0-9][0-9][0-9][0-9][0-9]'
	and m.symbol !~ '[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]'
	and m.symbol not like 'ORF%'
	and m._Marker_key = a._Object_key
	and a._MGIType_key = 2
	and a._LogicalDB_key = 1
	and a.prefixPart = 'MGI:'
	and a.preferred = 1
	and exists (select 1 from  VOC_Annot a, VOC_Evidence e
	where m._Marker_key = a._Object_key
	and a._AnnotType_key = 1000
	and a._Annot_key = e._Annot_key
	and e._EvidenceTerm_key = 115)
	and not exists (select 1 from  VOC_Annot a, VOC_Evidence e
	where m._Marker_key = a._Object_key
	and a._AnnotType_key = 1000
	and a._Annot_key = e._Annot_key
	and e._EvidenceTerm_key != 115) 
	''', None)
db.sql('create index markers_idx1 on #markers(_Marker_key)', None)

##

db.sql('''select distinct m.*, r._Refs_key, r.pubmedID
	into #references1
	from #markers m , MRK_Reference r
	where m._Marker_key = r._Marker_key
	''', None)
db.sql('create index index_refs1_key on #references1(_Refs_key)', None)

db.sql('''select r.*, b.jnum, b.jnumID, b.short_citation
	into #references2
	from #references1 r, BIB_All_View b
	where r._Refs_key = b._Refs_key
	''', None)
db.sql('create index index_refs_key on #references2(_Refs_key)', None)

# has reference been chosen for GXD
results = db.sql('''select distinct r._Refs_key
	from #references2 r, BIB_DataSet_Assoc ba, BIB_DataSet bd
	where r._Refs_key = ba._Refs_key
	and ba._DataSet_key = bd._DataSet_key
	and bd.dataSet = "Expression"
	and ba.isNeverUsed = 0
	''', 'auto')
gxd = []
for r in results:
	gxd.append(r['_Refs_key'])

# does gene have mouse model annotated to OMIM disease
results = db.sql('''select distinct m._Marker_key
	from #markers m, MRK_OMIM_Cache o
	where m._Marker_key = o._Marker_key
	''', 'auto')
omim = []
for r in results:
	omim.append(r['_Marker_key'])

#
# fpD
#

db.sql('''select distinct r._Marker_key, r._Refs_key, r.symbol, r.name, r.mgiID,
	r.jnumID, r.jnum, r.numericPart, r.pubmedID
	into #fpD
	from #references2 r, BIB_DataSet_Assoc ba, BIB_DataSet bd
	where r._Refs_key = ba._Refs_key
	and ba._DataSet_key = bd._DataSet_key
	and bd.dataSet = "Gene Ontology"
	and ba.isNeverUsed = 0
	and not exists (select 1 from VOC_Evidence e, VOC_Annot a
	where r._Refs_key = e._Refs_key
	and e._Annot_key = a._Annot_key
	and a._AnnotType_key = 1000)
	''', None)

# number of unique MGI gene
results = db.sql('select distinct _Marker_key from #fpD', 'auto')
fpD.write('Number of unique MGI Gene IDs:  %s\n' % (len(results)))

# number of unique J:gene
results = db.sql('select distinct _Refs_key from #fpD', 'auto')
fpD.write('Number of unique J: IDs:  %s\n' % (len(results)))

# total number of rows
results = db.sql('select * from #fpD', 'auto')
fpD.write('Total number of rows:  %s\n\n' % (len(results)))

results = db.sql('select * from #fpD order by numericPart', 'auto')
for r in results:
	writeRecordD(fpD, r)

#
# report 2E
#

# select genes with OMIM Associations
# feature type = 'protein coding genes'

db.sql('''select m._Marker_key, m.symbol, mgiID = a.accID, a.numericPart 
	into #omimmarkers
	from MRK_Marker m, ACC_Accession a, VOC_Annot tdc
	where m._Organism_key = 1
	and m._Marker_Type_key = 1
	and m._Marker_Status_key in (1,3)
	and m._Marker_key = a._Object_key
	and a._MGIType_key = 2
	and a._LogicalDB_key = 1
	and a.prefixPart = 'MGI:'
	and a.preferred = 1
	and m._Marker_key = tdc._Object_key
	and tdc._AnnotType_key = 1011
	and tdc._Term_key = 6238161
	and exists (select 1 from GXD_AlleleGenotype g, VOC_Annot a
	where m._Marker_key = g._Marker_key
	and g._Genotype_key = a._Object_key
	and a._AnnotType_key = 1005) ''', None)
db.sql('create index omim_idx1 on #omimmarkers(_Marker_key)', None)

#
# select markers with OMIM annotations and either only IEA GO annotations or no GO annotations
#

db.sql('''select o.*, "yes" as isGO
	into #fpE
	from #omimmarkers o, #markers m
	where o._Marker_key = m._Marker_key
	union
	select o.*, "no" as isGO
	from #omimmarkers o
	where not exists 
	  (select 1 from VOC_Annot a where o._Marker_key = a._Object_key and a._AnnotType_key = 1000)
	''', None)

# number of unique MGI gene
results = db.sql('select distinct _Marker_key from #fpE', 'auto')
fpE.write('Number of unique MGI Gene IDs:  %s\n' % (len(results)))

# total number of rows
results = db.sql('select * from #fpE', 'auto')
fpE.write('Total number of rows:  %s\n\n' % (len(results)))

results = db.sql('select * from #fpE order by symbol', 'auto')
for r in results:
    writeRecordF(fpE, r)

reportlib.finish_nonps(fpD, isHTML = 1)	# non-postscript file
reportlib.finish_nonps(fpE)	# non-postscript file

