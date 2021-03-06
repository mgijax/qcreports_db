
'''
#
# MRK_GOIEA.py 01/08/2002
#
# Report:
#       TR 3269 - remove A,B,C,F
#
#	Report 2D
#	Title = Gene with only GO Assocations w/ IEA evidence
#               with references that are GO/Indexed or Chosen
#
#    	Report in a tab delimited/html file:
#		J:
#		PubMed ID (with HTML link)
#		Ref in GXD?
#		MGI:ID
#		symbol
#		name
#		DO (print "DO" if gene has a mouse model associated with an DO disease)
#
#	Report 2E (TR 7125)
#	Title = Genes that have DO annotations and either no GO annotations or only IEA GO annotations
#    	Select markers of type 'gene'
#               where the marker has 'DO' associations
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
# dbm   01/26/2020
#       TR13430 exclude references tagged with "GO:QC5_IEA-only_exclude"
#       (_Term_key = 71460412)
#
# sc	03/07/2018
#	- If Indexed or Chosen or Full-coded 'ref in GXD' = 'Y'
#	- add explanation of 'ref in GXD' column to report header
#
# lec   11/27/2017
#       - TR12678
#       - column GXD? = set to Y if GXD workflow status = Indexed or Chosen
#       - add column heading for GXD column = "Ref in GXD?"
#       - filter out Gt(ROSA)26Sor
#
# sc    10/05/2017
#	- TR12250/Lit Triage/update WF Status logic
#	  Add column for curator tag
#
# lec   09/13/2017
#       - TR12250/Lit Triage/replace Data Sets with Workflow Status
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

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

PUBMED = 29
url = ''
pdfurl = os.environ['PDFVIEWER_URL']

def writeRecordD(fp, r):

        fp.write('<A HREF="%s%s">%s</A>' %(pdfurl, r['refID'], r['refID']) + TAB)

        if r['pubmedID'] != None:
                purl = str.replace(url, '@@@@', r['pubmedID'])
                fp.write('<A HREF="%s">%s</A>' % (purl, r['pubmedID']))
        fp.write(TAB)

        if r['_Refs_key'] in gxd:
                fp.write('Y' + TAB)
        else:
                fp.write('N' + TAB)

        fp.write(r['refID'] + TAB + \
                 r['symbol'] + TAB + \
                 r['name'] + TAB)

        if r['_Marker_key'] in dolookup:
                fp.write('DO')
        fp.write(TAB)
        refsKey = r['_Refs_key']
        if refsKey in curTagDict:
            curList = curTagDict[refsKey]
            fp.write(', '.join(curList))
        fp.write(CRT)

def writeRecordF(fp, r):

        fp.write(r['mgiID'] + TAB + \
                 r['symbol'] + TAB + \
                 r['isGO'] + CRT)

#
# Main
#

fpD = reportlib.init("MRK_GOIEA_D", outputdir = os.environ['QCOUTPUTDIR'], isHTML = 1)

fpE = reportlib.init("MRK_GOIEA_E", outputdir = os.environ['QCOUTPUTDIR'])

results = db.sql('select url from ACC_ActualDB where _LogicalDB_key = %d ' % (PUBMED), 'auto')
for r in results:
        url = r['url']

# lookup for curator tag
curTagDict = {}
results = db.sql('''select t._Refs_key, vt.term
        from BIB_Workflow_Tag t, VOC_Term vt
        where t._Tag_key = vt._Term_key
        and vt.term like 'MGI:curator_%' ''', 'auto')
for r in results:
        refsKey = r['_Refs_key']
        tag = r['term']
        if refsKey not in curTagDict:
            curTagDict[refsKey] = []
        curTagDict[refsKey].append(tag)
# select non-ORF genes with GO Associations of evidence IEA only

db.sql('''select m._Marker_key, m.symbol, m.name, a.accID as mgiID, a.numericPart
        into temporary table markers
        from MRK_Marker m, ACC_Accession a
        where m._Marker_Type_key = 1
        and m._Marker_Status_key = 1
        and m.name !~ 'gene model %'
        and m.symbol !~ '[A-Z][0-9][0-9][0-9][0-9][0-9]'
        and m.symbol !~ '[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]'
        and m.symbol !~ 'Gt(ROSA)26Sor'
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
db.sql('create index markers_idx1 on markers(_Marker_key)', None)

##

db.sql('''select distinct m.*, r._Refs_key, r.pubmedID
        into temporary table references1
        from markers m , MRK_Reference r
        where m._Marker_key = r._Marker_key
        ''', None)
db.sql('create index index_refs1_key on references1(_Refs_key)', None)

db.sql('''select r.*, b.mgiID as refID, b.short_citation
        into temporary table references2
        from references1 r, BIB_Citation_Cache b
        where r._Refs_key = b._Refs_key
        ''', None)
db.sql('create index index_refs_key on references2(_Refs_key)', None)

# yes if reference has be indexed/chosen for gxd
results = db.sql('''
        select distinct r._Refs_key
        from references1 r, BIB_Workflow_Status s
        where r._Refs_key = s._Refs_key
        and s._Group_key = 31576665
        and s._Status_key in (31576673, 31576671, 31576674)
        and s.isCurrent = 1
        ''', 'auto')
gxd = []
for r in results:
        gxd.append(r['_Refs_key'])

# does gene have mouse model annotated to DO disease
results = db.sql('''select distinct m._Marker_key
        from markers m, MRK_DO_Cache o
        where m._Marker_key = o._Marker_key
        ''', 'auto')
dolookup = []
for r in results:
        dolookup.append(r['_Marker_key'])

#
# fpD
#

db.sql('''select distinct r._Marker_key, r._Refs_key, r.symbol, r.name, r.mgiID,
        r.refID, r.numericPart, r.pubmedID
        into temporary table fpD
        from references2 r, BIB_Workflow_Status s
        where r._Refs_key = s._Refs_key
        and s._Group_key = 31576666 -- GO
        and s._Status_key in (31576673, 31576671) -- indexed, chosen
        and s.isCurrent = 1
        and not exists (select 1 from VOC_Evidence e, VOC_Annot a
        where r._Refs_key = e._Refs_key
        and e._Annot_key = a._Annot_key
        and a._AnnotType_key = 1000)
        and not exists (select 1 from BIB_Workflow_Tag wt
        where wt._Refs_key = r._Refs_key
        and wt._Tag_key = 71460412)
        ''', None)
# number of unique MGI gene
results = db.sql('select distinct _Marker_key from fpD', 'auto')

fpD.write('Number of unique MGI Gene IDs:  %s\n' % (len(results)))

# number of unique J:gene
results = db.sql('select distinct _Refs_key from fpD', 'auto')
fpD.write('Number of unique J: IDs:  %s\n' % (len(results)))

# total number of rows
results = db.sql('select * from fpD', 'auto')
fpD.write('Total number of rows:  %s\n\n' % (len(results)))
fpD.write('"Ref in GXD" column = "Y" if GXD current status is "chosen", "indexed" or "full-coded"\n\n')

fpD.write('ref ID' + TAB + \
         'pubMed ID' + TAB + \
         'ref in GXD?' + TAB + \
         'mgi ID' + TAB + \
         'symbol' + TAB + \
         'name' + TAB + \
         'DO' + TAB + \
         'Curator Tag' + CRT*2)

results = db.sql('select * from fpD order by numericPart', 'auto')
for r in results:
        writeRecordD(fpD, r)

#
# report 2E
#

# select genes with DO Associations
# feature type = 'protein coding genes'

db.sql('''select m._Marker_key, m.symbol, a.accID as mgiID, a.numericPart 
        into temporary table domarkers
        from MRK_Marker m, ACC_Accession a, VOC_Annot tdc
        where m._Organism_key = 1
        and m._Marker_Type_key = 1
        and m._Marker_Status_key = 1
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
        and a._AnnotType_key in (1020))''', None)
db.sql('create index do_idx1 on domarkers(_Marker_key)', None)

#
# select markers with DO annotations and either only IEA GO annotations or no GO annotations
#

db.sql('''select o.*, 'yes' as isGO
        into temporary table fpE
        from domarkers o, markers m
        where o._Marker_key = m._Marker_key
        union
        select o.*, 'no' as isGO
        from domarkers o
        where not exists 
          (select 1 from VOC_Annot a where o._Marker_key = a._Object_key and a._AnnotType_key = 1000)
        ''', None)

# number of unique MGI gene
results = db.sql('select distinct _Marker_key from fpE', 'auto')
fpE.write('Number of unique MGI Gene IDs:  %s\n' % (len(results)))

# total number of rows
results = db.sql('select * from fpE', 'auto')
fpE.write('Total number of rows:  %s\n\n' % (len(results)))

fpE.write('mgi ID' + TAB + \
         'symbol' + TAB + \
         'GO?' + CRT*2)

results = db.sql('select * from fpE order by symbol', 'auto')
for r in results:
    writeRecordF(fpE, r)

reportlib.finish_nonps(fpD, isHTML = 1)	# non-postscript file
reportlib.finish_nonps(fpE)	# non-postscript file
