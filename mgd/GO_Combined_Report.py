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
#       https://mgi-jira.atlassian.net/browse/FL2-644
#       per Karen Christie, we completely re-wrote this report
#               changed Yes/No per Karen's instructions
#               fixed DO/Genotype, DO/Human Marker counts
#               fixed counts at top (1-11)
#               removed exclusion of gene symbol/name checks
#               changed 5 fields (type1,2,3,4,5) -> one field/GO Status
#               added: field 5/feature type
#               added: field 6/predicted gene
#               added: "IBA Only" "ND+IBA" "ND+IBA+IEA"
#               added: feature type counts at top of each report
#               etc., etc., etc.
#
# sc    02/11/2021
#       TR13349 - B39 project. Update to use alliance direct homology
#
# mhall	04/01/2009
#	- TR 9555- created
#
'''
 
import sys 
import os 
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

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
'%s' + TAB + \
'%s' + TAB + \
'%s' + TAB + \
'%s' + TAB + \
'%s' + CRT;

# Type Mapping Strings
template = "%s" + TAB
type1 = "No GO"
type2 = "ND Only"
type3 = "IEA Only"
type4 = "ND+IEA"
type5 = "Others"
type6 = "IBA Only"
type7 = "ND+IBA"
type8 = "ND+IBA+IEA"
type9 = "has manual EXP"
type10 = "has HTP but no manual EXP"
type11 = "IBA+IEA"

# translate Yes/No to these field names
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
isPredictedGene = 'predicted gene'

def setPrintYesNo(r):
        #
        # print better Yes/No field names 
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

        if r['predictedGene'] == 'Yes':
                r['predictedGene'] = isPredictedGene
        else:
                r['predictedGene'] = 'gene'

        return r

def getMarkers():
        #
        # validMarkers : distinct set of markers used for all reports
        #
        # mouse markers of type gene, status = official
        #
        # if marker matches one of the criteria, then preditedGene = Yes
        #       name that starts with the words 'gene model'
        #       name that starts with the words 'predicted gene'
        #       name that starts with the words 'gene trap'
        #       symbol that starts with the word 'ORF'
        #       symbol that is a single letter followed by up to 5 numbers, for example 'a12345'
        #       symbol that is two letters followed by up to 5 numbers, for example 'ab12345'
        #
        # else predicatedGene = No
        #
        # exclude:
        #       feture type = "heritable phenotypic marker" : 6238170
        #
        #       markers we may need to add to exclude list:
        #       Gt(ROSA)26Sor    37270
        #

        db.sql('''
                WITH markers AS (
                        select distinct m.*, a.accID, t.term as featureType
                        from MRK_Marker m, ACC_Accession a, VOC_Annot va, VOC_Term t
                        where m._Marker_Type_key = 1
                        and m._Marker_Status_key = 1
                        and m._Organism_key = 1
                        and m._Marker_key = a._Object_key
                        and a._MGIType_key = 2
                        and a._LogicalDB_key = 1
                        and a.prefixPart = 'MGI:'
                        and a.preferred = 1
                        and m._Marker_key = va._Object_key
                        and va._AnnotType_key = 1011    -- MCV/Marker
                        and va._Term_key = t._Term_key
                        and t._term_key not in (6238170)
                        and m._Marker_key not in (37270)
                )
                select m.*, 'Yes' as predictedGene
                into temporary table validMarkers
                from markers m
                where m.name like 'gene model %'
                or m.name like 'gene trap %'
                or m.name like 'predicted gene%'
                or m.symbol like 'ORF%'
                or m.symbol ~ '[A-Z][0-9][0-9][0-9][0-9][0-9]'
                or m.symbol ~ '[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]'
                union
                select m.*, 'No' as predictedGene
                from markers m
                where m.name not like 'gene model %'
                and m.name not like 'gene trap %'
                and m.name not like 'predicted gene%'
                and m.symbol not like 'ORF%'
                and m.symbol !~ '[A-Z][0-9][0-9][0-9][0-9][0-9]'
                and m.symbol !~ '[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]'
                ''', None)

        db.sql('create index validMarkers_idx on validMarkers (_Marker_key)', None)

def getAlleles():
        #
        # mrkAlleles
        # Markers with Alleles where:
        #       Allele Status = Approved (847114)
        #       Allele Type != QTL (847130)
        #       Allele Transmission != Cell Line (3982953)
        #       Allele is not a wild type (0)
        #
        # LEFT OUTER JOIN required
        #

        db.sql('''
                select mm._Marker_key, count(_Allele_key) as hasAlleles
                into temporary table mrkAlleles
                from validMarkers mm
                LEFT OUTER JOIN ALL_Allele aa on (mm._Marker_key = aa._Marker_key
                        and aa.isWildType = 0
                        and aa._Allele_Status_key = 847114
                        and aa._Allele_Type_key != 847130
                        and aa.isWildType = 0
                        and aa._Transmission_key != 3982953
                        )
                group by mm._Marker_key
                ''', None)

        db.sql('create index mrkAlleles_idx on mrkAlleles (_Marker_key)', None)

def getMarkerDO():
        #
        # mrkDOAnnot = mrk/DO annotations table
        # Markers that contain DO/Genotype Annotations (1020)
        #
        # LEFT OUTER JOIN required
        #

        db.sql('''
                select m._Marker_key, count(vmc._Term_key) as hasDO
                into temporary table mrkDOAnnot
                from validMarkers m
                        LEFT OUTER JOIN VOC_Annot vmc on (m._Marker_key = vmc._Object_key and vmc._AnnotType_key = 1020)
                group by m._Marker_key
                ''', None)

        db.sql('create index mrkDOAnnot_idx on mrkDOAnnot (_Marker_key)', None)

def getOrthologs():
        #
        # mrkDOHumanAnnot = mrk human -> mouse orthologs relationship
        # Markers that contain Human ortholog
        # Human ortholog contains DO/Human annotation (1022)
        #
        # LEFT OUTER JOIN required
        #

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

        db.sql('create index mrkDOHumanAnnot_idx on mrkDOHumanAnnot (_Marker_key)', None)
        
        #
        # tmp_homology, mrkOrtholog = the marker has orthologs table
        # Markers that contain Human or Rat ortholog
        #
        # LEFT OUTER JOIN required
        #
        db.sql('''
                select mm._Marker_key, count(hm._Marker_key) as hasOrtholog
                into temporary table tmp_homology
                from MRK_Cluster mc, MRK_ClusterMember mh, MRK_ClusterMember hh, validMarkers mm, MRK_Marker hm
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
                into temporary table mrkOrtholog
                from validMarkers m
                        LEFT OUTER JOIN tmp_homology t on (m._Marker_key = t._Marker_key)
        ''', None)

        db.sql('create index mrkOrtholog_idx on mrkOrtholog (_Marker_key)', None)

def getRefs():

        #
        # reduced_bibgo, refGOUnused = number of unused go references per marker
        #
        db.sql('''
                select r.*
                into temporary table reduced_bibgo
                from BIB_GOXRef_View r, validMarkers vm
                where r._Marker_key = vm._Marker_key
                ''', None)

        db.sql('create index reduced_bibgo_idx on reduced_bibgo (_Marker_key)', None)

        #
        # number of unqiue references by marker not used by GO
        #
        db.sql('''
                (
                select vm._Marker_key, count(distinct r._Refs_key) as goRefUnusedCount
                into temporary table refGOUnused
                from validMarkers vm, reduced_bibgo r
                where vm._Marker_key = r._Marker_key
                and not exists (select 1 from VOC_Annot a, VOC_Evidence e
                    where a._AnnotType_key = 1000
                    and a._Annot_key = e._Annot_key
                    and e._Refs_key = r._Refs_key)
                group by vm._Marker_key
                union
                select distinct vm._Marker_key, 0
                from validMarkers vm
                where not exists (select 1 from reduced_bibgo r where vm._Marker_key = r._Marker_key)
                )
                ''', None)

        db.sql('create index refGOUnused_idx on refGOUnused (_Marker_key)', None)

        #
        # number of unqiue references by marker used by GO
        #
        db.sql('''
                (
                select distinct vm._Marker_key, count(distinct e._Refs_key) as goRefUsedCount
                into temporary table refGOUsed
                from validMarkers vm, voc_annot a, voc_evidence e, bib_workflow_status s
                where vm._Marker_key = a._Object_key
                and a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key
                and e._Refs_key = s._Refs_key
                and s.iscurrent = 1
                and s._group_key = 31576666
                and s._status_key = 31576674
                group by vm._Marker_key
                union
                select distinct vm._Marker_key, 0
                from validMarkers vm
                where not exists (select 1 from voc_annot a, voc_evidence e, bib_workflow_status s
                        where vm._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._Refs_key = s._Refs_key
                        and s.iscurrent = 1
                        and s._group_key = 31576666
                        and s._status_key = 31576674
                        )
                )
                ''', None)

        db.sql('create index refGOUsed_idx on refGOUsed (_Marker_key)', None)

def getOverall():
        #
        # goOverall = validMarkers (basic marker info) plus other temp tables:
        #       mrkAlleles
        #       mrkDOAnnot
        #       mrkDOHumanAnnot
        #       mrkOrtholog : human/rat
        #       refGOUnused : references by marker
        #       refGOUsed : references by marker
        #
        # the count of markers in validMarkers should match the count of markers in goOverall
        #
        # LEFT OUTER JOIN required
        #
        db.sql('''
                select m._Marker_key,
                case when gt.completion_date is not null then 'Yes' else 'No' end as isComplete,
                case when ma.hasAlleles > 0 then 'Yes' else 'No' end as hasAlleles,
                case when moa.hasDO > 0 then 'Yes' else 'No' end as hasDO,
                case when moha.hasDOHuman > 0 then 'Yes' else 'No' end as hasHumanDO,
                case when mho.hasOrtholog > 0 then 'Yes' else 'No' end as hasOrtholog,
                rgs.goRefUnusedCount,
                rgt.goRefUsedCount
                into temporary table goOverall
                from validMarkers m LEFT OUTER JOIN GO_Tracking gt on (m._Marker_key = gt._Marker_key),
                     mrkAlleles ma, 
                     mrkDOAnnot moa,
                     mrkDOHumanAnnot moha, 
                     mrkOrtholog mho,
                     refGOUnused rgs,
                     refGoUsed rgt
                where m._Marker_key = ma._Marker_key
                and m._Marker_key = moa._Marker_key
                and m._Marker_key = mho._Marker_key
                and m._Marker_key = moha._Marker_key
                and m._Marker_key = rgs._Marker_key
                and m._Marker_key = rgt._Marker_key
                ''', None)

        db.sql('create index goOverall_idx on goOverall (_Marker_key)', None)

def processStats():
        #
        # create temp tables to organize results, counts, etc.
        #

        global resultsNoGO
        global resultsND
        global resultsIEA
        global resultsIEAND
        global resultsIBA
        global resultsIBAND
        global resultsIBAIEAND
        global resultsEXP
        global resultsHTP
        global resultsIBAIEA
        global resultsAllOther

        global noGOCount, noGOGeneCount, noGOPredictedCount
        global NDCount, NDGeneCount, NDPredictedCount
        global IEACount, IEAGeneCount, IEAPredictedCount
        global IEANDCount, IEANDGeneCount, IEANDPredictedCount
        global IBACount, IBAGeneCount, IBAPredictedCount
        global IBANDCount, IBANDGeneCount, IBANDPredictedCount
        global IBAIEACount, IBAIEAGeneCount, IBAIEAPredictedCount
        global IBAIEANDCount, IBAIEANDGeneCount, IBAIEANDPredictedCount
        global EXPCount, EXPGeneCount, EXPPredictedCount
        global HTPCount, HTPGeneCount, HTPPredictedCount
        global otherCount, otherGeneCount, otherPredictedCount
        global hasOrthologCount, hasOrthologGeneCount, hasOrthologPredictedCount
        global hasDOCount, hasDOGeneCount, hasDOPredictedCount
        global hasHumanDOCount, hasHumanDOGeneCount, hasHumanDOPredictedCount
        global hasAlleleCount, hasAlleleGeneCount, hasAllelePredictedCount
        global hasCompleteCount, hasCompleteGeneCount, hasCompletePredictedCount
        global hasGORef1Count
        global hasGORef2Count

        global totalGeneCount, totalPredictedCount

        totalGeneCount = 0
        totalPredictedCount = 0

        #
        # using validMarkers and goOverall
        #       process some counts (sections 1-15 at top of GO_CombinedReport report)
        #       process the GO Status (field 1) sections
        #

        # markers w/o GO annotations
        db.sql('''
                select distinct '1' as type, m.*, g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, g.goRefUnusedCount, g.goRefUsedCount
                into temporary table hasNoGO
                from validMarkers m, goOverall g
                where m._Marker_key = g._Marker_key
                and not exists (select 1 from  VOC_Annot a where m._Marker_key = a._Object_key and a._AnnotType_key = 1000)
                ''', None)
        results = db.sql('select count(*) as noGOCount from hasNoGO', 'auto')
        noGOCount = results[0]['noGOCount']
        resultsNoGO = db.sql('select * from hasNoGO', 'auto')
        results = db.sql(''' select count(*) as counter from hasNoGO where predictedGene = 'No' ''', 'auto')
        totalGeneCount += results[0]['counter']
        noGOGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasNoGO where predictedGene = 'Yes' ''', 'auto')
        totalPredictedCount += results[0]['counter']
        noGOPredictedCount = results[0]['counter']

        # markers with ND Only
        db.sql('''
                select distinct '2' as type, m.*, g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, g.goRefUnusedCount, g.goRefUsedCount
                into temporary table hasNDOnly
                from validMarkers m, goOverall g
                where m._Marker_key = g._Marker_key
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
                ''', None)
        resultsND = db.sql('select * from hasNDOnly', 'auto')
        NDCount = len(resultsND)
        results = db.sql(''' select count(*) as counter from hasNDOnly where predictedGene = 'No' ''', 'auto')
        totalGeneCount += results[0]['counter']
        NDGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasNDOnly where predictedGene = 'Yes' ''', 'auto')
        totalPredictedCount += results[0]['counter']
        NDPredictedCount = results[0]['counter']

        # markers with IEA Only
        db.sql('''
                select distinct '3' as type, m.*, g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, g.goRefUnusedCount, g.goRefUsedCount
                into temporary table hasIEAOnly
                from validMarkers m, goOverall g
                where m._Marker_key = g._Marker_key
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
        resultsIEA = db.sql('select * from hasIEAOnly', 'auto')
        IEACount = len(resultsIEA)
        results = db.sql(''' select count(*) as counter from hasIEAOnly where predictedGene = 'No' ''', 'auto')
        totalGeneCount += results[0]['counter']
        IEAGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasIEAOnly where predictedGene = 'Yes' ''', 'auto')
        totalPredictedCount += results[0]['counter']
        IEAPredictedCount = results[0]['counter']

        # markers with IEA + ND Only
        db.sql('''
                select distinct '4' as type, m.*, g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, g.goRefUnusedCount, g.goRefUsedCount
                into temporary table hasIEANDOnly
                from validMarkers m, goOverall g
                where m._Marker_key = g._Marker_key
                and exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 115)
                and exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 118)
                and not exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key not in (115, 118))
                ''', None)
        resultsIEAND = db.sql('select * from hasIEANDOnly', 'auto')
        IEANDCount = len(resultsIEAND)
        results = db.sql(''' select count(*) as counter from hasIEANDOnly where predictedGene = 'No' ''', 'auto')
        totalGeneCount += results[0]['counter']
        IEANDGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasIEANDOnly where predictedGene = 'Yes' ''', 'auto')
        totalPredictedCount += results[0]['counter']
        IEANDPredictedCount = results[0]['counter']

        # markers with IBA Only
        db.sql('''
                select distinct '6' as type, m.*, g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, g.goRefUnusedCount, g.goRefUsedCount
                into temporary table hasIBAOnly
                from validMarkers m, goOverall g
                where m._Marker_key = g._Marker_key
                and exists (select 1 from  VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 7428292)
                and not exists (select 1 from  VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key != 7428292)
                ''', 'auto')
        resultsIBA = db.sql('select * from hasIBAOnly', 'auto')
        IBACount = len(resultsIBA)
        results = db.sql(''' select count(*) as counter from hasIBAOnly where predictedGene = 'No' ''', 'auto')
        totalGeneCount += results[0]['counter']
        IBAGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasIBAOnly where predictedGene = 'Yes' ''', 'auto')
        totalPredictedCount += results[0]['counter']
        IBAPredictedCount = results[0]['counter']

        # markers with IBA + ND Only
        db.sql('''
                select distinct '7' as type, m.*, g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, g.goRefUnusedCount, g.goRefUsedCount
                into temporary table hasIBAND
                from validMarkers m, goOverall g
                where m._Marker_key = g._Marker_key
                and exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 7428292)
                and exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 118)
                and not exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key not in (7428292, 118))
                ''', None)
        resultsIBAND = db.sql('select * from hasIBAND', 'auto')
        IBANDCount = len(resultsIBAND)
        results = db.sql(''' select count(*) as counter from hasIBAND where predictedGene = 'No' ''', 'auto')
        totalGeneCount += results[0]['counter']
        IBANDGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasIBAND where predictedGene = 'Yes' ''', 'auto')
        totalPredictedCount += results[0]['counter']
        IBANDPredictedCount = results[0]['counter']

        # markers with IBA + IEA + ND Only
        db.sql('''
                select distinct '8' as type, m.*, g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, g.goRefUnusedCount, g.goRefUsedCount
                into temporary table hasIBAIEAND
                from validMarkers m, goOverall g
                where m._Marker_key = g._Marker_key
                and exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 7428292)
                and exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 115)
                and exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 118)
                and not exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key not in (7428292, 115, 118))
                ''', None)
        resultsIBAIEAND = db.sql('select * from hasIBAIEAND', 'auto')
        IBAIEANDCount = len(resultsIBAIEAND)
        results = db.sql(''' select count(*) as counter from hasIBAIEAND where predictedGene = 'No' ''', 'auto')
        totalGeneCount += results[0]['counter']
        IBAIEANDGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasIBAIEAND where predictedGene = 'Yes' ''', 'auto')
        totalPredictedCount += results[0]['counter']
        IBAIEANDPredictedCount = results[0]['counter']

        # markers with IBA + IEA Only
        db.sql('''
                select distinct '11' as type, m.*, g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, g.goRefUnusedCount, g.goRefUsedCount
                into temporary table hasIBAIEA
                from validMarkers m, goOverall g
                where m._Marker_key = g._Marker_key
                and exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 7428292)
                and exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 115)
                and not exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key not in (7428292, 115))
                ''', None)
        resultsIBAIEA = db.sql('select * from hasIBAIEA', 'auto')
        IBAIEACount = len(resultsIBAIEA)
        results = db.sql(''' select count(*) as counter from hasIBAIEA where predictedGene = 'No' ''', 'auto')
        totalGeneCount += results[0]['counter']
        IBAIEAGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasIBAIEA where predictedGene = 'Yes' ''', 'auto')
        totalPredictedCount += results[0]['counter']
        IBAIEAPredictedCount = results[0]['counter']

        # markers that includes: EXP, IDA, IEP, IGI, IMP, & IPI
        db.sql('''
                select distinct '9' as type, m.*, g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, g.goRefUnusedCount, g.goRefUsedCount
                into temporary table hasEXP
                from validMarkers m, goOverall g
                where m._Marker_key = g._Marker_key
                and exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key in (4003114,109,117,112,110,111))
                ''', None)
        resultsEXP = db.sql('select * from hasEXP', 'auto')
        EXPCount = len(resultsEXP)
        results = db.sql(''' select count(*) as counter from hasEXP where predictedGene = 'No' ''', 'auto')
        totalGeneCount += results[0]['counter']
        EXPGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasEXP where predictedGene = 'Yes' ''', 'auto')
        totalPredictedCount += results[0]['counter']
        EXPPredictedCount = results[0]['counter']

        # markers that include: HDA, HEP, HGI, HMP, HTP
        # but does NOT include ANY : EXP, IDA, IEP, IGI, IMP, IPI
        resultsHTP = db.sql('''
                select distinct '10' as type, m.*, g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, g.goRefUnusedCount, g.goRefUsedCount
                into temporary table hasHTP
                from validMarkers m, goOverall g
                where m._Marker_key = g._Marker_key
                and exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key in (37264173,37264174,37264172,37264171))
                and not exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 4003114)
                and not exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 109)
                and not exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 117)
                and not exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 112)
                and not exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 110)
                and not exists (select 1 from VOC_Annot a, VOC_Evidence e
                        where m._Marker_key = a._Object_key
                        and a._AnnotType_key = 1000
                        and a._Annot_key = e._Annot_key
                        and e._EvidenceTerm_key = 111)
                ''', None)
        resultsHTP = db.sql('select * from hasHTP', 'auto')
        HTPCount = len(resultsHTP)
        results = db.sql(''' select count(*) as counter from hasHTP where predictedGene = 'No' ''', 'auto')
        totalGeneCount += results[0]['counter']
        HTPGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasHTP where predictedGene = 'Yes' ''', 'auto')
        totalPredictedCount += results[0]['counter']
        HTPPredictedCount = results[0]['counter']

        # markers with all other annotations
        db.sql('''
                select distinct '5' as type, m.*, g.isComplete, g.hasAlleles, g.hasDO, g.hasHumanDO, g.hasOrtholog, g.goRefUnusedCount, g.goRefUsedCount
                into temporary table hasOther
                from validMarkers m, goOverall g
                where m._Marker_key = g._Marker_key
                and exists (select 1 from VOC_Annot a where a._AnnotType_key = 1000 and m._Marker_key = a._Object_key)
                and not exists (select 1 from hasNDOnly r where m._Marker_key = r._Marker_key)
                and not exists (select 1 from hasIEAOnly r where m._Marker_key = r._Marker_key)
                and not exists (select 1 from hasIEANDOnly r where m._Marker_key = r._Marker_key)
                and not exists (select 1 from hasIBAOnly r where m._Marker_key = r._Marker_key)
                and not exists (select 1 from hasIBAND r where m._Marker_key = r._Marker_key)
                and not exists (select 1 from hasIBAIEAND r where m._Marker_key = r._Marker_key)
                and not exists (select 1 from hasIBAIEA r where m._Marker_key = r._Marker_key)
                and not exists (select 1 from hasEXP r where m._Marker_key = r._Marker_key)
                and not exists (select 1 from hasHTP r where m._Marker_key = r._Marker_key)
                ''', None)
        resultsAllOther = db.sql('select * from hasOther', 'auto')
        otherCount = len(resultsAllOther)
        results = db.sql(''' select count(*) as counter from hasOther where predictedGene = 'No' ''', 'auto')
        totalGeneCount += results[0]['counter']
        otherGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasOther where predictedGene = 'Yes' ''', 'auto')
        totalPredictedCount += results[0]['counter']
        otherPredictedCount = results[0]['counter']

        # rat/human homologs
        db.sql('''
                select go._Marker_key, m.predictedGene 
                into temporary table hasOrtholog
                from validMarkers m, goOverall go, hasNoGO hng
                where m._Marker_key = go._Marker_key
                and go.hasOrtholog = 'Yes' 
                and go._Marker_key = hng._Marker_key 
                ''', None)
        results = db.sql('select count(*) as counter from hasOrtholog', 'auto')
        hasOrthologCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasOrtholog where predictedGene = 'No' ''', 'auto')
        hasOrthologGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasOrtholog where predictedGene = 'Yes' ''', 'auto')
        hasOrthologPredictedCount = results[0]['counter']

        # Count of markers with do/genotype annotations and no GO annotations
        db.sql('''
                select go._Marker_key, m.predictedGene 
                into temporary table hasDO
                from validMarkers m, goOverall go, hasNoGO hng
                where m._Marker_key = go._Marker_key
                and go.hasDO = 'Yes' 
                and go._Marker_key = hng._Marker_key 
                ''', None)
        results = db.sql('select count(*) as counter from hasDO', 'auto')
        hasDOCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasDO where predictedGene = 'No' ''', 'auto')
        hasDOGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasDO where predictedGene = 'Yes' ''', 'auto')
        hasDOPredictedCount = results[0]['counter']

        # Count of markers with human disease annotations
        db.sql('''
                select go._Marker_key, m.predictedGene 
                into temporary table hasHumanDO
                from validMarkers m, goOverall go, hasNoGO hng
                where m._Marker_key = go._Marker_key
                and go.hasHumanDO = 'Yes' 
                and go._Marker_key = hng._Marker_key 
                ''', None)
        results = db.sql('select count(*) as counter from hasHumanDO', 'auto')
        hasHumanDOCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasHumanDO where predictedGene = 'No' ''', 'auto')
        hasHumanDOGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasHumanDO where predictedGene = 'Yes' ''', 'auto')
        hasHumanDOPredictedCount = results[0]['counter']

        # Count of markers that have alleles	
        db.sql('''
                select go._Marker_key, m.predictedGene 
                into temporary table hasAlleles
                from validMarkers m, goOverall go, hasNoGO hng
                where m._Marker_key = go._Marker_key
                and go.hasAlleles = 'Yes' 
                and go._Marker_key = hng._Marker_key 
                ''', None)
        results = db.sql('select count(*) as counter from hasAlleles', 'auto')
        hasAlleleCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasAlleles where predictedGene = 'No' ''', 'auto')
        hasAlleleGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasAlleles where predictedGene = 'Yes' ''', 'auto')
        hasAllelePredictedCount = results[0]['counter']

        # Count of markers marked complete in go	
        db.sql('''
                select go._Marker_key, m.predictedGene 
                into temporary table hasComplete
                from validMarkers m, goOverall go
                where m._Marker_key = go._Marker_key
                and go.isComplete = 'Yes'
                ''', None)
        results = db.sql('select count(*) as counter from hasComplete', 'auto')
        hasCompleteCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasComplete where predictedGene = 'No' ''', 'auto')
        hasCompleteGeneCount = results[0]['counter']
        results = db.sql(''' select count(*) as counter from hasComplete where predictedGene = 'Yes' ''', 'auto')
        hasCompletePredictedCount = results[0]['counter']

        # number of unique references in validMarkers that have GO annotations
        db.sql('''
                select distinct r._refs_key
                into temporary table hasGORef1
                from validMarkers m
                        LEFT OUTER JOIN reduced_bibgo r on (m._Marker_key = r._Marker_key
                        and exists (select 1 from VOC_Annot a where m._Marker_key = a._Object_key and a._AnnotType_key = 1000))
                ''', None)
        results = db.sql('select count(*) as counter from hasGORef1', 'auto')
        hasGORef1Count = results[0]['counter']

        # number of unique references in validMarkers that do not have GO annotations
        results = db.sql('''
                select distinct r._refs_key
                into temporary table hasGORef2
                from validMarkers m
                        LEFT OUTER JOIN reduced_bibgo r on (m._Marker_key = r._Marker_key
                        and not exists (select 1 from VOC_Annot a where m._Marker_key = a._Object_key and a._AnnotType_key = 1000))
                ''', 'auto')
        results = db.sql('select count(*) as counter from hasGORef2', 'auto')
        hasGORef2Count = results[0]['counter']

def openRpts():
        global fp
        global fp2
        global fp3

        header = "includes: organism = mouse, type = Gene, status = official" + CRT
        header += "excludes: feature type = 'heritable phenotypic marker' " + CRT
        header += "excludes: Gt(ROSA)26Sor" + 2*CRT
        header += "'Predicted genes' are those that:" + CRT
        header += "- have a name that starts with the words 'gene model'" + CRT
        header += "- have a name that starts with the words 'predicted gene'" + CRT
        header += "- have a name that starts with the words 'gene trap'" + CRT
        header += "- have a symbol that starts with the word 'ORF'" + CRT
        header += "- have a symbol that is a single letter followed by up to 5 numbers, for example 'a12345'" + CRT
        header += "- have a symbol that is two letters followed by up to 5 numbers, for example 'ab12345'" + CRT

        fp = reportlib.init(sys.argv[0], 'GO Combined Report', os.environ['QCOUTPUTDIR'])
        fp.write(header)
        fp2 = reportlib.init('GO_MRK_NoGO', 'Marker No GO', os.environ['QCOUTPUTDIR'])
        fp2.write(header)
        fp3 = reportlib.init('GO_MRK_NoGO_Has_Alleles', 'Marker No GO w/ Alleles', os.environ['QCOUTPUTDIR'])
        fp3.write(header)

def printFeatures(fpFeature, fpType):
        #
        # feature types counts:  total, gene, predicted gene
        #

        fpFeature.write(CRT + str.ljust("Feature type", 55) + str.ljust("total", 10) + str.ljust("gene", 10) + str.ljust("predicted gene", 10) + CRT)

        totalFeature = 0
        totalFeatureGene = 0
        totalFeaturePredicted = 0

        # 'gene', 'predictedGene' counts by feature type
        cmd = ''' select vm.featureType, vm.predictedGene, count(vm.predictedGene) as genecount from validMarkers vm '''

        if fpType == 2:
                cmd += '''\nwhere exists (select 1 from hasNoGO ma where vm._marker_key = ma._marker_key) '''
        elif fpType == 3:
                cmd += '''\nwhere exists (select 1 from hasAlleles ma where vm._marker_key = ma._marker_key) '''

        results = db.sql(cmd + '''\ngroup by vm.featureType, vm.predictedGene order by vm.featureType, vm.predictedGene asc ''', 'auto')
        featureType = {}
        for r in results:
                key = r['featureType']
                value = r
                if key not in featureType:
                        featureType[key] = []
                featureType[key].append(r)
        #print(featureType)

        # total count by featurea type
        cmd = ''' select vm.featureType, count(vm._marker_key) as totalcount from validMarkers vm '''
        if fpType == 2:
                cmd += '''\nwhere exists (select 1 from hasNoGO ma where vm._marker_key = ma._marker_key) '''
        elif fpType == 3:
                cmd += '''\nwhere exists (select 1 from hasAlleles ma where vm._marker_key = ma._marker_key) '''
        results = db.sql(cmd + '''\n group by featureType order by featureType asc ''', 'auto')
        featureTotal = {}
        for r in results:
                key = r['featureType']
                value = r['totalcount']
                if key not in featureTotal:
                        featureTotal[key] = []
                featureTotal[key].append(value)
        #print(featureTotal)

        for key in featureType:

                fpFeature.write(str.ljust(str(key), 55))
                fpFeature.write(str.ljust(str(featureTotal[key][0]), 10))
                totalFeature += featureTotal[key][0]

                foundNo = False
                foundYes = False

                for r in featureType[key]:

                        if r['predictedGene'] == 'No':
                                fpFeature.write(str.ljust(str(r['genecount']), 10))
                                totalFeatureGene += r['genecount']
                                foundNo = True

                        if r['predictedGene'] == 'Yes':
                                if foundNo == False:
                                        fpFeature.write(str.ljust(str(0), 10))
                                fpFeature.write(str.ljust(str(r['genecount']), 10))
                                totalFeaturePredicted += r['genecount']
                                foundYes = True

                if foundYes == False:
                        fpFeature.write(str.ljust(str(0), 10))

                fpFeature.write(CRT)

        fpFeature.write(str.ljust("Totals:", 55))
        fpFeature.write(str.ljust(str(totalFeature), 10))
        fpFeature.write(str.ljust(str(totalFeatureGene), 10))
        fpFeature.write(str.ljust(str(totalFeaturePredicted), 10))
        fpFeature.write(2*CRT)

def printRpt1():

        # print out the header
        fp.write(str.ljust("Category", 75) + str.ljust("total", 10) + str.ljust("gene", 10) + str.ljust("predicted gene", 10) + CRT)

        totalCount = noGOCount + IEACount + NDCount + IEANDCount + IBACount + IBANDCount + IBAIEACount + IBAIEANDCount + EXPCount + HTPCount + otherCount
        fp.write(str.ljust("1. Total number of rows:", 75))
        fp.write(str.ljust(str(totalCount), 10) + str.ljust(str(totalGeneCount), 10) + str.ljust(str(totalPredictedCount), 10))
        fp.write(2*CRT + str.ljust("2. Genes with no GO Annotations:", 75))
        fp.write(str.ljust(str(noGOCount), 10) + str.ljust(str(noGOGeneCount), 10) + str.ljust(str(noGOPredictedCount), 10))
        fp.write(2*CRT + str.ljust("3. Genes with Annotations to ND Only:", 75))
        fp.write(str.ljust(str(NDCount), 10) + str.ljust(str(NDGeneCount), 10) + str.ljust(str(NDPredictedCount), 10))
        fp.write(2*CRT + str.ljust("4. Genes with Annotations to IEA Only:", 75))
        fp.write(str.ljust(str(IEACount), 10) + str.ljust(str(IEAGeneCount), 10) + str.ljust(str(IEAPredictedCount), 10))
        fp.write(2*CRT + str.ljust("5. Genes with Annotations to ND+IEA Only:", 75))
        fp.write(str.ljust(str(IEANDCount), 10) + str.ljust(str(IEANDGeneCount), 10) + str.ljust(str(IEANDPredictedCount), 10))
        fp.write(2*CRT + str.ljust("6. Genes with Annotations to IBA Only:", 75))
        fp.write(str.ljust(str(IBACount), 10) + str.ljust(str(IBAGeneCount), 10) + str.ljust(str(IBAPredictedCount), 10))
        fp.write(2*CRT + str.ljust("7. Genes with Annotations to ND+IBA Only:", 75))
        fp.write(str.ljust(str(IBANDCount), 10) + str.ljust(str(IBANDGeneCount), 10) + str.ljust(str(IBANDPredictedCount), 10))
        fp.write(2*CRT + str.ljust("8. Genes with Annotations to IBA+IEA Only:", 75))
        fp.write(str.ljust(str(IBAIEACount), 10) + str.ljust(str(IBAIEAGeneCount), 10) + str.ljust(str(IBAIEAPredictedCount), 10))
        fp.write(2*CRT + str.ljust("9. Genes with Annotations to ND+IBA+IEA Only:", 75))
        fp.write(str.ljust(str(IBAIEANDCount), 10) + str.ljust(str(IBAIEANDGeneCount), 10) + str.ljust(str(IBAIEANDPredictedCount), 10))
        fp.write(2*CRT + str.ljust("10. Genes with many EXP Annotations:", 75))
        fp.write(str.ljust(str(EXPCount), 10) + str.ljust(str(EXPGeneCount), 10) + str.ljust(str(EXPPredictedCount), 10))
        fp.write(2*CRT + str.ljust("11. Genes with HTP but not manual EXP Annotations:", 75))
        fp.write(str.ljust(str(HTPCount), 10) + str.ljust(str(HTPGeneCount), 10) + str.ljust(str(HTPPredictedCount), 10))
        fp.write(2*CRT + str.ljust("12. Genes with Annotations to All other:", 75))
        fp.write(str.ljust(str(otherCount), 10) + str.ljust(str(otherGeneCount), 10) + str.ljust(str(otherPredictedCount), 10))
        fp.write(2*CRT + str.ljust("13. Mouse Genes that have Rat/Human Homologs and NO GO annotations:", 75))
        fp.write(str.ljust(str(hasOrthologCount), 10) + str.ljust(str(hasOrthologGeneCount), 10) + str.ljust(str(hasOrthologPredictedCount), 10))
        fp.write(2*CRT + str.ljust("14. Mouse Genes with DO Genotype Annotations and NO GO annotations:", 75))
        fp.write(str.ljust(str(hasDOCount), 10) + str.ljust(str(hasDOGeneCount), 10) + str.ljust(str(hasDOPredictedCount), 10))
        fp.write(2*CRT + str.ljust("15. Mouse Genes with Human Disease Annotations and NO GO annotations:", 75))
        fp.write(str.ljust(str(hasHumanDOCount), 10) + str.ljust(str(hasHumanDOGeneCount), 10) + str.ljust(str(hasHumanDOPredictedCount), 10))
        fp.write(2*CRT + str.ljust("16. Genes with Mutant Alleles and NO GO Annotations:", 75))
        fp.write(str.ljust(str(hasAlleleCount), 10) + str.ljust(str(hasAlleleGeneCount), 10) + str.ljust(str(hasAllelePredictedCount), 10))
        fp.write(2*CRT + str.ljust("17. Genes with GO Annotation reviewed date?:", 75))
        fp.write(str.ljust(str(hasCompleteCount), 10) + str.ljust(str(hasCompleteGeneCount), 10) + str.ljust(str(hasCompletePredictedCount), 10))
        fp.write(2*CRT + str.ljust("18. Total number of unique references that have GO Annotations:", 75))
        fp.write(str.ljust(str(hasGORef1Count), 10))
        fp.write(2*CRT + str.ljust("19. Total number of unique references that do not have GO Annotations:", 75))
        fp.write(str.ljust(str(hasGORef2Count), 10))

        # first report
        fp.write(2*CRT + "GO Status" + TAB + \
                "Gene Symbol" + TAB + \
                "MGI ID" + TAB + \
                "Gene Name" + TAB + \
                "Feature Type" + TAB + \
                "Predicted Gene" + TAB + \
                "Rat/Human Orthologs?" + TAB + \
                "DO Genotype Annotations?" + TAB + \
                "DO Human Annotations?" + TAB + \
                "Alleles?" + TAB + \
                "Annotation reviewed date?" + TAB + \
                "Unused GO Papers" + TAB + \
                "Used GO Papers" + TAB + \
                "Total GO Papers" + CRT)

def printRpt2():

        fp2.write(str.ljust("Category", 75) + str.ljust("total", 10) + str.ljust("gene", 10) + str.ljust("predicted gene", 10) + CRT)
        fp2.write(str.ljust("1. Genes with no GO Annotations:", 75))
        fp2.write(str.ljust(str(noGOCount), 10) + str.ljust(str(noGOGeneCount), 10) + str.ljust(str(noGOPredictedCount), 10))
        fp2.write(2*CRT + 
                "Gene Symbol" + TAB + \
                "MGI ID" + TAB + \
                "Gene Name" + TAB + \
                "Feature Type" + TAB + \
                "Predicted Gene" + TAB + \
                "Rat/Human Orthologs?" + TAB + \
                "DO Genotype Annotations?" + TAB + \
                "DO Human Annotations?" + TAB + \
                "Alleles?" + TAB + \
                "Annotation reviewed date?" + TAB + \
                "Unused GO Papers" + TAB + \
                "Used GO Papers" + TAB + \
                "Total GO Papers" + CRT)

def printRpt3():

        fp3.write(str.ljust("Category", 75) + str.ljust("total", 10) + str.ljust("gene", 10) + str.ljust("predicted gene", 10) + CRT)
        fp3.write(str.ljust("1. Genes with Mutant Alleles and NO GO Annotations:", 75))
        fp3.write(str.ljust(str(hasAlleleCount), 10) + str.ljust(str(hasAlleleGeneCount), 10) + str.ljust(str(hasAllelePredictedCount), 10))
        fp3.write(2*CRT +
                "Gene Symbol" + TAB + \
                "MGI ID" + TAB + \
                "Gene Name" + TAB + \
                "Feature Type" + TAB + \
                "Predicted Gene" + TAB + \
                "Rat/Human Orthologs?" + TAB + \
                "DO Genotype Annotations?" + TAB + \
                "DO Human Annotations?" + TAB + \
                "Alleles?" + TAB + \
                "Annotation reviewed date?" + TAB + \
                "Unused GO Papers" + TAB + \
                "Used GO Papers" + TAB + \
                "Total GO Papers" + CRT)
        
def printAllStats():
        #
        # print stats for all reports
        #

        for r in resultsNoGO:
                r = setPrintYesNo(r)
                fp.write(templateRow % (type1, r['symbol'], r['accID'], r['name'], r['featureType'], r['predictedGene'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefUnusedCount']), str(r['goRefUsedCount']), str(r['goRefUnusedCount'] + r['goRefUsedCount'])))
         
                # Report #2
                fp2.write(templateRow2 % (r['symbol'], r['accID'], r['name'], r['featureType'], r['predictedGene'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefUnusedCount']), str(r['goRefUsedCount']), str(r['goRefUnusedCount'] + r['goRefUsedCount'])))
         
                # Report #3
                if r['hasAlleles'] == hasAllelesYes:
                        fp3.write(templateRow2 % (r['symbol'], r['accID'], r['name'], r['featureType'], r['predictedGene'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefUnusedCount']), str(r['goRefUsedCount']), str(r['goRefUnusedCount'] + r['goRefUsedCount'])))
         
        for r in resultsND:
                r = setPrintYesNo(r)
                fp.write(templateRow % (type2, r['symbol'], r['accID'], r['name'], r['featureType'], r['predictedGene'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefUnusedCount']), str(r['goRefUsedCount']), str(r['goRefUnusedCount'] + r['goRefUsedCount'])))	
        
        for r in resultsIEA:
                r = setPrintYesNo(r)
                fp.write(templateRow % (type3, r['symbol'], r['accID'], r['name'], r['featureType'], r['predictedGene'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefUnusedCount']), str(r['goRefUsedCount']), str(r['goRefUnusedCount'] + r['goRefUsedCount'])))	
         
        for r in resultsIEAND:
                r = setPrintYesNo(r)
                fp.write(templateRow % (type4, r['symbol'], r['accID'], r['name'], r['featureType'], r['predictedGene'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefUnusedCount']), str(r['goRefUsedCount']), str(r['goRefUnusedCount'] + r['goRefUsedCount'])))	
         
        for r in resultsIBA:
                r = setPrintYesNo(r)
                fp.write(templateRow % (type6, r['symbol'], r['accID'], r['name'], r['featureType'], r['predictedGene'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefUnusedCount']), str(r['goRefUsedCount']), str(r['goRefUnusedCount'] + r['goRefUsedCount'])))	
         
        for r in resultsIBAND:
                r = setPrintYesNo(r)
                fp.write(templateRow % (type7, r['symbol'], r['accID'], r['name'], r['featureType'], r['predictedGene'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefUnusedCount']), str(r['goRefUsedCount']), str(r['goRefUnusedCount'] + r['goRefUsedCount'])))	
         
        for r in resultsIBAIEAND:
                r = setPrintYesNo(r)
                fp.write(templateRow % (type8, r['symbol'], r['accID'], r['name'], r['featureType'], r['predictedGene'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefUnusedCount']), str(r['goRefUsedCount']), str(r['goRefUnusedCount'] + r['goRefUsedCount'])))	
         
        for r in resultsEXP:
                r = setPrintYesNo(r)
                fp.write(templateRow % (type9, r['symbol'], r['accID'], r['name'], r['featureType'], r['predictedGene'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefUnusedCount']), str(r['goRefUsedCount']), str(r['goRefUnusedCount'] + r['goRefUsedCount'])))	
         
        for r in resultsHTP:
                r = setPrintYesNo(r)
                fp.write(templateRow % (type10, r['symbol'], r['accID'], r['name'], r['featureType'], r['predictedGene'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefUnusedCount']), str(r['goRefUsedCount']), str(r['goRefUnusedCount'] + r['goRefUsedCount'])))	
         
        for r in resultsIBAIEA:
                r = setPrintYesNo(r)
                fp.write(templateRow % (type11, r['symbol'], r['accID'], r['name'], r['featureType'], r['predictedGene'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefUnusedCount']), str(r['goRefUsedCount']), str(r['goRefUnusedCount'] + r['goRefUsedCount'])))	
         
        for r in resultsAllOther:
                r = setPrintYesNo(r)
                fp.write(templateRow % (type5, r['symbol'], r['accID'], r['name'], r['featureType'], r['predictedGene'], r['hasOrtholog'], r['hasDO'], r['hasHumanDO'], r['hasAlleles'], r['isComplete'], str(r['goRefUnusedCount']), str(r['goRefUsedCount']), str(r['goRefUnusedCount'] + r['goRefUsedCount'])))    

def closeRpts():

        reportlib.finish_nonps(fp)
        reportlib.finish_nonps(fp2)
        reportlib.finish_nonps(fp3)

#
#
# Main
#

getMarkers()
getAlleles()
getMarkerDO()
getOrthologs()
getRefs()
getOverall()
processStats()
openRpts()
printFeatures(fp,1)
printFeatures(fp2,2)
printFeatures(fp3,3)
printRpt1()
printRpt2()
printRpt3()
printAllStats()
closeRpts()

