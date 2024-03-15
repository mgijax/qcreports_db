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
# A: Experimental Annotations (EXP, IDA, IEP, IGI, IMP, or IPI) by Contributor 
# B: High-throughput Annotations (HTP, HDA, HMP, HGI, or HEP) by Contributor
# C: Curator/Author Statement Annotations (IC, TAS, NAS) by Contributor
# D: Total RCA Annotations by Contributor
# E1: Root Annotations (ND & GO_REFS:0000015) by Contributor
# E2: Other Root Annotations (ND & NOT GO_REFS:0000015) by Contributor
#
# F: Manual Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO)
# F1: Manual Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO) from non-GO_REF references by Contributor
# F2: Manual Sequence Annotations with GO_REF:0000008 (J:73065) by Contributor
# F3: Manual Sequence Annotations with GO_REF:0000024 by Contributor
# F4: Manual Sequence Annotations with GO_REF:0000114 by Contributor
#
# G: All Computational Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO)
# G1: Computational ISO with GO_REF:0000096 - Rat to Mouse ISO GO transfer 
# G2: Computational ISO with GO_REF:0000119 - Human to Mouse ISO GO transfer
#
# H: Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO) NOT using any of: 
#       GO_REF:0000008, GO_REF:0000096, GO_REF:0000119, GO_REF:0000024, GO_REF:0000114
#
# I: not used
#
# J1: Phylogenetic annotations (IBA using GO_REF:0000033) by Contributor
# J2: Phylogenetic annotations (IBA NOT using GO_REF:0000033) by Contributor
#
# K: IEA methods by Reference & Contributor (assigned by)
# K1: GO_REF:0000107 - IEAs to orthologs using Ensembl Compara.
# K2: GO_REF:0000002 -IEAs based on InterPro record links with GO terms.
# K3: GO_REF:0000116 -IEAs based on Rhea mapping.
# K4: GO_REF:0000003 - IEAs based on Enzyme Commission mapping
# K5: GO_REF:0000118 - IEAs from TreeGrafter
# K6: GO_REF:0000104 - IEAs for related proteins with shared sequence features
# K7: GO_REF:0000117 - IEAs created by ARBA machine learning models
# K8: GO_REF:0000043 - IEAs based on UniProtKB/Swiss-Prot keyword mapping
# K9: GO_REF:0000044 - IEAs based on UniProtKB/Swiss-Prot Subcellular Location vocabulary 
# K10: GO_REF:0000041 - IEAs based on UniPathway vocabulary mapping
# K11: IEA Annotations NOT using any of: 
#       GO_REF:0000002, GO_REF:0000003, GO_REF:0000041, GO_REF:0000043, GO_REF:0000044, GO_REF:0000104, GO_REF:0000107, GO_REF:0000116, GO_REF:0000117, GO_REF:0000118
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
        # !12 **DB Object Type
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

def closeTempGAF():
        #
        # close temp table gafAnnotations
        #

        db.sql('drop table if exists gafAnnotations;', None)
        db.commit()

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
                        select distinct a.accid as mgiid, m.symbol, m.name, gaf.dbType as featureType
                        from MRK_Marker m, ACC_Accession a, gafAnnotations gaf
                        where m._marker_key = a._object_key
                        and a._mgitype_key = 2
                        and a._logicaldb_key = 1
                        and a.prefixPart = 'MGI:'
                        and a.preferred = 1
                        and m._organism_key = 1
                        and m._marker_status_key = 1
                        and a.accid = gaf.mgiid
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
        # see overview at top of script
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
                addSQL = '''and gaf.dbType in (
                        'gene segment', 
                        'protein coding gene'
                        ) 
                        '''
        # RNA features
        elif subsection == 'C':
                addSQL = '''and gaf.dbType in (
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
                addSQL = '''and gaf.dbType in (
                        'polymorphic pseudogene', 
                        'pseudogene', 
                        'pseudogenic gene segment'
                        )
                        '''

        # other features
        elif subsection == 'E':
                addSQL = '''and gaf.dbType in (
                        'biological_region',
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
        # see overview at top of script
        #
        # validGenes      : set of marker by dag where predited = 'No'
        # validPredicted  : set of marker by dag where predicted = 'Yes'
        # validAnnoations : set of annotations by dag
        #

        db.sql('drop table if exists validGenes;', None)
        db.sql('drop table if exists validPredicted;', None)
        db.sql('drop table if exists validAnnotations;', None)

        if subsection == 'A':
                addSQL = '''and gaf.evidenceCode in ('EXP', 'IDA', 'IEP', 'IGI', 'IMP', 'IPI') '''

        elif subsection == 'B':
                addSQL = '''and gaf.evidenceCode in ('HTP', 'HDA', 'HEP', 'HGI', 'HMP') '''

        elif subsection == 'C':
                addSQL = '''and gaf.evidenceCode in ('IC', 'TAS', 'NAS') '''

        elif subsection == 'D':
                addSQL = '''and gaf.evidenceCode in ('RCA') '''

        elif subsection == 'E1':
                addSQL = '''and gaf.evidenceCode in ('ND') and gaf.refs = 'GO_REF:0000015' '''
        elif subsection == 'E2':
                addSQL = '''and gaf.evidenceCode in ('ND') and gaf.refs != 'GO_REF:0000015' '''

        elif subsection == 'F':
                addSQL = '''and gaf.evidenceCode in ('IKR', 'IGC', 'ISM', 'ISA', 'ISS', 'ISO') '''
                addSQL += '''and (gaf.refs not like 'GO_REF:%' '''
                addSQL += '''or gaf.refs in ('GO_REF:0000008', 'GO_REF:0000024', 'GO_REF:0000114')) '''
        elif subsection == 'F1':
                addSQL = '''and gaf.evidenceCode in ('IKR', 'IGC', 'ISM', 'ISA', 'ISS', 'ISO') '''
                addSQL += '''and gaf.refs not like 'GO_REF:%' '''
        elif subsection == 'F2':
                addSQL = '''and gaf.evidenceCode in ('IKR', 'IGC', 'ISM', 'ISA', 'ISS', 'ISO') '''
                addSQL += '''and gaf.refs = 'GO_REF:0000008' '''
        elif subsection == 'F3':
                addSQL = '''and gaf.evidenceCode in ('IKR', 'IGC', 'ISM', 'ISA', 'ISS', 'ISO') '''
                addSQL += '''and gaf.refs = 'GO_REF:0000024' '''
        elif subsection == 'F4':
                addSQL = '''and gaf.evidenceCode in ('IKR', 'IGC', 'ISM', 'ISA', 'ISS', 'ISO') '''
                addSQL += '''and gaf.refs = 'GO_REF:0000114' '''

        elif subsection == 'G':
                addSQL = '''and gaf.evidenceCode in ('IKR', 'IGC', 'ISM', 'ISA', 'ISS', 'ISO') '''
                addSQL += '''and gaf.refs in ('GO_REF:0000096', 'GO_REF:0000119') '''
        elif subsection == 'G1':
                addSQL = '''and gaf.evidenceCode in ('IKR', 'IGC', 'ISM', 'ISA', 'ISS', 'ISO') and gaf.refs = 'GO_REF:0000096' '''
        elif subsection == 'G2':
                addSQL = ''' and gaf.evidenceCode in ('IKR', 'IGC', 'ISM', 'ISA', 'ISS', 'ISO') and gaf.refs = 'GO_REF:0000119' '''

        elif subsection == 'H':
                addSQL = '''and gaf.evidenceCode in ('IKR', 'IGC', 'ISM', 'ISA', 'ISS', 'ISO') '''
                addSQL += '''and gaf.refs like 'GO_REF%' '''
                addSQL += '''and gaf.refs not in ('GO_REF:0000008', 'GO_REF:0000096', 'GO_REF:0000119', 'GO_REF:0000024', 'GO_REF:0000114') '''

        elif subsection == 'J1':
                addSQL = '''and gaf.evidenceCode in ('IBA') '''
        elif subsection == 'J2':
                addSQL = '''and gaf.evidenceCode in ('IBA') '''
                addSQL += '''and gaf.refs = 'GO_REF:0000033' '''

        elif subsection == 'K':
                addSQL = '''and gaf.evidenceCode in ('IEA') '''
        elif subsection == 'K1':
                addSQL = '''and gaf.evidenceCode in ('IEA') and gaf.refs = 'GO_REF:0000107' '''
        elif subsection == 'K2':
                addSQL = '''and gaf.evidenceCode in ('IEA') and gaf.refs = 'GO_REF:0000002' '''
        elif subsection == 'K3':
                addSQL = '''and gaf.evidenceCode in ('IEA') and gaf.refs = 'GO_REF:0000116' '''
        elif subsection == 'K4':
                addSQL = '''and gaf.evidenceCode in ('IEA') and gaf.refs = 'GO_REF:0000003' '''
        elif subsection == 'K5':
                addSQL = '''and gaf.evidenceCode in ('IEA') and gaf.refs = 'GO_REF:0000118' '''
        elif subsection == 'K6':
                addSQL = '''and gaf.evidenceCode in ('IEA') and gaf.refs = 'GO_REF:0000104' '''
        elif subsection == 'K7':
                addSQL = '''and gaf.evidenceCode in ('IEA') and gaf.refs = 'GO_REF:0000117' '''
        elif subsection == 'K8':
                addSQL = '''and gaf.evidenceCode in ('IEA') and gaf.refs = 'GO_REF:0000043' '''
        elif subsection == 'K9':
                addSQL = '''and gaf.evidenceCode in ('IEA') and gaf.refs = 'GO_REF:0000044' '''
        elif subsection == 'K10':
                addSQL = '''and gaf.evidenceCode in ('IEA') and gaf.refs = 'GO_REF:0000041' '''
        elif subsection == 'K11':
                addSQL = '''and gaf.evidenceCode in ('IEA') '''
                addSQL += '''and gaf.refs not in ('GO_REF:0000002', 'GO_REF:0000003', 'GO_REF:0000041', 'GO_REF:0000043', 'GO_REF:0000044', 'GO_REF:0000104', 'GO_REF:0000107', 'GO_REF:0000116', 'GO_REF:0000117', 'GO_REF:0000118') '''

        db.sql('''
                select gaf.mgiid, gaf.assignedBy as groupBy, d._dag_key, d.name
                into temporary table validGenes
                from gafAnnotations gaf, ACC_Accession a, DAG_Node n, DAG_DAG d
                where gaf.goid = a.accid
                and a._logicaldb_key = 31
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

        #results = db.sql('select distinct mgiid from validAnnotations order by mgiid', 'auto')
        #for r in results:
        #        fp.write(r['mgiid'] + CRT)
        #return

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
        # A-K
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

        fp.write(CRT + 'Computational Sequence Annotations' + CRT)
        createTempSection3('G')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'G')

        fp.write(CRT + 'Computational ISO with GO_REF:0000096 - Rat to Mouse ISO GO transfer' + CRT)
        createTempSection3('G1')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'G1')

        fp.write(CRT + 'Computational ISO with GO_REF:0000119 - Human to Mouse ISO GO transfer' + CRT)
        createTempSection3('G2')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'G2')

        fp.write(CRT + 'Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO) using a GO_REF NOT using any of: GO_REF:0000008, GO_REF:0000096, GO_REF:0000119, GO_REF:0000024, GO_REF:000011' + CRT)
        createTempSection3('H')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'H')

        fp.write(CRT + 'Phylogenetic annotations (IBA) using GO_REF:0000033' + CRT)
        createTempSection3('J1')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'J1')

        fp.write(CRT + 'Phylogenetic annotations (IBA) NOT using GO_REF:0000033' + CRT)
        createTempSection3('J2')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'J2')

        fp.write(CRT + 'IEA methods by Reference & Contributor (assigned by' + CRT)
        createTempSection3('K')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'K')

        fp.write(CRT + 'GO_REF:0000107 - IEAs to orthologs using Ensembl Compara' + CRT)
        createTempSection3('K1')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'K1')

        fp.write(CRT + 'GO_REF:0000002 -IEAs based on InterPro record links with GO terms' + CRT)
        createTempSection3('K2')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'K2')

        fp.write(CRT + 'GO_REF:0000116 -IEAs based on Rhea mapping' + CRT)
        createTempSection3('K3')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'K3')

        fp.write(CRT + 'GO_REF:0000003 - IEAs based on Enzyme Commission mapping' + CRT)
        createTempSection3('K4')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'K4')

        fp.write(CRT + 'GO_REF:0000118 - IEAs from TreeGrafte' + CRT)
        createTempSection3('K5')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'K5')

        fp.write(CRT + 'GO_REF:0000104 - IEAs for related proteins with shared sequence feature' + CRT)
        createTempSection3('K6')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'K6')

        fp.write(CRT + 'GO_REF:0000117 - IEAs created by ARBA machine learning model' + CRT)
        createTempSection3('K7')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'K7')

        fp.write(CRT + 'GO_REF:0000043 - IEAs based on UniProtKB/Swiss-Prot keyword mappin' + CRT)
        createTempSection3('K8')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'K8')

        fp.write(CRT + 'GO_REF:0000044 - IEAs based on UniProtKB/Swiss-Prot Subcellular Location vocabulary' + CRT)
        createTempSection3('K9')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'K9')

        fp.write(CRT + 'GO_REF:0000041 - IEAs based on UniPathway vocabulary mappin' + CRT)
        createTempSection3('K10')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'K10')

        fp.write(CRT + 'IEA Annotations NOT using any of: GO_REF:0000002, GO_REF:0000003, GO_REF:0000041, GO_REF:0000043, GO_REF:0000044, GO_REF:0000104, GO_REF:0000107, GO_REF:0000116, GO_REF:0000117, GO_REF:000011' + CRT)
        createTempSection3('K11')
        processSectionGene()
        processSectionPredicted()
        processSectionTotal(3,'K11')

def processSectionGene():
        #
        # gene section CDEFG,3-7
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
        # predicted section HIJKL,8-12
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
        # MNOPQ,13-17
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
                elif subsection == 'E1':
                        displayType = 'Root'
                elif subsection == 'E2':
                        displayType = 'Root'
                elif subsection == 'F':
                        displayType = 'Manual Sequence'
                elif subsection == 'F1':
                        displayType = 'Manual Sequence - non GO_REF'
                elif subsection == 'F2':
                        displayType = 'Manual Sequence - non GO_REF'
                elif subsection == 'F3':
                        displayType = 'Manual Sequence - to orthologs by curator judgement'
                elif subsection == 'F4':
                        displayType = 'Manual Sequence - to complexes by curator judgement'
                elif subsection == 'G':
                        displayType = 'Computational SO'
                elif subsection == 'G1':
                        displayType = 'Computational SO: Rat to Mouse'
                elif subsection == 'G2':
                        displayType = 'Computational SO: Human to Mouse'
                elif subsection in ('H'):
                        displayType = 'Sequence annotations with unexpected GO_REF(s)'
                elif subsection in ('J1'):
                        displayType = 'Phylogenetic annotations (IBA) using GO_REF:0000033'
                elif subsection in ('J2'):
                        displayType = 'Phylogenetic annotations (IBA) NOT using GO_REF:0000033'
                elif subsection in ('K'):
                        displayType = 'Group summary'
                elif subsection in ('K1'):
                        displayType = 'IEAs from GO_REF:0000107 - Ensembl Compara'
                elif subsection in ('K2'):
                        displayType = 'IEAs from GO_REF:0000002 - InterPro to GO mapping'
                elif subsection in ('K3'):
                        displayType = 'IEAs from GO_REF:0000116 - Rhea mapping'
                elif subsection in ('K4'):
                        displayType = 'IEAs from GO_REF:0000003 - Enzyme Commission mapping'
                elif subsection in ('K5'):
                        displayType = 'IEAs from GO_REF:0000118 - TreeGrafter'
                elif subsection in ('K6'):
                        displayType = 'IEAs from GO_REF:0000104 - related proteins with shared sequence features'
                elif subsection in ('K7'):
                        displayType = 'IEAs from GO_REF:0000117 - ARBA machine learning models'
                elif subsection in ('K8'):
                        displayType = 'IEAs from  GO_REF:0000043 - UniProtKB/Swiss-Prot keyword mapping'
                elif subsection in ('K9'):
                        displayType = 'IEAs from  GO_REF:0000044 - UniProtKB/Swiss-Prot Subcellular Location vocabulary mapping'
                elif subsection in ('K10'):
                        displayType = 'IEAs from  GO_REF:0000041 - UniPathway vocabulary mapping'
                elif subsection in ('K11'):
                        displayType = 'IEAs from unexpected GO_REF(s)'

        # for each groupBy
        #       CDEFG,3-7   : Total # of Genes
        #       HIJKL,8-12  : Total # of Predicted Genes
        #       MNOPQ,13-17 : Total # of Annotations
        for groupBy in dagAll:

                # section 2/subsection 'A' -> skip
                if section == 2 and subsection == 'A':
                        continue
                # section 3/subsection 'F', 'G', 'K' -> skip
                if section == 3 and subsection in ('F', 'G', 'K'):
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
                classificationAxis = 'Feature type'
                if subsection == 'A':
                        sortingClassification = 'Summary Row for Group'
                else:
                        sortingClassification = 'Summary Row'
        elif section == 3:
                if subsection == 'A':
                        fp.write(TAB + 'Total Experimental Annotations (EXP,IDA,IEP,IGI,IMP,IPI)' + TAB)
                elif subsection == 'B':
                        fp.write(TAB + 'Total High-throughput Annotations (HTP, HDA, HMP, HGI, or HEP)' + TAB)
                elif subsection == 'C':
                        fp.write(TAB + 'Total Curator/Author Statement Annotations (IC, TAS, NAS)' + TAB)
                elif subsection == 'D':
                        fp.write(TAB + 'Total RCA Annotations' + TAB)
                elif subsection == 'E1':
                        fp.write(TAB + 'Total Root Annotations (ND & GO_REF:0000015)' + TAB)
                elif subsection == 'E2':
                        fp.write(TAB + 'Total Root Annotations (ND & NOT GO_REF:0000015)' + TAB)
                elif subsection == 'F':
                        fp.write(TAB + 'Total Manual Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO)' + TAB)
                elif subsection == 'F1':
                        fp.write(TAB + 'Total Manual Sequence Annotations (IKR, IGC, ISM, ISA, ISS, or ISO) from non-GO_REF' + TAB)
                elif subsection == 'F2':
                        fp.write(TAB + 'Total Manual Sequence Annotations with a non-GO_REF' + TAB)
                elif subsection == 'F3':
                        fp.write(TAB + 'Total Manual Sequence Annotations with GO_REF:0000024' + TAB)
                elif subsection == 'F4':
                        fp.write(TAB + 'Total Manual Sequence Annotations with GO_REF:0000114' + TAB)
                elif subsection == 'G':
                        fp.write(TAB + 'Total Computational Sequence Annotations' + TAB)
                elif subsection == 'G1':
                        fp.write(TAB + 'Computational ISO with GO_REF:0000096 - Rat to Mouse ISO GO transfer' + TAB)
                elif subsection == 'G2':
                        fp.write(TAB + 'Computational ISO with GO_REF:0000119 - Human to Mouse ISO GO transfer' + TAB)
                elif subsection == 'H':
                        fp.write(TAB + 'Sequence annotations with unexpected GO_REF(s)' + TAB)
                elif subsection == 'J1':
                        fp.write(TAB + 'Total Phylogenetic annotations (IBA) using GO_REF:0000033' + TAB)
                elif subsection == 'J2':
                        fp.write(TAB + 'Total Phylogenetic annotations (IBA) & NOT GO_REF:0000033' + TAB)
                elif subsection == 'K':
                        fp.write(TAB + 'All Electronic Annotations (IEA)' + TAB)
                elif subsection == 'K1':
                        fp.write(TAB + 'Total IEAs from GO_REF:0000107 - Ensembl Compara' + TAB)
                elif subsection == 'K2':
                        fp.write(TAB + 'Total IEAs from GO_REF:0000002 - InterPro to GO mapping' + TAB)
                elif subsection == 'K3':
                        fp.write(TAB + 'Total IEAs from GO_REF:0000116 - Rhea mapping' + TAB)
                elif subsection == 'K4':
                        fp.write(TAB + 'Total IEAs from GO_REF:0000003 - Enzyme Comission mapping' + TAB)
                elif subsection == 'K5':
                        fp.write(TAB + 'Total IEAs from GO_REF:0000118 - TreeGrafter' + TAB)
                elif subsection == 'K6':
                        fp.write(TAB + 'Total IEAs from GO_REF:0000104 - related proteins with shared sequence features' + TAB)
                elif subsection == 'K7':
                        fp.write(TAB + 'Total IEAs from GO_REF:0000117 - ARBA machine learning models' + TAB)
                elif subsection == 'K8':
                        fp.write(TAB + 'Total IEAs from GO_REF:0000043 - UniProtKB/Swiss-Prot keyword mapping' + TAB)
                elif subsection == 'K9':
                        fp.write(TAB + 'Total IEAs from GO_REF:0000044 - UniProtKB/Swiss-Prot Subcellular Location vocabulary ' + TAB)
                elif subsection == 'K10':
                        fp.write(TAB + 'Total IEAs from GO_REF:0000041 - UniPathway vocabulary mapping' + TAB)
                elif subsection == 'K11':
                        fp.write(TAB + 'Total IEAs from unexpected GO_REF(s)' + TAB)

                classificationAxis = 'Evidence type'
                if subsection in ('F', 'J', 'G', 'K'):
                        sortingClassification = 'Summary Row for Group'
                else:
                        sortingClassification = 'Summary Row'

        outputCols = ['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q']
        for c in outputCols: 
                if c not in totalSummary:
                        fp.write('0' + TAB)
                else:
                        fp.write(str(totalSummary[c][0]) + TAB)

        # R,18: Classification Axis, S,19: Sorting Classification
        fp.write(classificationAxis + TAB + sortingClassification + CRT)

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
closeTempGAF()
reportlib.finish_nonps(fp)

