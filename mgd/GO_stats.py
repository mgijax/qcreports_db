'''
#
# GO_stats.py
#
# 1    : Annotation Category
# 2    : GO_REF
# 3    : Contribor, Feature Type, or Summary row description
# DEFGH,4-8  : Total # of Genes
# IJKLM,9-13 : Total # of Predicted Genes
# NOPQR,14-18: Total # of Annotations
# S,19   : Classification Axis
# T,20   : Sorting Classification
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

def createTempTables():
        #
        # validMarkers    : distinct set of markers used for all reports
        # validGenes      : set of marker by dag where predited = 'No'
        # validPredicted  : set of marker by dag where predicted = 'Yes'
        # validAnnoations : set of annotations by dag
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

        #!1  DB
        #!2  DB Object ID
        #!3  DB Object Symbol
        #!4  Qualifier
        #!5  GO ID
        #!6  DB:Reference (|DB:Reference)
        #!7  Evidence Code
        #!8  With (or) From
        #!9  Aspect
        #!10 DB Object Name
        #!11 DB Object Synonym (|Synonym)
        #!12 DB Object Type
        #!13 Taxon(|taxon)
        #!14 Date
        #!15 Assigned By
        #!16 Annotation Extension
        #!17 Gene Product Form ID

        #db.sql('drop table if exists gafAnnotations;', None)
        #db.sql('''
        #create table gafAnnotations (
        #        db text,
        #        mgiid text,
        #        dbSymbol text,
        #        qualifier text,
        #        goid text,
        #        dbRefs text,
        #        evidenceCode text,
        #        inferredFrom text,
        #        aspect text,
        #        dbName text,
        #        dbSynonyms text,
        #        dbType text,
        #        taxon text,
        #        dbDate text,
        #        assignedBy text,
        #        extensions text,
        #        proteoform text
        #);
        #''', None)
        #db.commit()
        #gafFileName = os.environ['QCREPORTDIR'] + '/output/gene_association.mgi'
        #db.bcp(gafFileName, 'gafAnnotations')
        #db.commit()
        #db.sql('create index gaf_idx1 on gafAnnotations (mgiid)', None)
        #db.sql('create index gaf_idx2 on gafAnnotations (goid)', None)

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

        db.sql('''
                select gaf.mgiid, gaf.assignedBy, d._dag_key, d.name
                into temporary table validGenes
                from gafAnnotations gaf, ACC_Accession a, VOC_Term ec, DAG_Node n, DAG_DAG d
                where gaf.goid = a.accid
                and a._logicaldb_key = 31
                and gaf.evidenceCode = ec.abbreviation
                and ec._vocab_key = 3
                and ec._term_key in (4003114,109,117,112,110,111)
                and a._object_key = n._object_key
                and n._dag_key = d._dag_key
                and d._dag_key in (1,2,3,4)
                and exists (select 1 from validMarkers m where gaf.mgiid = m.mgiid and m.predictedGene = 'No')
                ''', None)

        db.sql('create index validGenes_idx on validGenes (mgiid)', None)

        db.sql('''
                select gaf.mgiid, gaf.assignedBy, d._dag_key, d.name
                into temporary table validPredicted
                from gafAnnotations gaf, ACC_Accession a, VOC_Term ec, DAG_Node n, DAG_DAG d
                where gaf.goid = a.accid
                and a._logicaldb_key = 31
                and gaf.evidenceCode = ec.abbreviation
                and ec._vocab_key = 3
                and ec._term_key in (4003114,109,117,112,110,111)
                and a._object_key = n._object_key
                and n._dag_key = d._dag_key
                and d._dag_key in (1,2,3,4)
                and exists (select 1 from validMarkers m where gaf.mgiid = m.mgiid and m.predictedGene = 'Yes')
                ''', None)

        db.sql('create index validPredicted_idx on validPredicted (mgiid)', None)

        # interested in distinct annotations
        # from the GAF (gene_association.mgi)
        #2 = Marker ID          
        #4 = Qualifier          
        #5 = GO ID              
        #6 = Reference          
        #7 = Evidence code      
        #8 = Inferred from      
        #17 = Proteoform

        db.sql('''
                select distinct gaf.mgiid, gaf.goid, gaf.dbRefs, gaf.qualifier, gaf.evidenceCode, gaf.inferredFrom, gaf.proteoform, gaf.assignedBy,
                        d._dag_key, d.name
                into temporary table validAnnotations
                from gafAnnotations gaf, ACC_Accession a, VOC_Term ec, DAG_Node n, DAG_DAG d
                where gaf.goid = a.accid
                and a._logicaldb_key = 31
                and gaf.evidenceCode = ec.abbreviation
                and ec._vocab_key = 3
                and ec._term_key in (4003114,109,117,112,110,111)
                and a._object_key = n._object_key
                and n._dag_key = d._dag_key
                and d._dag_key in (1,2,3,4)
                and exists (select 1 from validMarkers m where gaf.mgiid = m.mgiid)
                ''', None)

        db.sql('create index validAnnotations_idx1 on validAnnotations (mgiid)', None)
        db.sql('create index validAnnotations_idx2 on validAnnotations (goid)', None)

def goSummary():
        #
        # GO Ontology Summary
        # number of GO terms per ontology
        # number of GO terms per ontology used in MGI
        #

        fp.write(4*TAB + 'Biological Process' + TAB + 'Cellular Component' + TAB + 'Molecular Function' + CRT)

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

        fp.write('Gene Ontology Summary - Number of GO Terms per Ontology' + 3*TAB)
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

        fp.write('Gene Ontology Summary - Number of GO Terms per Ontology Used in MGI' + 3*TAB)
        for r in results:
                fp.write(TAB + str(r['counter']))
        fp.write(2*CRT)

def processDag(results):
        #
        # load the dagResults by assignedBy and return
        #

        dagResults = {}

        for r in results:
                key = r['assignedBy']
                value = r
                if key not in dagResults:
                        dagResults[key] = []
                dagResults[key].append(value)

        #print(dagResults)
        return dagResults

def getExperimental():
        #
        # classification: Experimental
        #

        fp.write(CRT + 'Experimental Annotations (EXP,IDA,IEP,IGI,IMP,IPI) by Contributor' + CRT)

        getExperimentalGene()
        getExperimentalPredicted()
        getExperimentalTotal()

def getExperimentalGene():
        global totalGene, dagGene, totalSummary

        print('DEFGH,4-8  : Total # of Genes')

        results = db.sql('''
                select assignedBy, count(distinct mgiid) as counter from validGenes group by assignedBy order by assignedBy
        ''', 'auto')
        for r in results:
                key = r['assignedBy']
                value = r['counter']
                totalGene[key] = []
                totalGene[key].append(value)
                
        results = db.sql(''' 
                select 'D' as column, count(distinct mgiid) as counter from validGenes 
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
                        key = 'E'
                elif r['_dag_key'] == 1:
                        key = 'F'
                elif r['_dag_key'] == 2:
                        key = 'G'
                else:
                        key = 'H'
                value = r['counter']
                totalSummary[key] = []
                totalSummary[key].append(value)
                
        results = db.sql('''
                (
                select _dag_key, name, assignedBy, count(distinct mgiid) as counter
                from validGenes
                group by name, _dag_key, assignedBy
                union
                select distinct 1 as _dag_key, 'Cellular Component' as name, assignedBy, 0 as counter
                from validGenes v1 where not exists (select 1 from validGenes v2 where v1.assignedBy = v2.assignedBy and v2._dag_key in (1))
                union
                select distinct 2 as _dag_key, 'Molecular Function' as name, assignedBy, 0 as counter
                from validGenes v1 where not exists (select 1 from validGenes v2 where v1.assignedBy = v2.assignedBy and v2._dag_key in (2))
                union
                select distinct 3 as _dag_key, 'Biological Process' as name, assignedBy, 0 as counter
                from validGenes v1 where not exists (select 1 from validGenes v2 where v1.assignedBy = v2.assignedBy and v2._dag_key in (3))
                union
                select distinct 4 as _dag_key, 'Obsolete' as name, assignedBy, 0 as counter
                from validGenes v1 where not exists (select 1 from validGenes v2 where v1.assignedBy = v2.assignedBy and v2._dag_key in (4))
                )
                order by assignedBy, name
        ''', 'auto')
        dagGene = processDag(results)

def getExperimentalPredicted():
        global totalPredicted, dagPredicted, totalSummary

        print('IJKLM,9-13 : Total # of Predicted Genes')

        results = db.sql('''
                select assignedBy, count(distinct mgiid) as counter from validPredicted group by assignedBy order by assignedBy
        ''', 'auto')
        for r in results:
                key = r['assignedBy']
                value = r['counter']
                totalPredicted[key] = []
                totalPredicted[key].append(value)
                
        results = db.sql('''
                select 'I' as column, count(distinct mgiid) as counter from validPredicted
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
                        key = 'J'
                elif r['_dag_key'] == 1:
                        key = 'K'
                elif r['_dag_key'] == 2:
                        key = 'L'
                else:
                        key = 'M'
                value = r['counter']
                totalSummary[key] = []
                totalSummary[key].append(value)
                
        results = db.sql('''
                (
                select _dag_key, name, assignedBy, count(distinct mgiid) as counter
                from validPredicted
                group by name, _dag_key, assignedBy
                union
                select distinct 1 as _dag_key, 'Cellular Component' as name, assignedBy, 0 as counter
                from validPredicted v1 where not exists (select 1 from validPredicted v2 where v1.assignedBy = v2.assignedBy and v2._dag_key in (1))
                union
                select distinct 2 as _dag_key, 'Molecular Function' as name, assignedBy, 0 as counter
                from validPredicted v1 where not exists (select 1 from validPredicted v2 where v1.assignedBy = v2.assignedBy and v2._dag_key in (2))
                union
                select distinct 3 as _dag_key, 'Biological Process' as name, assignedBy, 0 as counter
                from validPredicted v1 where not exists (select 1 from validPredicted v2 where v1.assignedBy = v2.assignedBy and v2._dag_key in (3))
                union
                select distinct 4 as _dag_key, 'Obsolete' as name, assignedBy, 0 as counter
                from validPredicted v1 where not exists (select 1 from validPredicted v2 where v1.assignedBy = v2.assignedBy and v2._dag_key in (4))
                )
                order by assignedBy, name
        ''', 'auto')
        dagPredicted = processDag(results)

def getExperimentalTotal():
        global totalAll, dagAll, totalSummary

        print('NOPQR,14-18: Total # of Annotations')

        results = db.sql('''
                select assignedBy, count(*) as counter from validAnnotations group by assignedBy order by assignedBy
        ''', 'auto')
        for r in results:
                key = r['assignedBy']
                value = r['counter']
                totalAll[key] = []
                totalAll[key].append(value)
        #print(totalAll)

        results = db.sql('''
                select 'N' as column, count(*) as counter from validAnnotations
        ''', 'auto')
        for r in results:
                key = r['column']
                value = r['counter']
                totalSummary[key] = []
                totalSummary[key].append(value)
                
        results = db.sql('''
                select _dag_key, name, count(*) as counter from validAnnotations group by name, _dag_key
        ''', 'auto')
        for r in results:
                if r['_dag_key'] == 3:
                        key = 'O'
                elif r['_dag_key'] == 1:
                        key = 'P'
                elif r['_dag_key'] == 2:
                        key = 'Q'
                else:
                        key = 'R'
                value = r['counter']
                totalSummary[key] = []
                totalSummary[key].append(value)
                
        results = db.sql('''
                (
                select _dag_key, name, assignedBy, count(*) as counter
                from validAnnotations
                group by name, _dag_key, assignedBy
                union
                select distinct 1 as _dag_key, 'Cellular Component' as name, assignedBy, 0 as counter
                from validAnnotations v1 where not exists (select 1 from validAnnotations v2 where v1.assignedBy = v2.assignedBy and v2._dag_key in (1))
                union
                select distinct 2 as _dag_key, 'Molecular Function' as name, assignedBy, 0 as counter
                from validAnnotations v1 where not exists (select 1 from validAnnotations v2 where v1.assignedBy = v2.assignedBy and v2._dag_key in (2))
                union
                select distinct 3 as _dag_key, 'Biological Process' as name, assignedBy, 0 as counter
                from validAnnotations v1 where not exists (select 1 from validAnnotations v2 where v1.assignedBy = v2.assignedBy and v2._dag_key in (3))
                union
                select distinct 4 as _dag_key, 'Obsolete' as name, assignedBy, 0 as counter
                from validAnnotations v1 where not exists (select 1 from validAnnotations v2 where v1.assignedBy = v2.assignedBy and v2._dag_key in (4))
                )
                order by assignedBy, name
        ''', 'auto')

        dagAll = processDag(results)
        #print(dagAll)

        # for each assignedBy
        #       DEFGH,4-8  : Total # of Genes
        #       IJKLM,9-13 : Total # of Predicted Genes
        #       NOPQR,14-18: Total # of Annotations
        for assignedBy in dagAll:

                fp.write(2*TAB + str(assignedBy) + TAB)

                # dags for given assignedBy, print total, b, c, m, obsolete
                if assignedBy in dagGene:
                        totalCount = totalGene[assignedBy][0]
                        fp.write(str(totalCount) + TAB)
                        dags = dagGene[assignedBy]
                        for d in dags:
                                fp.write(str(d['counter']) + TAB)
                else:
                        fp.write("0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB)

                if assignedBy in dagPredicted:
                        totalCount = totalPredicted[assignedBy][0]
                        fp.write(str(totalCount) + TAB)
                        dags = dagPredicted[assignedBy]
                        for d in dags:
                                fp.write(str(d['counter']) + TAB)
                else:
                        fp.write("0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB)

                if assignedBy in dagAll:
                        totalCount = totalAll[assignedBy][0]
                        fp.write(str(totalCount) + TAB)
                        dags = dagAll[assignedBy]
                        for d in dags:
                                fp.write(str(d['counter']) + TAB)
                else:
                        fp.write("0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB)

                fp.write('Evidence type' + TAB + 'Experimental' + CRT)

        fp.write(2*TAB + 'Total Experimental Annotations (EXP,IDA,IEP,IGI,IMP,IPI)' + TAB)
        fp.write(str(totalSummary['D'][0]) + TAB)
        fp.write(str(totalSummary['E'][0]) + TAB)
        fp.write(str(totalSummary['F'][0]) + TAB)
        fp.write(str(totalSummary['G'][0]) + TAB)

        if 'H' not in totalSummary:
                fp.write('0' + TAB)
        else:
                fp.write(str(totalSummary['H'][0]) + TAB)

        fp.write(str(totalSummary['I'][0]) + TAB)
        fp.write(str(totalSummary['J'][0]) + TAB)
        fp.write(str(totalSummary['K'][0]) + TAB)
        fp.write(str(totalSummary['L'][0]) + TAB)

        if 'M' not in totalSummary:
                fp.write('0' + TAB)
        else:
                fp.write(str(totalSummary['M'][0]) + TAB)

        fp.write(str(totalSummary['N'][0]) + TAB)
        fp.write(str(totalSummary['O'][0]) + TAB)
        fp.write(str(totalSummary['P'][0]) + TAB)
        fp.write(str(totalSummary['Q'][0]) + TAB)

        if 'R' not in totalSummary:
                fp.write('0' + TAB)
        else:
                fp.write(str(totalSummary['R'][0]) + TAB)

        fp.write('Evidence type' + TAB + 'Summary Row' + CRT)
#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

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

createTempTables()
goSummary()

fp.write(str.ljust('Annotation Category', 25) + TAB)
fp.write('GO_REF' + TAB)
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

getExperimental()

#db.sql('drop table if exists gafAnnotations;', None)

reportlib.finish_nonps(fp)
