'''
#
# TR 9555
#
# Report:
#
# Please see the body of TR9555 for details, the description is too long to list here.
#
# Usage:
#       GO_Combined_Report.py
#
# History:
#
# lec   12/15/2023
#       wts2-1155/GOC taking over GOA mouse, GOA human, etc.
#       changed Yes/No per Karen's instructions
#       fixed DO/Genotype, DO/Human Marker counts
#
# sc    02/11/2021
#       TR13349 - B39 project. Update to use alliance direct homology
#
# 04/09/2012	lec
#	- and m.name not like 'predicted gene %'
#	changed to
#	- and m.name not like 'predicted gene%'
#
# 04/03/2012	lec
#	- fixed up some nameing issues ('go' -> 'GO')
#
# 12/21/2011	lec
#	- convert to outer join
#
# mhall	04/01/2009
#	- TR 9555- created
#
#
'''
 
import sys 
import os 
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

isCompleteYes = 'has annotation reviewed date'
isCompleteNo = 'no annotation reviewed date'
hasAllelesYes = 'has allele(s)'
hasAllelesNo = 'no alleles'
hasDOYes = 'has DO genotype annotation(s)'
hasDONo = 'no DO genotype annotations'
hasDOHumanYes = 'has DO human annotation(s)'
hasDOHumanNo = 'no DO human annotations'
hasOrthoogYes = 'has rat/human ortholog(s)'
hasOrthologNo = 'no rat/human orthologs'

def setPrintYesNo(r):
        #
        # print names based on Yes or No
        #

        if r['isComplete'] == 'Yes': 
                r['isComplete'] = isCompleteYes
        else: 
                r['isComplete'] = isCompleteNo

        if r['hasAlleles'] == 'Yes': 
                r['hasAlleles'] = hasAllelesYes
        else: 
                r['hasAlleles'] = hasAllelesNo

        if r['hasDO'] == 'Yes': 
                r['hasDO'] = hasDOYes
        else: 
                r['hasDO'] = hasDONo

        if r['hasHumanDO'] == 'Yes': 
                r['hasHumanDO'] = hasDOHumanYes
        else: 
                r['hasHumanDO'] = hasDOHumanNo

        if r['hasOrtholog'] == 'Yes': 
                r['hasOrtholog'] = hasOrthoogYes 
        else: 
                r['hasOrtholog'] = hasOrthologNo

        return r

#
# Main
#

# The main report
fp = reportlib.init(sys.argv[0], 'GO Combined Report', os.environ['QCOUTPUTDIR'])

# The secondary report, just the No GO Section
fp2 = reportlib.init('GO_MRK_NoGO', 'Marker No GO', os.environ['QCOUTPUTDIR'])

# The third report, the no go section that has been filtered down to just alleles
fp3 = reportlib.init('GO_MRK_NoGO_Has_Alleles', 'Marker No GO w/ Alleles', os.environ['QCOUTPUTDIR'])

# Type Mapping Strings
template = "%s" + TAB
type1 = "No GO"
type2 = "ND Only"
type3 = "IEA Only"
type4 = "ND+IEA"
type5 = "Others"

# markers of type gene, status = officieal
# sequence XP or NP
db.sql('''
        select distinct m.* 
        into temporary table validMarkers
        from MRK_Marker m, SEQ_Marker_Cache smc
        where m._Marker_Type_key = 1
        and m._Marker_Status_key = 1
        and m._Organism_key = 1
        and m._Marker_key = smc._Marker_key
        and (smc.accID like 'XP%' or smc.accID like 'NP%' 
        or smc._logicalDB_key in (13, 41)) 
        ''', None)
db.sql('create index vmIndex3 on validMarkers (_Marker_key)', None)

#  mrkAlleles = alleles count -> markers table
db.sql('''
        select mm._Marker_key, count(_Allele_key) as hasAlleles
        into temporary table mrkAlleles
        from validMarkers mm
             LEFT OUTER JOIN ALL_Allele aa on (mm._Marker_key = aa._Marker_key
        and aa.isWildType = 0 
        and aa._Allele_Type_key != 847130
        and aa._Allele_Status_key = 847114
        and aa.isWildType = 0
        and aa._Transmission_key != 3982953)
        group by mm._Marker_key
        ''', None)
db.sql('create index mrkAlleleIndex on mrkAlleles (_Marker_key)', None)

# mrkDOAnnot = mrk/DO annotations table
db.sql('''
        select m._Marker_key, count(vmc._Term_key) as hasDO
        into temporary table mrkDOAnnot
        from validMarkers m
             LEFT OUTER JOIN VOC_Annot vmc on (m._Marker_key = vmc._Object_key
                 and vmc._AnnotType_key = 1020)
        group by m._Marker_key
        ''', None)
db.sql('create index mrkDOIndex on mrkDOAnnot (_Marker_key)', None)

# mrkDOHumanAnnot = mrk human -> mouse orthologs relationship
db.sql('''
        WITH vocabmh AS (
                select mm._Marker_key, v._Term_key
                from validMarkers mm, MRK_Cluster mc, MRK_ClusterMember mh, MRK_ClusterMember hh, MRK_Marker hm, VOC_Annot v
                where mc._ClusterSource_key = 75885739
                and mc._Cluster_key = mh._Cluster_key
                and mh._Cluster_key = hh._Cluster_key
                and mh._Marker_key = mm._Marker_key
                and hh._Marker_key = hm._Marker_key
                and mm._Organism_key = 1
                and hm._Organism_key = 2
                and hm._Marker_key = v._Object_key
                and v._AnnotType_key = 1022
        )
        select m._Marker_key, count(vmh._Term_key) as hasDOHuman
        into temporary table mrkDOHumanAnnot
        from validMarkers m
             LEFT OUTER JOIN vocabmh vmh on (m._Marker_key = vmh._Marker_key)
        group by m._Marker_key
        ''', None)
db.sql('create index mrkDOHumanIndex on mrkDOHumanAnnot (_Marker_key)', None)

# tmp_homology, mrkHomology = the marker has orthologs table
db.sql('''
        select mm._Marker_key, count(hm._Marker_key) as hasOrtholog
        into temporary table tmp_homology
        from MRK_Cluster mc, MRK_ClusterMember mh, MRK_ClusterMember hh,
                validMarkers mm, MRK_Marker hm
        where mc._ClusterSource_key = 75885739
        and mc._Cluster_key = mh._Cluster_key
        and mh._Cluster_key = hh._Cluster_key
        and mh._Marker_key = mm._Marker_key
        and hh._Marker_key = hm._Marker_key
        and mm._Organism_key = 1
        and hm._Organism_key in (2, 40)
        group by (mm._Marker_key)
        ''', None)

db.sql('''
        select m._Marker_key, t.hasOrtholog as hasOrtholog
        into temporary table mrkHomology
        from validMarkers m
             LEFT OUTER JOIN tmp_homology t on (m._Marker_key = t._Marker_key)
       ''', None)
db.sql('create index mrkOrthoIndex on mrkHomology (_Marker_key)', None)

# reduced_bibgo, refGOUnused = number of unused go references per marker
db.sql('''
        select r.*
        into temporary table reduced_bibgo
        from BIB_GOXRef_View r, validMarkers vm
        where r._Marker_key = vm._Marker_key
        ''', None)
db.sql('create index vmIndex2 on reduced_bibgo (_Marker_key)', None)

db.sql('''
        select vm._Marker_key, count(r._Refs_key) as goRefcount
        into temporary table refGOUnused
        from validMarkers vm
             LEFT OUTER JOIN reduced_bibgo r on (vm._Marker_key = r._Marker_key
        and not exists (select 1 from
                VOC_Annot a, VOC_Evidence e
                where a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key
                and e._Refs_key = r._Refs_key))
        group by vm._Marker_key 
        ''', None)
db.sql('create index goRefIndex on refGOUnused (_Marker_key)', None)

# goOverall = collapse all these temp tables down to a single one, to make the subsequent queries easier to design.
db.sql('''
        select m._Marker_key,
        case when gt.completion_date is not null then 'Yes' else 'No' end as isComplete,
        case when ma.hasAlleles > 0 then 'Yes' else 'No' end as hasAlleles,
        case when moa.hasDO > 0 then 'Yes' else 'No' end as hasDO,
        case when moha.hasDOHuman > 0 then 'Yes' else 'No' end as hasHumanDO,
        case when mho.hasOrtholog > 0 then 'Yes' else 'No' end as hasOrtholog,
        rgs.goRefcount 
        into temporary table goOverall
        from validMarkers m
             LEFT OUTER JOIN GO_Tracking gt on (m._Marker_key = gt._Marker_key),
             mrkAlleles ma, mrkDOAnnot moa, 
             refGOUnused rgs, mrkDOHumanAnnot moha, mrkHomology mho
        where m._Marker_key = ma._Marker_key
        and m._Marker_key = moa._Marker_key
        and m._Marker_key = mho._Marker_key
        and m._Marker_key = rgs._Marker_key
        and m._Marker_key = moha._Marker_key
        ''', None)
db.sql('create index goOverall_idx on goOverall (_Marker_key)', None)

# markers w/o GO evidence codes
resultsNoGO = db.sql('''
        select distinct '1' as type, m.symbol, a.accID as mgiID, m.name,
                g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, 
                g.goRefcount
        from validMarkers m, ACC_Accession a, goOverall g
        where m._Marker_key = a._Object_key
        and a._MGIType_key = 2
        and a._LogicalDB_key = 1
        and a.prefixPart = 'MGI:'
        and a.preferred = 1
        and m._Marker_key = g._Marker_key
        and not exists (select 1 from  VOC_Annot a, VOC_Evidence e
                where m._Marker_key = a._Object_key
                and a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key)
        ''', 'auto') 
noGOCount = len(resultsNoGO)
        
db.sql('''
        select distinct '1' as type, m.symbol, a.accID as mgiID, m.name,
                g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, 
                g.goRefcount, m._Marker_key
        into temporary table hasNoGO
        from validMarkers m, ACC_Accession a, goOverall g
        where m._Marker_key = a._Object_key
        and a._MGIType_key = 2 
        and a._LogicalDB_key = 1
        and a.prefixPart = 'MGI:'
        and a.preferred = 1
        and m._Marker_key = g._Marker_key
        and not exists (select 1 from  VOC_Annot a, VOC_Evidence e
                where m._Marker_key = a._Object_key
                and a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key)
        ''', None)

# markers with ND Only
resultsNDOnly = db.sql('''
        select distinct '2' as type, m.symbol, a.accID as mgiID, m.name,
                g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, g.goRefcount
        from validMarkers m, ACC_Accession a, VOC_Annot a2, voc_evidence e2, voc_term vt, goOverall g
        where m._Marker_key = a._Object_key
        and a._MGIType_key = 2
        and a._LogicalDB_key = 1
        and a.prefixPart = 'MGI:'
        and a.preferred = 1
        and m._Marker_key = a2._Object_key and a2._AnnotType_key = 1000 and a2._Annot_key = e2._Annot_key
        and e2._EvidenceTerm_key = vt._Term_key and vt._Vocab_key = 3
        and m._Marker_key = g._Marker_key
        and exists (select 1 from  VOC_Annot a, VOC_Evidence e
                where m._Marker_key = a._Object_key
                and a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key
                and e._EvidenceTerm_key = 118)
        and not exists (select 1 from  VOC_Annot a, VOC_Evidence e
                where m._Marker_key = a._Object_key
                and a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key
                and e._EvidenceTerm_key != 118)
        ''', 'auto')
NDOnlyCount = len(resultsNDOnly[0])

# markers with IEA Only
resultsIEAOnly = db.sql('''
        select distinct '3' as type, m.symbol, a.accID as mgiID, m.name,
                g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, g.goRefcount
        from validMarkers m, ACC_Accession a, VOC_Annot a2, voc_evidence e2, voc_term vt, goOverall g
        where m._Marker_key = a._Object_key
        and a._MGIType_key = 2
        and a._LogicalDB_key = 1
        and a.prefixPart = 'MGI:'
        and a.preferred = 1
        and m._Marker_key = a2._Object_key and a2._AnnotType_key = 1000
        and a2._Annot_key = e2._Annot_key
        and e2._EvidenceTerm_key = vt._Term_key and vt._Vocab_key = 3
        and m._Marker_key = g._Marker_key
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
        ''', 'auto')
IEAOnlyCount = len(resultsIEAOnly[0])

# markers with IEA + ND
resultsIEAAndNDOnly = db.sql('''
        select distinct '4' as type, m.symbol, a.accID as mgiID, m.name,
                g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, g.goRefcount
        from MRK_Marker m, ACC_Accession a, VOC_Annot a2, voc_evidence e2, voc_term vt, goOverall g
        where m._Marker_key = a._Object_key
        and a._MGIType_key = 2
        and a._LogicalDB_key = 1
        and a.prefixPart = 'MGI:'
        and a.preferred = 1
        and m._Marker_key = a2._Object_key and a2._AnnotType_key = 1000
        and a2._Annot_key = e2._Annot_key
        and e2._EvidenceTerm_key = vt._Term_key and vt._Vocab_key = 3
        and m._Marker_key = g._Marker_key
        and exists (select 1 from  VOC_Annot a, VOC_Evidence e
                where m._Marker_key = a._Object_key
                and a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key
                and e._EvidenceTerm_key = 115)
        and exists (select 1 from  VOC_Annot a, VOC_Evidence e
                where m._Marker_key = a._Object_key
                and a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key
                and e._EvidenceTerm_key = 118)
        and not exists (select 1 from  VOC_Annot a, VOC_Evidence e
                where m._Marker_key = a._Object_key
                and a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key
                and e._EvidenceTerm_key not in (115, 118))
        ''', 'auto')
IEAAndNDOnlyCount = len(resultsIEAAndNDOnly[0])

# markers with all other annotations
resultsAllOther = db.sql('''
        select distinct '5' as type, m.symbol, a.accID as mgiID, m.name,
                g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, g.goRefcount
        from MRK_Marker m, ACC_Accession a, VOC_Annot a2, voc_evidence e2, voc_term vt, goOverall g
        where m._Marker_key = a._Object_key
        and a._MGIType_key = 2
        and a._LogicalDB_key = 1
        and a.prefixPart = 'MGI:'
        and a.preferred = 1
        and m._Marker_key = a2._Object_key and a2._AnnotType_key = 1000
        and a2._Annot_key = e2._Annot_key
        and e2._EvidenceTerm_key = vt._Term_key and vt._Vocab_key = 3
        and m._Marker_key = g._Marker_key
        and exists (select 1 from  VOC_Annot a, VOC_Evidence e
                where m._Marker_key = a._Object_key
                and a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key)
        and exists (select 1 from  VOC_Annot a, VOC_Evidence e
                where m._Marker_key = a._Object_key
                and a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key
                and e._EvidenceTerm_key not in (115, 118))
        ''', 'auto')	
otherCount = len(resultsAllOther[0])

# Print out the descriptive information about the genes

fp.write("Genes in this report are of type 'Gene', are for the mouse, and do not have a 'withdrawn' status.\n")
fp.write("Additionally they have had the following restrictions placed on them:\n")
fp.write("They must have a protein sequence of type Uniprot, XP or NP \n\n")
        
# Print out the Header

totalCount = noGOCount + NDOnlyCount + IEAOnlyCount + IEAAndNDOnlyCount + otherCount

fp.write("1. Total number of rows: %d" % totalCount)
fp.write(CRT + "2. Genes with no GO Annotations: %d" % noGOCount)

# The second report also needs this line, so print it out.
fp2.write(CRT + "1. Genes with no GO Annotations: %d" % noGOCount)

fp.write(CRT + "3. Genes with Annotations to IEA Only: %d" % IEAOnlyCount)
fp.write(CRT + "4. Genes with Annotations to ND Only: %d" % NDOnlyCount)
fp.write(CRT + "5. Genes with Annotations to ND+IEA: %d" % IEAAndNDOnlyCount)
fp.write(CRT + "6. Genes with Annotations to All other: %d" % otherCount)

# Gather all of the other statistical data.
results = db.sql('''
        select count(go._Marker_key) as cnt from goOverall go, hasNoGO hng
        where go.hasOrtholog = 'Yes' and go._Marker_key = hng._Marker_key 
        ''', 'auto')
for r in results:
    rhHomologsYes = r['cnt']
fp.write(CRT + "7. Mouse Genes that have Rat/Human Homologs and NO GO annotations: %d" % rhHomologsYes)

# Count of markers with human disease annotations
results = db.sql('''
        select count(go._Marker_key) as cnt from goOverall go, hasNoGO hng
        where go.hasHumanDO = 'Yes' and go._Marker_key = hng._Marker_key 
        ''', 'auto')
for r in results:
    doGenoYes = r['cnt']
fp.write(CRT + "8. Mouse Genes with Human Disease Annotations and NO GO annotations: %d" % doGenoYes)

# Count of markers that have alleles	
results = db.sql('''
        select count(distinct go._Marker_key) as cnt from goOverall go, hasNoGO hng
        where go.hasAlleles = 'Yes' and go._Marker_key = hng._Marker_key
        ''', 'auto')	
for r in results:
    allelesYes = r['cnt']
fp.write(CRT + "9. Genes with Mutant Alleles and NO GO Annotations: %d" % allelesYes)

# Count of markers marked complete in go	
results = db.sql('''
        select count(_Marker_key) as cnt from goOverall
        where isComplete = 'Yes' 
        ''', 'auto')
for r in results:
    completeYes = r['cnt']
fp.write(CRT + "10. Genes with GO Annotation reviewed date?: %d" % completeYes)

# Count of unique references for all markers.
results = db.sql('select sum(goRefcount) as cnt from goOverall', 'auto')
for r in results:
    uniqueRef = r['cnt']
fp.write(CRT + "11. Total number of unique references: %d" % uniqueRef)

# template for rows in the report
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

# other two reports do not need the template section, so we can remove them.
templateRow2 = '%s' + TAB + \
        '%s' + TAB + \
        '%s' + TAB + \
        '%s' + TAB + \
        '%s' + TAB + \
        '%s' + TAB + \
        '%s' + TAB + \
        '%s' + TAB + \
        '%s' + CRT;

# first report
fp.write(3*CRT + 'GO Status' + TAB + \
        'Gene Symbol' + TAB + \
        'MGI ID' + TAB + \
        'Gene Name' + TAB + \
        'Rat/Human Orthologs?' + TAB + \
        'DO Genotype Annotations?' + TAB + \
        'DO Human Annotations?' + TAB + \
        'Alleles?' + TAB + \
        'Annotation reviewed date?' + TAB + \
        'Number of GO References' + CRT)

# second report
fp2.write(3*CRT + 
        'Gene Symbol' + TAB + \
        'MGI ID' + TAB + \
        'Gene Name' + TAB + \
        'Rat/Human Orthologs?' + TAB + \
        'DO Genotype Annotations?' + TAB + \
        'DO Human Annotations?' + TAB + \
        'Alleles?' + TAB + \
        'Annotation reviewed date?' + TAB + \
        'Number of GO References' + CRT)

# third report also needs this line, so print it out.
fp3.write(CRT + "1. Genes with Mutant Alleles and NO GO Annotations: %d" % allelesYes)
fp3.write(3*CRT +
        'Gene Symbol' + TAB + \
        'MGI ID' + TAB + \
        'Gene Name' + TAB + \
        'Rat/Human Orthologs?' + TAB + \
        'DO Genotype Annotations?' + TAB + \
        'DO Human Annotations?' + TAB + \
        'Alleles?' + TAB + \
        'Annotation reviewed date?' + TAB + \
        'Number of GO References' + CRT)
        
for r in resultsNoGO:

    r = setPrintYesNo(r)

    fp.write(templateRow % (type1, r['symbol'], r['mgiID'], r['name'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefcount'])))
    
    # Report #2 needs a copy of this
    fp2.write(templateRow2 % (r['symbol'], r['mgiID'], r['name'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefcount'])))
    
    # Report #3 needs a copy of this, if they have alleles.
    if r['hasAlleles'] == hasAllelesYes:
        fp3.write(templateRow2 % (r['symbol'], r['mgiID'], r['name'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefcount'])))
        
for r in resultsNDOnly:
    r = setPrintYesNo(r)
    fp.write(templateRow % (type2, r['symbol'], r['mgiID'], r['name'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefcount'])))	

for r in resultsIEAOnly:
    r = setPrintYesNo(r)
    fp.write(templateRow % (type3, r['symbol'], r['mgiID'], r['name'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefcount'])))	
    
for r in resultsIEAAndNDOnly:
    r = setPrintYesNo(r)
    fp.write(templateRow % (type4, r['symbol'], r['mgiID'], r['name'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefcount'])))	
    
for r in resultsAllOther:
    r = setPrintYesNo(r)
    fp.write(templateRow % (type5, r['symbol'], r['mgiID'], r['name'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefcount'])))    

reportlib.finish_nonps(fp)

