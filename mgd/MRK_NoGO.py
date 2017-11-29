#!/usr/local/bin/python

'''
#
# MRK_NoGO.py 01/08/2002
#
# Report:
#
#	TR 3269 (removed A,B,C)
#
#	TR 4491
#	Report 1D
#	Title = Genes with no GO associations
#    	Select markers of type 'gene'
#		where 'current' name does not contain 'gene model', 'gene trap'
#               where the marker has no 'GO' association.
#
#	Report in a tab delimited/html file with the following columns:
#
#	J: of reference associated with the Marker, selected for GO but has not been used in annotation
#	PubMed ID of reference (with HTML link to PubMed)	(TR 4698)
#	Ref in GXD?
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
# lec	11/27/2017
#	- TR12678
#	- column GXD? = set to Y if GXD workflow status = Indexed or Chosen
#	- add column heading for GXD column = "Ref in GXD?"
#	- filter out Gt(ROSA)26Sor
#
# sc	10/05/2017
#	- TR 12250 Littriage project, exclude Gt(ROSA)26Sor and Gcna
#
#	04/07/2011
#	- TR 10668; exclude feature type ''heritable phenotypic marker' (6238170)
#
# lec	12/31/2009
#	- TR 9989; remove A,B,C; keep D
#
# lec	09/17/2008
#	- TR 9265; remove "RIKEN", "expressed", "EST" restrictions
#
# lec	07/09/2008
#	- TR 8945
#
# lec	02/12/2008
#	- TR 8774; exclude "gene trap" markers
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
import string
import mgi_utils
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

PUBMED = 29
url = ''
pdfurl = os.environ['PDFVIEWER_URL']
gxd = []

fpD = None

def reportOpen():
    global fpD

    fpD = reportlib.init("MRK_NoGO_D", printHeading = None, outputdir = os.environ['QCOUTPUTDIR'], isHTML = 1)

def reportClose():
    global fpD

    reportlib.finish_nonps(fpD, isHTML = 1)

def runQueries():

    global gxd, url

    results = db.sql('select url from ACC_ActualDB where _LogicalDB_key = %d ' % (PUBMED), 'auto')
    for r in results:
	    url = r['url']

    # exclude markers that have GO annotations
    # exclude markers that contain feature 'heritable phenotypic marker' (6238170)

    db.sql('''
	   select m._Marker_key, m.symbol, m.name, a.accID as mgiID, a.numericPart, 'no '::text as hasOrthology
	   into temporary table markers 
	   from MRK_Marker m, ACC_Accession a 
	   where m._Marker_Type_key = 1 
	   and m._Marker_Status_key = 1
	   and m.name !~ 'gene model %' 
	   and m.name !~ 'gene trap %' 
	   and m.symbol !~ '[A-Z][0-9][0-9][0-9][0-9][0-9]' 
	   and m.symbol !~ '[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]' 
	   and m.symbol !~ 'ORF%' 
	   and m.symbol !~ 'Gt(ROSA)26Sor' 
	   and m._Marker_key = a._Object_key 
	   and a._MGIType_key = 2 
	   and a._LogicalDB_key = 1 
	   and a.prefixPart = 'MGI:' 
	   and a.preferred = 1 
	   and not exists (select 1 from  VOC_Annot a 
	   where m._Marker_key = a._Object_key 
	   and a._AnnotType_key = 1000) 
	   and not exists (select 1 from  VOC_Annot a 
	   where m._Marker_key = a._Object_key 
	   and a._AnnotType_key = 1011
	   and a._Term_key = 6238170)
	   ''', None)
    db.sql('create index markers_idx1 on markers(_Marker_key)', None)

    # orthologies

    db.sql('''update markers set hasOrthology = 'yes'
	where exists (select 1 from MRK_Cluster mc, MRK_ClusterMember hm1, MRK_ClusterMember hm2, MRK_Marker mh 
	where mc._ClusterSource_key = 9272151 
        and mc._Cluster_key = hm1._Cluster_key 
	and hm1._Marker_key = markers._Marker_key 
	and hm1._Cluster_key = hm2._Cluster_key 
	and hm2._Marker_key = mh._Marker_key 
	and mh._Organism_key = 2) 
	''', None)

    db.sql('''update markers set hasOrthology = 'yes' 
	where exists (select 1 from MRK_Cluster mc, MRK_ClusterMember hm1, MRK_ClusterMember hm2, MRK_Marker mh 
	where mc._ClusterSource_key = 9272151 
        and mc._Cluster_key = hm1._Cluster_key 
	and hm1._Marker_key = markers._Marker_key 
	and hm1._Cluster_key = hm2._Cluster_key 
	and hm2._Marker_key = mh._Marker_key 
	and mh._Organism_key = 40) 
	''', None)

    # references

    db.sql('''select m._Marker_key, m.symbol, m.name, m.mgiID, m.numericPart, m.hasOrthology, 
	r._Refs_key, r.pubmedID, b.journal, b.mgiID as refID
	into temporary table references1 
	from markers m , MRK_Reference r, BIB_Citation_Cache b 
	where m._Marker_key = r._Marker_key
	and m._Marker_key not in ( 25559, 37270 ) -- Gcna, Gt(ROSA)26Sor
	and r._Refs_key = b._Refs_key
	and r.jnum is not null
	''', None)
    db.sql('create index references_idx1 on references1(_Refs_key)', None)
    db.sql('create index references_idx2 on references1(_Marker_key)', None)
    db.sql('create index references_idx3 on references1(symbol)', None)
    db.sql('create index references_idx4 on references1(numericPart)', None)

    # yes if reference has be indexed/chosen for gxd

    results = db.sql('''select distinct r._Refs_key
        from references1 r, BIB_Workflow_Status w
        where r._Refs_key = w._Refs_key
        and w._Group_key = 31576665
        and w._Status_key in (31576673, 31576671)  -- indexed or chosen
        ''', 'auto')
    for r in results:
        gxd.append(r['_Refs_key'])

def writeRecordD(fp, r):

	fp.write('<A HREF="%s%s">%s</A>' %(pdfurl, r['refID'], r['refID']) + TAB)

	if r['pubmedID'] != None:
		purl = string.replace(url, '@@@@', r['pubmedID'])
		fp.write('<A HREF="%s">%s</A>' % (purl, r['pubmedID']))
	fp.write(TAB)

        if r['_Refs_key'] in gxd:
                fp.write('Y' + TAB)
        else:
                fp.write('N' + TAB)

	fp.write(r['refID'] + TAB + \
	         r['symbol'] + TAB + \
	         r['name'] + CRT)

def reportD():

    db.sql('''select distinct r._Marker_key, r._Refs_key, r.symbol,
	r.name, r.mgiID, r.refID, r.numericPart, r.pubmedID, r.hasOrthology 
	into temporary table fpD 
	from references1 r, BIB_Workflow_Status s
	where r._Refs_key = s._Refs_key 
        and r._Refs_key = s._Refs_key 
        and s._Group_key = 31576666
        and s._Status_key in (31576673, 31576671)
        and s.isCurrent = 1 
	and not exists (select 1 from VOC_Evidence e, VOC_Annot a 
	where r._Refs_key = e._Refs_key 
	and e._Annot_key = a._Annot_key 
	and a._AnnotType_key = 1000) 
	''', None)

    # number of unique MGI gene
    results = db.sql('select distinct _Marker_key from fpD', 'auto')
    fpD.write('Number of unique MGI Gene IDs:  %s\n' % (len(results)))

    # number of unique J:
    results = db.sql('select distinct _Refs_key from fpD', 'auto')
    fpD.write('Number of unique J: IDs:  %s\n' % (len(results)))

    # number of has orthology?
    results = db.sql('select * from fpD where hasOrthology = \'yes\'', 'auto')
    fpD.write('Number of has orthology? = yes:  %s\n' % (len(results)))
    results = db.sql('select * from fpD where hasOrthology = \'no \'', 'auto')
    fpD.write('Number of has orthology? = no:  %s\n' % (len(results)))

    # total number of rows
    results = db.sql('select * from fpD', 'auto')
    fpD.write('Total number of rows:  %s\n\n' % (len(results)))

    fpD.write('ref ID' + TAB + \
	     'pubMed ID' + TAB + \
	     'ref in GXD?' + TAB + \
	     'mgi ID' + TAB + \
	     'symbol' + TAB + \
	     'name' + CRT*2)

    results = db.sql('select * from fpD order by hasOrthology desc, numericPart', 'auto')
    for r in results:
	    writeRecordD(fpD, r)

#
# Main
#

reportOpen()
runQueries()
reportD()
reportClose()

