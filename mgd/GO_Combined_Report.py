#!/usr/local/bin/python

'''
#
# TR 9555
#
# Report:
#
# Please see the body of TR9555 for details, the description is too long to list here.
#
#
# Usage:
#       GO_Combined_Report.py
#
# Notes:
#
# History:
#
# mhall	04/01/2009
#	- TR 9555- created
#
#
'''
 
import sys 
import os 
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

db.useOneConnection(1)

fp = reportlib.init(sys.argv[0], 'Go Combined Report', os.environ['QCOUTPUTDIR'])

# Type Mapping Strings

template = "%s" + TAB + "%s" + TAB + "%s" + TAB + "%s" + TAB + "%s"

type1 = template % ("X"," "," "," "," ")
type2 = template % (" ","X"," "," "," ")
type3 = template % (" "," ","X"," "," ")
type4 = template % (" "," "," ","X"," ")
type5 = template % (" "," "," "," ","X")


# Reduce the total list of markers that we need to compare against w/ a filter versus the
# marker table.

cmds = []

cmds.append('select m.* ' + \
	'into #validMarkers ' + \
	'from mrk_marker m ' + \
	'where  m._Marker_Type_key = 1 ' + \
	'and m._Marker_Status_key in (1,3) ' + \
	'and m.name not like "gene model %" ' + \
	'and m.symbol not like "[A-Z][0-9][0-9][0-9][0-9][0-9]" ' + \
	'and m.symbol not like "[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]" ' + \
	'and m.symbol not like "ORF%" ' + \
	'and m._Organism_key = 1')

cmds.append('create index vmIndex on #validMarkers (_Marker_key)')

results = db.sql(cmds,'auto')

# Setup the alleles count -> markers table

cmds = []

cmds.append('select mm._Marker_key, count(_Allele_key) as "hasAlleles" ' + \
	'into #mrkAlleles ' + \
	'from all_allele aa, #validMarkers mm ' + \
	'where mm._Marker_key *= aa._Marker_key ' + \
	'group by mm._Marker_key')

cmds.append('create index mrkAlleleIndex on #mrkAlleles (_Marker_key)')

results = db.sql(cmds,'auto')

# setup the mrk Omim annotations table

cmds = []

cmds.append('select m._Marker_key, count(vmc._Term_key) as "hasOmim" ' + \
	'into #mrkOmimAnnot ' + \
	'from VOC_Marker_Cache vmc, #validMarkers m ' + \
	'where m._Marker_key *= vmc._Marker_key ' + \
	'and annotType = "OMIM/Genotype" ' + \
	'group by m._Marker_key')

cmds.append('create index mrkOmimIndex on #mrkOmimAnnot (_Marker_key)')
results = db.sql(cmds,'auto')

# Setup the mrk human -> mouse orthologs relationship

cmds = []

cmds.append('select m._Marker_key, count(vmc._Term_key) as "hasOmimHuman" ' + \
	'into #mrkOmimHumanAnnot ' + \
	'from VOC_Marker_Cache vmc, #validMarkers m ' + \
	'where m._Marker_key *= vmc._Marker_key ' + \
	'and annotType = "OMIM/Human Marker" ' + \
	'group by m._Marker_key')

cmds.append('create index mrkOmimHumanIndex on #mrkOmimHumanAnnot (_Marker_key)')
results = db.sql(cmds,'auto')

# Set up the marker has orthologs table

cmds = []

cmds.append('select mm._Marker_key, ' + \
	'count(hm._Marker_key) as "hasOrtholog" ' + \
	'into #tmp_homology ' + \
	'from MRK_Homology_Cache mh, MRK_Homology_Cache hh, ' + \
	'#validMarkers mm, MRK_Marker hm ' + \
	'where mh._Class_key = hh._Class_key ' + \
	'and hm._Marker_key = hh._Marker_key ' + \
	'and mh._Marker_key = mm._Marker_key ' + \
	'and mh._Organism_key = 1 ' + \
	'and hh._Organism_key in (2, 40) ' + \
	'group by (mm._Marker_key)')

cmds.append('select m._Marker_key, count(t.hasOrtholog) as "hasOrtholog" ' + \
	'into #mrkHomology ' + \
	'from #validMarkers m, #tmp_homology t ' + \
	'where m._Marker_key *= t._Marker_key')

cmds.append('create index mrkOrthoIndex on #mrkHomology (_Marker_key)')
results = db.sql(cmds,'auto')

# Get the number of unused go references per marker

cmds = []

cmds.append('select r.* ' +\
	'into #reduced_bibgo ' +\
	'from BIB_GOXRef_View r, #validMarkers vm ' +\
	'where r._Marker_key = vm._Marker_key')

cmds.append('create index vmIndex on #reduced_bibgo (_Marker_key)')

cmds.append('select vm._Marker_key, count(r._Refs_key) as "goRefcount" ' +\
	'into #refGoUnused ' +\
	'from #reduced_bibgo r, #validMarkers vm ' +\
	'where vm._Marker_key *= r._Marker_key ' +\
	'and not exists (select 1 from ' +\
	'VOC_ANNOT a, VOC_EVIDENCE e ' +\
	'where a._AnnotType_key = 1000 ' +\
	'and a._Annot_key = e._Annot_key ' +\
	'and e._Refs_key = r._Refs_key) ' +\
	'group by vm._Marker_key ')

cmds.append('create index goRefIndex on #refGoUnused (_Marker_key)')

results = db.sql(cmds,'auto')

# Collapse all these temp tables down to a single one, to make the subsequent queries easier
# to design.

cmds = []

cmds.append('select m._Marker_key, ' + \
	'case when gt.completion_date != null then "Yes" else "No" end as "isComplete", ' + \
	'case when ma.hasAlleles > 0 then "Yes" else "No" end as "hasAlleles", ' + \
	'case when moa.hasOmim > 0 then "Yes" else "No" end as "hasOmim", ' + \
	'case when moha.hasOmimHuman > 0 then "Yes" else "No" end as "hasHumanOmim", ' + \
	'case when moa.hasOmim > 0 then "Yes" else "No" end as "hasOrtholog", ' + \
	'rgs.goRefcount ' + \
	'into #goOverall ' + \
	'from #validMarkers m, GO_Tracking gt, #mrkAlleles ma, #mrkOmimAnnot moa, ' + \
	'#mrkHomology mh, #refGoUnused rgs, #mrkOmimHumanAnnot moha ' + \
	'where m._Marker_key = ma._Marker_key ' + \
	'and m._Marker_key *= gt._Marker_key ' + \
	'and m._Marker_key = moa._Marker_key ' + \
	'and m._Marker_key = mh._Marker_key ' + \
	'and m._Marker_key = rgs._Marker_key ' + \
	'and m._Marker_key = moha._Marker_key')

cmds.append('create index goOverall on #goOverall (_Marker_key)')
results = db.sql(cmds,'auto')

# Markers w/o Go Evidence Codes

cmds = []

cmds.append('select distinct "1" as type, m.symbol, mgiID = a.accID, m.name, ' + \
	'g.isComplete, g.hasAlleles, g.hasOmim, g.hasHumanOmim, g.hasOrtholog, g.goRefcount ' + \
	'from #validMarkers m, ACC_Accession a, #goOverall g  ' + \
	'where m._Marker_key = a._Object_key  ' + \
	'and a._MGIType_key = 2  ' + \
	'and a._LogicalDB_key = 1  ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1  ' + \
	'and m._Marker_key = g._Marker_key ' + \
	'and not exists (select 1 from  VOC_Annot a, VOC_Evidence e  ' + \
	'where m._Marker_key = a._Object_key  ' + \
	'and a._AnnotType_key = 1000  ' + \
	'and a._Annot_key = e._Annot_key)') 

resultsNoGo = db.sql(cmds,'auto')
noGoCount = len(resultsNoGo[0])

# Markers with ND Only

cmds = []

cmds.append('select distinct "2" as type, m.symbol, mgiID = a.accID, m.name,  ' + \
	'g.isComplete, g.hasAlleles, g.hasOmim, g.hasHumanOmim, g.hasOrtholog, g.goRefcount ' + \
	'from #validMarkers m, ACC_Accession a, voc_annot a2, ' + \
	'voc_evidence e2, voc_term vt, #goOverall g ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1 ' + \
	'and m._Marker_key = a2._Object_key and a2._AnnotType_key = 1000 and a2._Annot_key = e2._Annot_key ' + \
	'and e2._EvidenceTerm_key = vt._Term_key and vt._Vocab_key = 3 ' + \
	'and m._Marker_key = g._Marker_key ' + \
	'and exists (select 1 from  VOC_Annot a, VOC_Evidence e ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._EvidenceTerm_key = 118) ' + \
	'and not exists (select 1 from  VOC_Annot a, VOC_Evidence e ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._EvidenceTerm_key != 118)')
	
resultsNDOnly = db.sql(cmds,'auto')	
NDOnlyCount = len(resultsNDOnly[0])

# Markers with IEA Only

cmds = []

cmds.append('select distinct "3" as type, m.symbol, mgiID = a.accID, m.name, ' + \
	'g.isComplete, g.hasAlleles, g.hasOmim, g.hasHumanOmim, g.hasOrtholog, g.goRefcount ' + \
	'from #validMarkers m, ACC_Accession a, voc_annot a2, ' + \
	'voc_evidence e2, voc_term vt, #goOverall g ' + \
	'where m._Marker_key = a._Object_key  ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1 ' + \
	'and m._Marker_key = a2._Object_key and a2._AnnotType_key = 1000 ' + \
	'and a2._Annot_key = e2._Annot_key ' + \
	'and e2._EvidenceTerm_key = vt._Term_key and vt._Vocab_key = 3 ' + \
	'and m._Marker_key = g._Marker_key ' + \
	'and exists (select 1 from  VOC_Annot a, VOC_Evidence e ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._EvidenceTerm_key = 115) ' + \
	'and not exists (select 1 from  VOC_Annot a, VOC_Evidence e ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._EvidenceTerm_key != 115)')

resultsIEAOnly = db.sql(cmds,'auto')
IEAOnlyCount = len(resultsIEAOnly[0])

# Markers with IEA + ND

cmds = []

cmds.append('select distinct "4" as type, m.symbol, mgiID = a.accID, m.name, ' + \
	'g.isComplete, g.hasAlleles, g.hasOmim, g.hasHumanOmim, g.hasOrtholog, g.goRefcount ' + \
	'from MRK_Marker m, ACC_Accession a, voc_annot a2, ' + \
	'voc_evidence e2, voc_term vt, #goOverall g ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1 ' + \
	'and m._Marker_key = a2._Object_key and a2._AnnotType_key = 1000 ' + \
	'and a2._Annot_key = e2._Annot_key ' + \
	'and e2._EvidenceTerm_key = vt._Term_key and vt._Vocab_key = 3 ' + \
	'and m._Marker_key = g._Marker_key ' + \
	'and exists (select 1 from  VOC_Annot a, VOC_Evidence e ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._EvidenceTerm_key = 115) ' + \
	'and exists (select 1 from  VOC_Annot a, VOC_Evidence e ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._EvidenceTerm_key = 118) ' + \
	'and not exists (select 1 from  VOC_Annot a, VOC_Evidence e ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._EvidenceTerm_key not in (115, 118))')
	
resultsIEAAndNDOnly = db.sql(cmds,'auto')
IEAAndNDOnlyCount = len(resultsIEAAndNDOnly[0])

# Markers with all other annotations

cmds = []
	
cmds.append('select distinct "5" as type, m.symbol, mgiID = a.accID, m.name, ' + \
	'g.isComplete, g.hasAlleles, g.hasOmim, g.hasHumanOmim, g.hasOrtholog, g.goRefcount ' + \
	'from MRK_Marker m, ACC_Accession a, voc_annot a2, ' + \
	'voc_evidence e2, voc_term vt, #goOverall g ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1 ' + \
	'and m._Marker_key = a2._Object_key and a2._AnnotType_key = 1000 ' + \
	'and a2._Annot_key = e2._Annot_key ' + \
	'and e2._EvidenceTerm_key = vt._Term_key and vt._Vocab_key = 3 ' + \
	'and m._Marker_key = g._Marker_key ' + \
	'and exists (select 1 from  VOC_Annot a, VOC_Evidence e ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key) ' + \
	'and exists (select 1 from  VOC_Annot a, VOC_Evidence e ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e._EvidenceTerm_key not in (115, 118))')	
	
resultsAllOther = db.sql(cmds,'auto')
otherCount = len(resultsAllOther[0])

# Gather all of the other statistical data.

cmds = []

# Total number of rows

cmds.append('select count(_Marker_key) as "count" from #goOverall ' + \
	'where hasOrtholog = "Yes"')

# Total number of unique markers (Same as above)

cmds.append('select count(_Marker_key) as "count" from #goOverall ' + \
	'where hasOrtholog = "No"')

# Count of markers with omim geno annotations

cmds.append('select count(_Marker_key) as "count" from #goOverall ' + \
	'where hasOmim = "Yes"')

# Count of markers w/0 omim geno annotations

cmds.append('select count(_Marker_key) as "count" from #goOverall ' + \
	'where hasOmim = "No"')

# Count of markers w/ omim human annotations
	
cmds.append('select count(_Marker_key) as "count" from #goOverall ' + \
	'where hasHumanOmim = "Yes"')

# Count of markers w/o omim human annotations

cmds.append('select count(_Marker_key) as "count" from #goOverall ' + \
	'where hasHumanOmim = "No"')	
	
# Count of markers that have alleles	
	
cmds.append('select count(_Marker_key) as "count" from #goOverall ' + \
	'where hasAlleles = "Yes"')

# Count of markers that w/o alleles

cmds.append('select count(_Marker_key) as "count" from #goOverall ' + \
	'where hasAlleles = "No"')		
	
# Count of markers marked complete in go	
	
cmds.append('select count(_Marker_key) as "count" from #goOverall ' + \
	'where isComplete = "Yes"')

# Count of markers not marked complete in go

cmds.append('select count(_Marker_key) as "count" from #goOverall ' + \
	'where isComplete = "No"')

# Total number of references unused for all markers
	
cmds.append('select sum(goRefcount) as "count" ' + \
	'from #goOverall')	

# Count of unique unused references for all markers.
	
cmds.append('select count(distinct jnum) as "count" from #reduced_bibgo')	

resultsStats = db.sql(cmds,'auto')
	
# Print out the Header

totalCount = noGoCount + NDOnlyCount + IEAOnlyCount + IEAAndNDOnlyCount + otherCount

fp.write("1. Total number of rows: %d" % totalCount)
fp.write(CRT + "2. Total number unique MGI IDs: %d" % totalCount)
fp.write(CRT + "3. Total no go Number: %d" % noGoCount)
fp.write(CRT + "4. IEA Only Number: %d" % IEAOnlyCount)
fp.write(CRT + "5. ND Only Number: %d" % NDOnlyCount)
fp.write(CRT + "6. ND+IEA Number: %d" % IEAAndNDOnlyCount)
fp.write(CRT + "7. All other Number: %d" % otherCount)

for r in resultsStats[0]:
    rhHomologsYes = r['count']
    
for r in resultsStats[1]:
    rhHomologsNo = r['count']
    

fp.write(CRT + "8. Rat/Human Homologs - yes Number: %d" % rhHomologsYes)
fp.write(CRT + "9. Rat/Human Homologs - no Number: %d" % rhHomologsNo)

for r in resultsStats[2]:
    omimGenoYes = r['count']
    
for r in resultsStats[3]:
    omimGenoNo = r['count']
    

fp.write(CRT + "10. OMIM Genotype Annotations - yes Number: %d" % omimGenoYes)
fp.write(CRT + "11. OMIM Genotype Annotations - no Number: %d" % omimGenoNo)

for r in resultsStats[4]:
    omimHumanYes = r['count']
    
for r in resultsStats[5]:
    omimHumanNo = r['count']
    

fp.write(CRT + "12. OMIM Human Annotations - yes Number: %d" % omimHumanYes)
fp.write(CRT + "13. OMIM Human Annotations - no Number: %d" % omimHumanNo)

for r in resultsStats[6]:
    allelesYes = r['count']
    
for r in resultsStats[7]:
    allelesNo = r['count']
    

fp.write(CRT + "14. Alleles - yes Number: %d" % allelesYes)
fp.write(CRT + "15. Alleles - no Number: %d" % allelesNo)

for r in resultsStats[8]:
    completeYes = r['count']
    
for r in resultsStats[9]:
    completeNo = r['count']
    

fp.write(CRT + "16. Annotation Complete - yes Number: %d" % completeYes)
fp.write(CRT + "17. Annotation Complete - no Number: %d" % completeNo)

for r in resultsStats[10]:
    totalRef = r['count']
    

fp.write(CRT + "18. Total number of references for all Rows - yes Number: %d" % totalRef)

for r in resultsStats[11]:
    uniqueRef = r['count']
    

fp.write(CRT + "19. Total number of unique references: %d" % uniqueRef)

# Setup the template for rows in the report

templateRow = '%s' + TAB + \
	'%s' + TAB + \
	'%s' + TAB + \
	'%s' + TAB + \
	'%s' + TAB + \
	'%s' + TAB + \
	'%s' + TAB + \
	'%s' + TAB + \
	'%s' + TAB + \
	'%s' + CRT;

# Print out the report itself

fp.write(CRT + CRT + CRT + 'No GO' + TAB + \
	'ND Only' + TAB + \
	'IEA Only' + TAB + \
	'ND+IEA' + TAB + \
	'Others' + TAB + \
	'Gene Symbol' + TAB + \
	'MGI ID' + TAB + \
	'Gene Name' + TAB + \
	'Rat/Human Orthologs?' + TAB + \
	'OMIM Genotype Annotations?' + TAB + \
	'OMIM Human Annotations?' + TAB + \
	'Alleles?' + TAB + \
	'Annotation Complete?' + TAB + \
	'Number of Go References' + CRT)

for r in resultsNoGo[0]:
    fp.write(templateRow % (type1, r['symbol'], r['mgiID'], r['name'], r['hasOrtholog'], r['hasOmim'], r['hasHumanOmim'], r['hasAlleles'], r['isComplete'], str(r['goRefcount'])))

for r in resultsNDOnly[0]:
    fp.write(templateRow % (type2, r['symbol'], r['mgiID'], r['name'], r['hasOrtholog'], r['hasOmim'], r['hasHumanOmim'], r['hasAlleles'], r['isComplete'], str(r['goRefcount'])))	

for r in resultsIEAOnly[0]:
    fp.write(templateRow % (type3, r['symbol'], r['mgiID'], r['name'], r['hasOrtholog'], r['hasOmim'], r['hasHumanOmim'], r['hasAlleles'], r['isComplete'], str(r['goRefcount'])))	
    
for r in resultsIEAAndNDOnly[0]:
    fp.write(templateRow % (type4, r['symbol'], r['mgiID'], r['name'], r['hasOrtholog'], r['hasOmim'], r['hasHumanOmim'], r['hasAlleles'], r['isComplete'], str(r['goRefcount'])))	
    
for r in resultsAllOther[0]:
    fp.write(templateRow % (type5, r['symbol'], r['mgiID'], r['name'], r['hasOrtholog'], r['hasOmim'], r['hasHumanOmim'], r['hasAlleles'], r['isComplete'], str(r['goRefcount'])))    


reportlib.finish_nonps(fp)

db.useOneConnection(0)
