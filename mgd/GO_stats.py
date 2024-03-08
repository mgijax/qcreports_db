'''
#
# GO_stats.py
#
# CDEFG,3-7   : Total # of Genes
# HIJKL,8-12  : Total # of Predicted Genes
# MNOPQ,13-17 : Total # of Annotations
# R,18        : Classification Axis
# S,19        : Sorting Classification
#
# Section I   - GO Ontology Summary      : processSection1()
#
# Section II  - Counts by Features types : processSection2()
# A: All Annotations
# B: Protein Coding Features
# C: RNA Features
# D: Pseudogenic Features
# E: Other Features
#
# Section III - Counts by Assigned By  : processSection3()
# A: Experimental Annotations (EXP, IDA, IEP, IGI, IMP, or IPI) by Contributor (assigned by)
# B: High-throughput Annotations (HTP, HDA, HMP, HGI, or HEP) by Contributor (assigned by)
# C: Curator/Author Statement Annotations (IC, TAS, NAS) by Contributor (assigned by)
# D: Total RCA Annotations by Contributor (assigned by)
# E: Root Annotations (ND) by Contributor (assigned by)
# E1: Root Annotations (ND & GO_REFS:0000015) by Contributor (assigned by)
# E2: Other Root Annotations (ND & NOT GO_REFS:0000015) by Contributor (assigned by)
# F: Manual Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO) from PMIDs by Contributor (assigned by)
# F1: Manual Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO) from non-GO_REF references by Contributor (assigned by)
# F2: Manual Sequence Annotations with GO_REF:0000008 (J:73065)
# F3: Manual Sequence Annotations with GO_REF:0000024
# F4: Manual Sequence Annotations with GO_REF:0000114
#
# This report:
#       . depends on report GO_MGIGAF.rpt, which is genereated from GO_MGIGAF.py, which is created *before* this reprot
#       . is a set of counts taken from the GO_MGIGAF.rpt file
#
# The GO_MGIGAF.rpt file is read into temp table 'gafAnnotations'      : createTempGAF()
# Columns are used in gafAnnotations to generate the Annotation counts : createTempSection3()
#
# Contact person:  Karen.Christie@jax.org
#
# History:
#
# 02/28/2024    lec
#       wts2-1155/GOC taking over GOA mouse, GOA human, etc.
#
'''
 
import sys 
import os
import reportlib
import db

db.setTrace(True)

CRT = reportlib.CRT
TAB = reportlib.TAB

totalGene = {}
dagGene = {}
totalPredicted = {}
dagPredicted = {}
totalAll = {}
dagAll = {}
totalSummary = {}

#
# start: creating temp tables
#

def createTempGAF():
        #
        # Use the mgi-GAF file:
        #       os.environ['QCREPORTDIR'] + '/output/GO_MGIGAF.rpt'
        #       
        # to create a temporary GAF table : gafAnnotations
        # i.e., bcp the mgi-GAF file into the temporary GAF table
        # if the GAF format changes, then the gafAnnotations format may need to change
        #
        # this must be in sync with gaf-version: 2.2
        # the ** are the columns used in this report
        #
        # !1  DB
        # !2  **DB Object ID (MGI ID)
        # !3  DB Object Symbol
        # !4  **Qualifier
        # !5  **GO ID
        # !6  **DB:Reference (|DB:Reference)
        # !7  **Evidence Code              
        # !8  **With (or) From             
        # !9  Aspect
        # !10 DB Object Name
        # !11 DB Object Synonym (|Synonym)
        # !12 DB Object Type
        # !13 Taxon(|taxon)
        # !14 Date
        # !15 **Assigned By                
        # !16 **Annotation Extension
        # !17 **Gene Product Form ID (proteoform)
        #

        db.sql('drop table if exists gafAnnotations;', None)
        db.sql('''
        create table gafAnnotations (
                db text,
                mgiid text,
                symbol text,
                qualifier text,
                goid text,
                refs text,
                evidenceCode text,
                inferredFrom text,
                aspect text,
                name text,
                synonyms text,
                dbType text,
                taxon text,
                dbDate text,
                assignedBy text,
                extensions text,
                proteoform text
        );
        ''', None)
        db.commit()
        gafFileName = os.environ['QCREPORTDIR'] + '/output/GO_MGIGAF.rpt'
        db.bcp(gafFileName, 'gafAnnotations')
        db.commit()
        db.sql('create index gaf_idx1 on gafAnnotations (mgiid)', None)
        db.sql('create index gaf_idx2 on gafAnnotations (goid)', None)

def createTempMarkers():
        #
        # validMarkers : distinct set of markers used for this report
        #
        # mouse markers that contains GO Annotations (_vocab_key = 1000)
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

        db.sql('''
                WITH markers AS (
                        select distinct a.accid as mgiid, m.symbol, m.name, t.term as featureType
                        from MRK_Marker m, ACC_Accession a, VOC_Annot va, VOC_Term t
                        where m._marker_key = va._object_key
                        and va._annottype_key = 1011    -- MCV/Marker
                        and va._term_key = t._term_key
                        and m._marker_key = a._object_key
                        and a._mgitype_key = 2
                        and a._logicaldb_key = 1
                        and a.prefixPart = 'MGI:'
                        and a.preferred = 1
                        and m._organism_key = 1
                        and m._marker_status_key = 1
                        and exists (select 1 from gafAnnotations gaf where gaf.mgiid = a.accid)
                        --and m.symbol in ('Nrg1')
                )
                select m.*, 'Yes' as predictedGene
                into temporary table validMarkers
                from markers m
                where (
                        m.name like 'gene model %'
                        or m.name like 'gene trap %'
                        or m.name like 'predicted gene%'
                        or m.symbol like 'ORF%'
                        or m.symbol ~ '[A-Z][0-9][0-9][0-9][0-9][0-9]'
                        or m.symbol ~ '[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]'
                )
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

        db.sql('create index validMarkers_idx on validMarkers (mgiid)', None)

def createTempSection2(subsection):
        #
        # section 2: create the temp tables for given subsection A-J
        #
        # A: All Annotations
        # B: Protein Coding Features
        # C: RNA Features
        # D: Pseudogenic Features
        # E: Other Features
        #
        # validGenes      : set of marker by dag where predited = 'No'
        # validPredicted  : set of marker by dag where predicted = 'Yes'
        # validAnnoations : set of annotations by dag
        #

        db.sql('drop table if exists validGenes;', None)
        db.sql('drop table if exists validPredicted;', None)
        db.sql('drop table if exists validAnnotations;', None)

        # all annotations
        if subsection == 'A':
                addSQL = ''
        # protein coding features
        elif subsection == 'B':
                addSQL = ''' and gaf.dbType in (
                        'gene segment', 
                        'protein coding gene'
                        ) 
                        '''
        # RNA features
        elif subsection == 'C':
                addSQL = ''' and gaf.dbType in (
                        'antisense lncRNA gene',
                        'bidirectional promoter lncRNA gene',
                        'lincRNA gene',
                        'lncRNA gene',
                        'miRNA gene',
                        'non-coding RNA gene',
                        'RNase MRP RNA gene',
                        'RNase P RNA gene',
                        'rRNA gene',
                        'scRNA gene',
                        'sense intronic lncRNA gene',
                        'sense overlapping lncRNA gene',
                        'snoRNA gene',
                        'snRNA gene',
                        'SRP RNA gene',
                        'telomerase RNA gene',
                        'tRNA gene'
                        )
                        '''

        # pseudogenic features
        elif subsection == 'D':
                addSQL = ''' and gaf.dbType in (
                        'polymorphic pseudogene', 
                        'pseudogene', 
                        'pseudogenic gene segment'
                        )
                        '''

        # other features
        elif subsection == 'E':
                addSQL = ''' and gaf.dbType in (
                        'unclassified gene', 
                        'unclassified non-coding RNA gene'
                        )
                        '''
        db.sql('''
                select gaf.mgiid, gaf.dbType as groupBy, d._dag_key, d.name
                into temporary table validGenes
                from gafAnnotations gaf, ACC_Accession a, DAG_Node n, DAG_DAG d, VOC_Term t
                where gaf.goid = a.accid
                and a._logicaldb_key = 31
                %s
                and gaf.dbType = t.term
                and t._vocab_key = 79
                and a._object_key = n._object_key
                and n._dag_key = d._dag_key
                and d._dag_key in (1,2,3,4)
                and exists (select 1 from validMarkers m where gaf.mgiid = m.mgiid and m.predictedGene = 'No')
                ''' % (addSQL), None)

        db.sql('create index validGenes_idx on validGenes (mgiid)', None)

        db.sql('''
                select gaf.mgiid, gaf.dbType as groupBy, d._dag_key, d.name
                into temporary table validPredicted
                from gafAnnotations gaf, ACC_Accession a, DAG_Node n, DAG_DAG d
                where gaf.goid = a.accid
                and a._logicaldb_key = 31
                %s
                and a._object_key = n._object_key
                and n._dag_key = d._dag_key
                and d._dag_key in (1,2,3,4)
                and exists (select 1 from validMarkers m where gaf.mgiid = m.mgiid and m.predictedGene = 'Yes')
                ''' % (addSQL), None)

        db.sql('create index validPredicted_idx on validPredicted (mgiid)', None)

        # 
        # select the columns from gafAnnotations that are needed to determine a distinct Annotation row
        # the Annotation rows will be counted by DAG name/assignedBy
        # to change the distinct Annotation row logic, add or remove the proper gafAnnotations column to this set:
        #
        #       !2  **DB Object ID (MGI ID)
        #       !4  **Qualifier
        #       !5  **GO ID
        #       !6  **DB:Reference (|DB:Reference)
        #       !8  **With (or) From             
        #       !12 **DB Object Type
        #       !16 **Annotation Extension
        #       !17 **Gene Product Form ID (proteoform)
        #       + _dag_key, name
        #
        # addSQL is used to determine the specific set of feature types used for a given A-J subsection
        #
        db.sql('''
                select distinct gaf.mgiid, gaf.qualifier, gaf.goid, gaf.refs, 
                        gaf.inferredFrom, gaf.dbType as groupBy, gaf.extensions, gaf.proteoform,
                        d._dag_key, d.name
                into temporary table validAnnotations
                from gafAnnotations gaf, ACC_Accession a, DAG_Node n, DAG_DAG d
                where gaf.goid = a.accid
                and a._logicaldb_key = 31
                %s
                and a._object_key = n._object_key
                and n._dag_key = d._dag_key
                and d._dag_key in (1,2,3,4)
                and exists (select 1 from validMarkers m where gaf.mgiid = m.mgiid)
                ''' % (addSQL), None)

        db.sql('create index validAnnotations_idx1 on validAnnotations (mgiid)', None)
        db.sql('create index validAnnotations_idx2 on validAnnotations (goid)', None)

        # find all _vocab_key = 79 terms that do not exist/are not used in gaf.dbType, add gaf.dbType(groupBy) to validAnnotations
        # exclude the feature types below from consideration
        if subsection == 'E':
                results = db.sql('''
                        select t.term
                        from voc_term t
                        where t._vocab_key = 79
                        and not exists (select 1 from gafAnnotations gaf where gaf.dbType = t.term)
                        and exists (select 1 from VOC_Annot va where t._term_key = va._term_key and va._annottype_key = 1011)
                        and t.term not in (
                                'all feature types',
                                'QTL',
                                'transgene',
                                'complex/cluster/region',
                                'cytogenetic marker',
                                'BAC/YAC end',
                                'DNA segment',
                                'BAC end',
                                'PAC end',
                                'chromosomal deletion',
                                'chromosomal duplication',
                                'chromosomal inversion',
                                'chromosomal translocation',
                                'chromosomal transposition',
                                'CpG island',
                                'CTCF binding site',
                                'endogenous retroviral region',
                                'enhancer',
                                'heritable phenotypic marker',
                                'histone modification',
                                'imprinting control region',
                                'insertion',
                                'insulator',
                                'insulator binding site',
                                'intronic regulatory region',
                                'locus control region',
                                'minisatellite',
                                'mutation defined region',
                                'open chromatin region',
                                'origin of replication',
                                'other feature type',
                                'other genome feature',
                                'promoter',
                                'promoter flanking region',
                                'reciprocal chromosomal translocation',
                                'response element',
                                'retrotransposon',
                                'Robertsonian fusion',
                                'silencer',
                                'splice enhancer',
                                'telomere',
                                'transcriptional cis regulatory region',
                                'transcription factor binding site',
                                'TSS cluster',
                                'unclassified cytogenetic marker',
                                'YAC end'
                                )
                        order by t.term
                        ''', 'auto')
                for r in results:
                        db.sql(''' insert into validAnnotations select distinct null, null, null, null, null, '%s', null, null, v._dag_key, v.name from validAnnotations v; ''' % (r['term']), None)

def createTempSection3(subsection):
        #
        # section 3: create the temp tables for given subsection A-J
        #
        # A: Experimental Annotations (EXP, IDA, IEP, IGI, IMP, or IPI) by Contributor (assigned by)
        # B: High-throughput Annotations (HTP, HDA, HMP, HGI, or HEP) by Contributor (assigned by)
        # C: Curator/Author Statement Annotations (IC, TAS, NAS) by Contributor (assigned by)
        # D: Total RCA Annotations by Contributor (assigned by)
        # E: Root Annotations (ND) by Contributor (assigned by)
        # E1: Root Annotations (ND & GO_REFS:0000015) by Contributor (assigned by)
        # E2: Other Root Annotations (ND & NOT GO_REFS:0000015) by Contributor (assigned by)
        # F: Manual Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO) from PMIDs by Contributor (assigned by)
        # F1: Manual Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO) from non-GO_REF references by Contributor (assigned by)
        # F2: Manual Sequence Annotations with GO_REF:0000008 (J:73065)
        # F3: Manual Sequence Annotations with GO_REF:0000024
        # F4: Manual Sequence Annotations with GO_REF:0000114
        # F: Manual Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO) from PMIDs by Contributor (assigned by)
        #
        # validGenes      : set of marker by dag where predited = 'No'
        # validPredicted  : set of marker by dag where predicted = 'Yes'
        # validAnnoations : set of annotations by dag
        #

        db.sql('drop table if exists validGenes;', None)
        db.sql('drop table if exists validPredicted;', None)
        db.sql('drop table if exists validAnnotations;', None)

        # EXP|4003114 IDA|109 IEP|117 IGI|112 IMP|110 IPI|111
        if subsection == 'A':
                addSQL = 'and ec._term_key in (4003114,109,117,112,110,111)'
        # HTP:xxxx HDA|37264173 HEP|37264174 HGI|37264172 HMP|37264171
        elif subsection == 'B':
                addSQL = 'and ec._term_key in (37264173,37264174,37264172,37264171,114159319)'
        # IC|25238 TAS|113 NAS|116
        elif subsection == 'C':
                addSQL = 'and ec._term_key in (25238,113,116)'
        # RCA|514597
        elif subsection == 'D':
                addSQL = 'and ec._term_key in (514597)'

        # ND|118
        elif subsection == 'E':
                addSQL = 'and ec._term_key in (118)'
        # ND|118, GO_REF:0000015
        elif subsection == 'E1':
                addSQL = ''' and ec._term_key in (118) and gaf.refs = 'GO_REF:0000015' '''
        # ND|118, != GO_REF:0000015
        elif subsection == 'E2':
                addSQL = ''' and ec._term_key in (118) and gaf.refs != 'GO_REF:0000015' '''

        # IGC|xxxx IKR|7428294 ISM|3251497 ISA|3251496 ISS|114 ISO|3251466
        elif subsection == 'F':
                addSQL = 'and ec._term_key in (7428294,3251497,3251496,114,3251466,114159318)' 
                addSQL += '''\nand gaf.refs like 'PMID:%' '''
        # IGC|xxxx IKR|7428294 ISM|3251497 ISA|3251496 ISS|114 ISO|3251466
        elif subsection == 'F1':
                addSQL = 'and ec._term_key in (7428294,3251497,3251496,114,3251466,114159318)' 
                addSQL += '''\nand gaf.refs not like 'GO_REF:%' '''
        # IGC|xxxx IKR|7428294 ISM|3251497 ISA|3251496 ISS|114 ISO|3251466
        elif subsection == 'F2':
                addSQL = 'and ec._term_key in (7428294,3251497,3251496,114,3251466,114159318)' 
                addSQL += '''\nand gaf.refs = 'GO_REF:0000008' '''
        # IGC|xxxx IKR|7428294 ISM|3251497 ISA|3251496 ISS|114 ISO|3251466
        elif subsection == 'F3':
                addSQL = 'and ec._term_key in (7428294,3251497,3251496,114,3251466,114159318)' 
                addSQL += '''\nand gaf.refs = 'GO_REF:0000024' '''
        # IGC|xxxx IKR|7428294 ISM|3251497 ISA|3251496 ISS|114 ISO|3251466
        elif subsection == 'F4':
                addSQL = 'and ec._term_key in (7428294,3251497,3251496,114,3251466,114159318)' 
                addSQL += '''\nand gaf.refs = 'GO_REF:0000114' '''

        # IKR|7428294 ISM|3251497 ISA|3251496 ISS|114 ISO|3251466
        elif subsection == 'G':
                addSQL = 'and ec._term_key in (7428294,3251497,3251496,114,3251466)'
        # ISO|3251466
        elif subsection == 'H':
                addSQL = 'and ec._term_key in (3251466)'
        # IBA|7428292
        elif subsection == 'I':
                addSQL = 'and ec._term_key in (7428292)'
        # IEA|115
        elif subsection == 'J':
                addSQL = 'and ec._term_key in (115)'

        db.sql('''
                select gaf.mgiid, gaf.assignedBy as groupBy, d._dag_key, d.name
                into temporary table validGenes
                from gafAnnotations gaf, ACC_Accession a, VOC_Term ec, DAG_Node n, DAG_DAG d
                where gaf.goid = a.accid
                and a._logicaldb_key = 31
                and gaf.evidenceCode = ec.abbreviation
                and ec._vocab_key = 3
                %s
                and a._object_key = n._object_key
                and n._dag_key = d._dag_key
                and d._dag_key in (1,2,3,4)
                and exists (select 1 from validMarkers m where gaf.mgiid = m.mgiid and m.predictedGene = 'No')
                ''' % (addSQL), None)

        db.sql('create index validGenes_idx on validGenes (mgiid)', None)

        db.sql('''
                select gaf.mgiid, gaf.assignedBy as groupBy, d._dag_key, d.name
                into temporary table validPredicted
                from gafAnnotations gaf, ACC_Accession a, VOC_Term ec, DAG_Node n, DAG_DAG d
                where gaf.goid = a.accid
                and a._logicaldb_key = 31
                and gaf.evidenceCode = ec.abbreviation
                and ec._vocab_key = 3
                %s
                and a._object_key = n._object_key
                and n._dag_key = d._dag_key
                and d._dag_key in (1,2,3,4)
                and exists (select 1 from validMarkers m where gaf.mgiid = m.mgiid and m.predictedGene = 'Yes')
                ''' % (addSQL), None)

        db.sql('create index validPredicted_idx on validPredicted (mgiid)', None)

        # 
        # select the columns from gafAnnotations that are needed to determine a distinct Annotation row
        # the Annotation rows will be counted by DAG name/groupBy
        # to change the distinct Annotation row logic, add or remove the proper gafAnnotations column to this set:
        #
        #       !2  **DB Object ID (MGI ID)
        #       !4  **Qualifier
        #       !5  **GO ID
        #       !6  **DB:Reference (|DB:Reference)
        #       !7  **Evidence Code              
        #       !8  **With (or) From             
        #       !15 **Assigned By                
        #       !16 **Annotation Extension
        #       !17 **Gene Product Form ID (proteoform)
        #       + _dag_key, name
        #
        # addSQL is used to determine the specific set of evidence codes used for a given A-J subsection
        #
        db.sql('''
                select distinct gaf.mgiid, gaf.qualifier, gaf.goid, gaf.refs, 
                        gaf.evidenceCode, gaf.inferredFrom, gaf.assignedBy as groupBy, gaf.extensions, gaf.proteoform,
                        d._dag_key, d.name
                into temporary table validAnnotations
                from gafAnnotations gaf, ACC_Accession a, VOC_Term ec, DAG_Node n, DAG_DAG d
                where gaf.goid = a.accid
                and a._logicaldb_key = 31
                and gaf.evidenceCode = ec.abbreviation
                and ec._vocab_key = 3
                %s
                and a._object_key = n._object_key
                and n._dag_key = d._dag_key
                and d._dag_key in (1,2,3,4)
                and exists (select 1 from validMarkers m where gaf.mgiid = m.mgiid)
                ''' % (addSQL), None)

        db.sql('create index validAnnotations_idx1 on validAnnotations (mgiid)', None)
        db.sql('create index validAnnotations_idx2 on validAnnotations (goid)', None)

#
# end: creating temp tables
#

#
# start: processing
#

def processDag(results):
        #
        # used by processSection2(), processSection3()
        # load the dagResults by groupBy and return
        #

        dagResults = {}

        for r in results:
                key = r['groupBy']
                value = r
                if key not in dagResults:
                        dagResults[key] = []
                dagResults[key].append(value)

        #print(dagResults)
        return dagResults

def processSection1():
        #
        # GO Ontology Summary
        # number of GO terms per ontology
        # number of GO terms per ontology used in MGI
        #

        # header for section 1

        fp.write('includes: all GO annotations' + 2*CRT)
        fp.write('\'Predicted genes\' are those that:' + CRT)
        fp.write('- have a name that starts with the words \'gene model\'' + CRT)
        fp.write('- have a name that starts with the words \'predicted gene\'' + CRT)
        fp.write('- have a name that starts with the words \'gene trap\'' + CRT)
        fp.write('- have a symbol that starts with the word \'ORF\'' + CRT)
        fp.write('- have a symbol that is a single letter followed by up to 5 numbers, for example \'a12345\'' + CRT)
        fp.write('- have a symbol that is two letters followed by up to 5 numbers, for example \'ab12345\'' + CRT)
        fp.write(CRT)
        fp.write('This report is best viewed by importing into Excel')
        fp.write(2*CRT)
        fp.write(3*TAB + 'Biological Process' + TAB + 'Cellular Component' + TAB + 'Molecular Function' + CRT)

        results = db.sql('''
                select d._dag_key, d.name, count(distinct a._term_key) as counter
                from VOC_Term a, DAG_Node n, DAG_DAG d
                where a._Vocab_key = 4
                and a._Term_key = n._Object_key
                and n._DAG_key = d._DAG_key
                and d._dag_key in (1,2,3)
                group by d.name, d._dag_key
                order by d.name
        ''', 'auto')

        fp.write('Gene Ontology Summary - Number of GO Terms per Ontology' + 2*TAB)
        for r in results:
                fp.write(TAB + str(r['counter']))
        fp.write(CRT)

        results = db.sql('''
                select d._dag_key, d.name, count(distinct gaf.goid) as counter
                from gafAnnotations gaf, ACC_Accession a, DAG_Node n, DAG_DAG d
                where gaf.goid = a.accid
                and a._logicaldb_key = 31
                and a._object_key = n._Object_key
                and n._DAG_key = d._DAG_key
                and d._dag_key in (1,2,3)
                and exists (select 1 from validMarkers m where gaf.mgiid = m.mgiid)
                group by d.name, d._dag_key
                order by d.name
        ''', 'auto')

        fp.write('Gene Ontology Summary - Number of GO Terms per Ontology Used in MGI' + 2*TAB)
        for r in results:
                fp.write(TAB + str(r['counter']))
        fp.write(2*CRT)

def processSection2():
        #
        # Section II - Counts by Features types
        #
        # A: All Annotations
        # B: Protein Coding Features
        # C: RNA Features
        # D: Pseudogenic Features
        # E: Other Features
        #

        fp.write(CRT + 'All Annotations' + CRT)
        createTempSection2('A')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(2,'A')

        fp.write(CRT + 'Protein Coding Features' + CRT)
        createTempSection2('B')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(2,'B')

        fp.write(CRT + 'RNA Features' + CRT)
        createTempSection2('C')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(2,'C')

        fp.write(CRT + 'Pseudogenic Features' + CRT)
        createTempSection2('D')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(2,'D')

        fp.write(CRT + 'Other Features' + CRT)
        createTempSection2('E')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(2,'E')

        return

def processSection3():
        #
        # Section III - Counts by "Assigned By"
        #
        # A: Experimental Annotations (EXP, IDA, IEP, IGI, IMP, or IPI) by Contributor (assigned by)
        # B: High-throughput Annotations (HTP, HDA, HMP, HGI, or HEP) by Contributor (assigned by)
        # C: Curator/Author Statement Annotations (IC, TAS, NAS) by Contributor (assigned by)
        # D: Total RCA Annotations by Contributor (assigned by)
        # E: Root Annotations (ND) by Contributor (assigned by)
        # E1: Root Annotations (ND & GO_REFS:0000015) by Contributor (assigned by)
        # E2: Other Root Annotations (ND & NOT GO_REFS:0000015) by Contributor (assigned by)
        # F: Manual Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO) from PMIDs by Contributor (assigned by)
        # F1: Manual Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO) from non-GO_REF references by Contributor (assigned by)
        # F2: Manual Sequence Annotations with GO_REF:0000008 (J:73065)
        # F3: Manual Sequence Annotations with GO_REF:0000024
        # F4: Manual Sequence Annotations with GO_REF:0000114
        # G: Manual Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO) using GO_REFs by GO_REF & Contributor (assigned by)
        #

        fp.write(CRT + 'Experimental Annotations (EXP,IDA,IEP,IGI,IMP,IPI) by Contributor' + CRT)
        createTempSection3('A')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'A')

        fp.write(CRT + 'High-throughput Annotations (HTP, HDA, HMP, HGI, or HEP) by Contributor' + CRT)
        createTempSection3('B')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'B')

        fp.write(CRT + 'Curator/Author Statement Annotations (IC, TAS, NAS) by Contributor' + CRT)
        createTempSection3('C')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'C')

        fp.write(CRT + 'Total RCA Annotations by Contributor' + CRT)
        createTempSection3('D')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'D')

        fp.write(CRT + 'Root Annotations (ND)' + CRT)
        createTempSection3('E')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'E')

        fp.write(CRT + 'Root Annotations (ND) with GO_REF:0000015 - Use of the ND evidence code' + CRT)
        createTempSection3('E1')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'E1')

        fp.write(CRT + 'Other Root Annotations (ND & NOT GO_REF:0000015) by Contributor' + CRT)
        createTempSection3('E2')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'E2')

        fp.write(CRT + 'Manual Sequence Annotations' + CRT)
        createTempSection3('F')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'F')

        fp.write(CRT + 'Manual Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO) from non-GO_REF references by Contributor' + CRT)
        createTempSection3('F1')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'F2')

        fp.write(CRT + 'Manual Sequence Annotations with GO_REF:0000008 (J:73065) - Gene Ontology annotation by the MGI curatorial staff, curated orthology' + CRT)
        createTempSection3('F2')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'F2')

        fp.write(CRT + 'Manual Sequence Annotations with GO_REF:0000024 - Manual transfer of experimentally-verified manual GO annotation data to orthologs by curator judgment of sequence similarity.' + CRT)
        createTempSection3('F3')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'F3')

        fp.write(CRT + 'Manual Sequence Annotations with GO_REF:0000114 - Manual transfer of experimentally-verified manual GO annotation data to homologous complexes by curator judgment of sequence, composition and function similarity' + CRT)
        createTempSection3('F4')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'F4')

def processSectionGene():
        #
        # section 2 : process the genes : validGenes
        # section 3 : process the genes : validGenes
        #

        global totalGene, dagGene, totalSummary

        print('processSectionGene:CDEFG,3-7')

        totalSummary = {}

        results = db.sql('''
                select groupBy, count(distinct mgiid) as counter from validGenes group by groupBy order by groupBy
        ''', 'auto')
        for r in results:
                key = r['groupBy']
                value = r['counter']
                totalGene[key] = []
                totalGene[key].append(value)
                
        results = db.sql(''' 
                select 'C' as column, count(distinct mgiid) as counter from validGenes 
        ''', 'auto')
        for r in results:
                key = r['column']
                value = r['counter']
                totalSummary[key] = []
                totalSummary[key].append(value)
                
        results = db.sql('''
                select _dag_key, name, count(distinct mgiid) as counter from validGenes group by name, _dag_key
        ''', 'auto')
        for r in results:
                if r['_dag_key'] == 3:
                        key = 'D'
                elif r['_dag_key'] == 1:
                        key = 'E'
                elif r['_dag_key'] == 2:
                        key = 'F'
                else:
                        key = 'G'
                value = r['counter']
                totalSummary[key] = []
                totalSummary[key].append(value)
                
        results = db.sql('''
                (
                select _dag_key, name, groupBy, count(distinct mgiid) as counter
                from validGenes
                group by name, _dag_key, groupBy
                union
                select distinct 1 as _dag_key, 'Cellular Component' as name, groupBy, 0 as counter
                from validGenes v1 where not exists (select 1 from validGenes v2 where v1.groupBy = v2.groupBy and v2._dag_key in (1))
                union
                select distinct 2 as _dag_key, 'Molecular Function' as name, groupBy, 0 as counter
                from validGenes v1 where not exists (select 1 from validGenes v2 where v1.groupBy = v2.groupBy and v2._dag_key in (2))
                union
                select distinct 3 as _dag_key, 'Biological Process' as name, groupBy, 0 as counter
                from validGenes v1 where not exists (select 1 from validGenes v2 where v1.groupBy = v2.groupBy and v2._dag_key in (3))
                union
                select distinct 4 as _dag_key, 'Obsolete' as name, groupBy, 0 as counter
                from validGenes v1 where not exists (select 1 from validGenes v2 where v1.groupBy = v2.groupBy and v2._dag_key in (4))
                )
                order by groupBy, name
        ''', 'auto')
        dagGene = processDag(results)

def processSectionPredicted():
        #
        # section 3 : process the predicted genes : validPredicted
        #

        global totalPredicted, dagPredicted, totalSummary

        print('processSectionPredicted:HIJKL,8-12')

        results = db.sql('''
                select groupBy, count(distinct mgiid) as counter from validPredicted group by groupBy order by groupBy
        ''', 'auto')
        for r in results:
                key = r['groupBy']
                value = r['counter']
                totalPredicted[key] = []
                totalPredicted[key].append(value)
                
        results = db.sql('''
                select 'H' as column, count(distinct mgiid) as counter from validPredicted
        ''', 'auto')
        for r in results:
                key = r['column']
                value = r['counter']
                totalSummary[key] = []
                totalSummary[key].append(value)
                
        results = db.sql('''
                select _dag_key, name, count(distinct mgiid) as counter from validPredicted group by name, _dag_key
        ''', 'auto')
        
        for r in results:
                if r['_dag_key'] == 3:
                        key = 'I'
                elif r['_dag_key'] == 1:
                        key = 'J'
                elif r['_dag_key'] == 2:
                        key = 'K'
                else:
                        key = 'L'
                value = r['counter']
                totalSummary[key] = []
                totalSummary[key].append(value)
                
        results = db.sql('''
                (
                select _dag_key, name, groupBy, count(distinct mgiid) as counter
                from validPredicted
                group by name, _dag_key, groupBy
                union
                select distinct 1 as _dag_key, 'Cellular Component' as name, groupBy, 0 as counter
                from validPredicted v1 where not exists (select 1 from validPredicted v2 where v1.groupBy = v2.groupBy and v2._dag_key in (1))
                union
                select distinct 2 as _dag_key, 'Molecular Function' as name, groupBy, 0 as counter
                from validPredicted v1 where not exists (select 1 from validPredicted v2 where v1.groupBy = v2.groupBy and v2._dag_key in (2))
                union
                select distinct 3 as _dag_key, 'Biological Process' as name, groupBy, 0 as counter
                from validPredicted v1 where not exists (select 1 from validPredicted v2 where v1.groupBy = v2.groupBy and v2._dag_key in (3))
                union
                select distinct 4 as _dag_key, 'Obsolete' as name, groupBy, 0 as counter
                from validPredicted v1 where not exists (select 1 from validPredicted v2 where v1.groupBy = v2.groupBy and v2._dag_key in (4))
                )
                order by groupBy, name
        ''', 'auto')
        dagPredicted = processDag(results)

def processSectionTotal(section, subsection):
        #
        # process the total annotations : validAnnotations
        # where subsection in A-J
        #

        global totalAll, dagAll, totalSummary

        print('processSectionTotal:MNOPQ,13-17')

        results = db.sql('''
                select groupBy, count(*) as counter from validAnnotations where mgiid is not null group by groupBy order by groupBy
        ''', 'auto')
        for r in results:
                key = r['groupBy']
                value = r['counter']
                totalAll[key] = []
                totalAll[key].append(value)
        #print(totalAll)

        results = db.sql('''
                select 'M' as column, count(*) as counter from validAnnotations where mgiid is not null
        ''', 'auto')
        for r in results:
                key = r['column']
                value = r['counter']
                totalSummary[key] = []
                totalSummary[key].append(value)
        #print(totalSummary)

        results = db.sql('''
                select _dag_key, name, count(*) as counter from validAnnotations where mgiid is not null group by name, _dag_key
        ''', 'auto')
        for r in results:
                if r['_dag_key'] == 3:
                        key = 'N'
                elif r['_dag_key'] == 1:
                        key = 'O'
                elif r['_dag_key'] == 2:
                        key = 'P'
                else:
                        key = 'Q'
                value = r['counter']
                totalSummary[key] = []
                totalSummary[key].append(value)
                
        results = db.sql('''
                (
                select _dag_key, name, groupBy, count(*) as counter
                from validAnnotations
                group by name, _dag_key, groupBy
                union
                select distinct 1 as _dag_key, 'Cellular Component' as name, groupBy, 0 as counter
                from validAnnotations v1 where not exists (select 1 from validAnnotations v2 where v1.groupBy = v2.groupBy and v2._dag_key in (1))
                union
                select distinct 2 as _dag_key, 'Molecular Function' as name, groupBy, 0 as counter
                from validAnnotations v1 where not exists (select 1 from validAnnotations v2 where v1.groupBy = v2.groupBy and v2._dag_key in (2))
                union
                select distinct 3 as _dag_key, 'Biological Process' as name, groupBy, 0 as counter
                from validAnnotations v1 where not exists (select 1 from validAnnotations v2 where v1.groupBy = v2.groupBy and v2._dag_key in (3))
                union
                select distinct 4 as _dag_key, 'Obsolete' as name, groupBy, 0 as counter
                from validAnnotations v1 where not exists (select 1 from validAnnotations v2 where v1.groupBy = v2.groupBy and v2._dag_key in (4))
                )
                order by groupBy, name
        ''', 'auto')

        dagAll = processDag(results)
        #print(dagAll)

        if section == 2:
                if subsection == 'A':
                        displayType = 'All Annotations'
                elif subsection == 'B':
                        displayType = 'Protein Coding Features'
                elif subsection == 'C':
                        displayType = 'RNA Features'
                elif subsection == 'D':
                        displayType = 'Pseudogenic Features'
                elif subsection == 'E':
                        displayType = 'Other Features'
        elif section == 3:
                if subsection == 'A':
                        displayType = 'Experimental'
                elif subsection == 'B':
                        displayType = 'High-throughput'
                elif subsection == 'C':
                        displayType = 'Curator/Author Statement'
                elif subsection == 'D':
                        displayType = 'RCA'
                elif subsection == 'E':
                        displayType = 'Root'
                elif subsection == 'E1':
                        displayType = 'Root'
                elif subsection == 'E2':
                        displayType = 'Root'
                elif subsection == 'F':
                        displayType = 'Manual Sequence'
                elif subsection == 'F1':
                        displayType = 'Manual Sequence'
                elif subsection == 'F2':
                        displayType = 'Manual Sequence'
                elif subsection == 'F3':
                        displayType = 'Manual Sequence'
                elif subsection == 'F4':
                        displayType = 'Manual Sequence'

        # for each groupBy
        #       CDEFG,3-7   : Total # of Genes
        #       HIJKL,8-12  : Total # of Predicted Genes
        #       MNOPQ,13-17 : Total # of Annotations
        for groupBy in dagAll:

                # section 2/subsection 'A' -> skip
                if section == 2 and subsection == 'A':
                        continue

                fp.write(TAB + str(groupBy) + TAB)

                # dags for given groupBy, print total, b, c, m, obsolete
                if groupBy in dagGene:
                        totalCount = totalGene[groupBy][0]
                        fp.write(str(totalCount) + TAB)
                        dags = dagGene[groupBy]
                        for d in dags:
                                fp.write(str(d['counter']) + TAB)
                else:
                        fp.write("0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB)

                if groupBy in dagPredicted:
                        totalCount = totalPredicted[groupBy][0]
                        fp.write(str(totalCount) + TAB)
                        dags = dagPredicted[groupBy]
                        for d in dags:
                                fp.write(str(d['counter']) + TAB)
                else:
                        fp.write("0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB)

                if groupBy in dagAll and groupBy in totalAll:
                        totalCount = totalAll[groupBy][0]
                        fp.write(str(totalCount) + TAB)
                        dags = dagAll[groupBy]
                        for d in dags:
                                fp.write(str(d['counter']) + TAB)
                else:
                        fp.write("0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB)

                if section == 2:
                        fp.write('Feature type' + TAB + displayType + CRT)
                elif section == 3:
                        fp.write('Evidence type' + TAB + displayType + CRT)

        if section == 2:
                if subsection == 'A':
                        fp.write(TAB + 'Total All Annotations' + TAB)
                elif subsection == 'B':
                        fp.write(TAB + 'Total protein coding features' + TAB)
                elif subsection == 'C':
                        fp.write(TAB + 'Total RNA features' + TAB)
                elif subsection == 'D':
                        fp.write(TAB + 'Total Pseudogenic features' + TAB)
                elif subsection == 'E':
                        fp.write(TAB + 'Total other features' + TAB)
        elif section == 3:
                if subsection == 'A':
                        fp.write(TAB + 'Total Experimental Annotations (EXP,IDA,IEP,IGI,IMP,IPI)' + TAB)
                elif subsection == 'B':
                        fp.write(TAB + 'Total High-throughput Annotations (HTP, HDA, HMP, HGI, or HEP)' + TAB)
                elif subsection == 'C':
                        fp.write(TAB + 'Total Curator/Author Statement Annotations (IC, TAS, NAS)' + TAB)
                elif subsection == 'D':
                        fp.write(TAB + 'Total RCA Annotations' + TAB)
                elif subsection == 'E':
                        fp.write(TAB + 'All Root Annotations (ND)' + TAB)
                elif subsection == 'E1':
                        fp.write(TAB + 'Total Root Annotations (ND & GO_REF:0000015)' + TAB)
                elif subsection == 'E2':
                        fp.write(TAB + 'Total Root Annotations (ND & NOT GO_REF:0000015)' + TAB)
                elif subsection == 'F':
                        fp.write(TAB + 'Total Manual Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO) from PMIDs' + TAB)
                elif subsection == 'F1':
                        fp.write(TAB + 'Total Manual Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO) from non-GO_REF' + TAB)
                elif subsection == 'F2':
                        fp.write(TAB + 'Total Manual Sequence Annotations with GO_REF:0000008 (J:73065)' + TAB)
                elif subsection == 'F3':
                        fp.write(TAB + 'Total Manual Sequence Annotations with GO_REF:0000024' + TAB)
                elif subsection == 'F4':
                        fp.write(TAB + 'Total Manual Sequence Annotations with GO_REF:0000114' + TAB)

        outputCols = ['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q']
        for c in outputCols: 
                if c not in totalSummary:
                        fp.write('0' + TAB)
                else:
                        fp.write(str(totalSummary[c][0]) + TAB)

        if section == 2:
                fp.write('Feature type' + TAB + 'Summary Row' + CRT)
        elif section == 3:
                fp.write('Evidence type' + TAB + 'Summary Row' + CRT)

#
# end: processing
#

def printHeader():
        #
        # the header for section 2,3
        #

        fp.write(str.ljust('Annotation Category', 25) + TAB)
        fp.write('Contribor, Feature Type, or Summary row description' + TAB)
        fp.write('Total Number of Genes Annotated:' + TAB)
        fp.write('Biological Process' + TAB)
        fp.write('Cellular Component' + TAB)
        fp.write('Molecular Funcation' + TAB)
        fp.write('Obsolete' + TAB)
        fp.write('Total Number of Predicted Genes Annotated:' + TAB)
        fp.write('Biological Process' + TAB)
        fp.write('Cellular Component' + TAB)
        fp.write('Molecular Funcation' + TAB)
        fp.write('Obsolete' + TAB)
        fp.write('Total Number of Annotations:' + TAB)
        fp.write('Biological Process' + TAB)
        fp.write('Cellular Component' + TAB)
        fp.write('Molecular Funcation' + TAB)
        fp.write('Obsolete' + TAB)
        fp.write('Classification Axis' + TAB)
        fp.write('Sorting Classification' + CRT)

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])
createTempGAF()
createTempMarkers()
processSection1()
printHeader()
processSection2()
processSection3()
db.sql('drop table if exists gafAnnotations;', None)
db.commit()
reportlib.finish_nonps(fp)

