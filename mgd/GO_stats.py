
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

        db.sql('''
                WITH markers AS (
                        select distinct m.*, t.term as featureType
                        from MRK_Marker m, VOC_Annot va, VOC_Term t
                        where m._Marker_key = va._Object_key
                        and va._AnnotType_key = 1011    -- MCV/Marker
                        and va._Term_key = t._Term_key
                        and exists (select 1 from VOC_Annot gva where gva._annottype_key = 1000 and m._marker_key = gva._object_key)
                )
                select m.*, 'Yes' as predictedGene
                into temporary table validMarkers
                from markers m
                where m._organism_key = 1
                and m._marker_status_key = 1
                and (
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
                where m._organism_key = 1
                and m._marker_status_key = 1
                and m.name not like 'gene model %'
                and m.name not like 'gene trap %'
                and m.name not like 'predicted gene%'
                and m.symbol not like 'ORF%'
                and m.symbol !~ '[A-Z][0-9][0-9][0-9][0-9][0-9]'
                and m.symbol !~ '[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]'
                ''', None)

        db.sql('create index validMarkers_idx on validMarkers (_Marker_key)', None)

        db.sql('''
                select a._object_key, d._dag_key, d.name, u.login
                into temporary table validGenes
                from VOC_Annot a, VOC_Evidence e, DAG_Node n, DAG_DAG d, MGI_User u
                where d._dag_key in (1,2,3,4)
                and d._dag_key = n._dag_key
                and n._Object_key = a._Term_key
                and a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key
                and e._EvidenceTerm_key in (4003114,109,117,112,110,111)
                and e._ModifiedBy_key = u._User_key
                and exists (select 1 from validMarkers m where a._Object_key = m._Marker_key and m.predictedGene = 'No')
                ''', None)

        db.sql('create index validGenes_idx on validGenes (_object_key)', None)

        db.sql('''
                select a._object_key, d._dag_key, d.name, u.login
                into temporary table validPredicted
                from VOC_Annot a, VOC_Evidence e, DAG_Node n, DAG_DAG d, MGI_User u
                where d._dag_key in (1,2,3,4)
                and d._dag_key = n._dag_key
                and n._Object_key = a._Term_key
                and a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key
                and e._EvidenceTerm_key in (4003114,109,117,112,110,111)
                and e._ModifiedBy_key = u._User_key
                and exists (select 1 from validMarkers m where a._Object_key = m._Marker_key and m.predictedGene = 'Yes')
                ''', None)

        db.sql('create index validPredicted_idx on validPredicted (_object_key)', None)

        db.sql('''
                select a._annot_key, d._dag_key, d.name, u.login
                into temporary table validAnnotations
                from VOC_Annot a, VOC_Evidence e, DAG_Node n, DAG_DAG d, MGI_User u
                where d._dag_key in (1,2,3,4)
                and d._dag_key = n._dag_key
                and n._Object_key = a._Term_key
                and a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key
                and e._EvidenceTerm_key in (4003114,109,117,112,110,111)
                and e._ModifiedBy_key = u._User_key
                and exists (select 1 from validMarkers m where a._Object_key = m._Marker_key)
                ''', None)

        db.sql('create index validAnnotations_idx on validAnnotations (_annot_key)', None)

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
                select d._dag_key, d.name, count(distinct a._term_key) as counter
                from VOC_Annot a, DAG_Node n, DAG_DAG d
                where a._AnnotType_key = 1000
                and a._Term_key = n._Object_key
                and n._DAG_key = d._DAG_key
                and d._dag_key in (1,2,3)
                and exists (select 1 from validMarkers m where a._Object_key = m._Marker_key)
                group by d.name, d._dag_key
                order by d.name
        ''', 'auto')

        fp.write('Gene Ontology Summary - Number of GO Terms per Ontology Used in MGI' + 3*TAB)
        for r in results:
                fp.write(TAB + str(r['counter']))
        fp.write(2*CRT)

def processDag(results):

        dagResults = {}

        for r in results:
                key = r['login']
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
                select login, count(distinct _object_key) as counter from validGenes group by login order by login
        ''', 'auto')
        for r in results:
                key = r['login']
                value = r['counter']
                totalGene[key] = []
                totalGene[key].append(value)
                
        results = db.sql(''' 
                select 'D' as column, count(distinct _object_key) as counter from validGenes 
        ''', 'auto')
        for r in results:
                key = r['column']
                value = r['counter']
                totalSummary[key] = []
                totalSummary[key].append(value)
                
        results = db.sql('''
                select _dag_key, name, count(distinct _object_key) as counter from validGenes group by name, _dag_key
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
                select _dag_key, name, login, count(distinct _object_key) as counter
                from validGenes
                group by name, _dag_key, login
                union
                select distinct 1 as _dag_key, 'Cellular Component' as name, login, 0 as counter
                from validGenes v1 where not exists (select 1 from validGenes v2 where v1.login = v2.login and v2._dag_key in (1))
                union
                select distinct 2 as _dag_key, 'Molecular Function' as name, login, 0 as counter
                from validGenes v1 where not exists (select 1 from validGenes v2 where v1.login = v2.login and v2._dag_key in (2))
                union
                select distinct 3 as _dag_key, 'Biological Process' as name, login, 0 as counter
                from validGenes v1 where not exists (select 1 from validGenes v2 where v1.login = v2.login and v2._dag_key in (3))
                union
                select distinct 4 as _dag_key, 'Obsolete' as name, login, 0 as counter
                from validGenes v1 where not exists (select 1 from validGenes v2 where v1.login = v2.login and v2._dag_key in (4))
                )
                order by login, name
        ''', 'auto')
        dagGene = processDag(results)

def getExperimentalPredicted():
        global totalPredicted, dagPredicted, totalSummary

        print('IJKLM,9-13 : Total # of Predicted Genes')

        results = db.sql('''
                select login, count(distinct _object_key) as counter from validPredicted group by login order by login
        ''', 'auto')
        for r in results:
                key = r['login']
                value = r['counter']
                totalPredicted[key] = []
                totalPredicted[key].append(value)
                
        results = db.sql('''
                select 'I' as column, count(distinct _object_key) as counter from validPredicted
        ''', 'auto')
        for r in results:
                key = r['column']
                value = r['counter']
                totalSummary[key] = []
                totalSummary[key].append(value)
                
        results = db.sql('''
                select _dag_key, name, count(distinct _object_key) as counter from validPredicted group by name, _dag_key
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
                select _dag_key, name, login, count(distinct _object_key) as counter
                from validPredicted
                group by name, _dag_key, login
                union
                select distinct 1 as _dag_key, 'Cellular Component' as name, login, 0 as counter
                from validPredicted v1 where not exists (select 1 from validPredicted v2 where v1.login = v2.login and v2._dag_key in (1))
                union
                select distinct 2 as _dag_key, 'Molecular Function' as name, login, 0 as counter
                from validPredicted v1 where not exists (select 1 from validPredicted v2 where v1.login = v2.login and v2._dag_key in (2))
                union
                select distinct 3 as _dag_key, 'Biological Process' as name, login, 0 as counter
                from validPredicted v1 where not exists (select 1 from validPredicted v2 where v1.login = v2.login and v2._dag_key in (3))
                union
                select distinct 4 as _dag_key, 'Obsolete' as name, login, 0 as counter
                from validPredicted v1 where not exists (select 1 from validPredicted v2 where v1.login = v2.login and v2._dag_key in (4))
                )
                order by login, name
        ''', 'auto')
        dagPredicted = processDag(results)

def getExperimentalTotal():
        global totalAll, dagAll, totalSummary

        print('NOPQR,14-18: Total # of Annotations')

        results = db.sql('''
                select login, count(_annot_key) as counter from validAnnotations group by login order by login
        ''', 'auto')
        for r in results:
                key = r['login']
                value = r['counter']
                totalAll[key] = []
                totalAll[key].append(value)
        #print(totalAll)

        results = db.sql('''
                select 'N' as column, count(_annot_key) as counter from validAnnotations
        ''', 'auto')
        for r in results:
                key = r['column']
                value = r['counter']
                totalSummary[key] = []
                totalSummary[key].append(value)
                
        results = db.sql('''
                select _dag_key, name, count(_annot_key) as counter from validAnnotations group by name, _dag_key
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
                select _dag_key, name, login, count(distinct _annot_key) as counter
                from validAnnotations
                group by name, _dag_key, login
                union
                select distinct 1 as _dag_key, 'Cellular Component' as name, login, 0 as counter
                from validAnnotations v1 where not exists (select 1 from validAnnotations v2 where v1.login = v2.login and v2._dag_key in (1))
                union
                select distinct 2 as _dag_key, 'Molecular Function' as name, login, 0 as counter
                from validAnnotations v1 where not exists (select 1 from validAnnotations v2 where v1.login = v2.login and v2._dag_key in (2))
                union
                select distinct 3 as _dag_key, 'Biological Process' as name, login, 0 as counter
                from validAnnotations v1 where not exists (select 1 from validAnnotations v2 where v1.login = v2.login and v2._dag_key in (3))
                union
                select distinct 4 as _dag_key, 'Obsolete' as name, login, 0 as counter
                from validAnnotations v1 where not exists (select 1 from validAnnotations v2 where v1.login = v2.login and v2._dag_key in (4))
                )
                order by login, name
        ''', 'auto')

        dagAll = processDag(results)
        #print(dagAll)

        # for each login
        #       DEFGH,4-8  : Total # of Genes
        #       IJKLM,9-13 : Total # of Predicted Genes
        #       NOPQR,14-18: Total # of Annotations
        for login in dagAll:

                fp.write(2*TAB + str(login) + TAB)

                # dags for given login, print total, b, c, m, obsolete
                if login in dagGene:
                        totalCount = totalGene[login][0]
                        fp.write(str(totalCount) + TAB)
                        dags = dagGene[login]
                        for d in dags:
                                fp.write(str(d['counter']) + TAB)
                else:
                        fp.write("0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB)

                if login in dagPredicted:
                        totalCount = totalPredicted[login][0]
                        fp.write(str(totalCount) + TAB)
                        dags = dagPredicted[login]
                        for d in dags:
                                fp.write(str(d['counter']) + TAB)
                else:
                        fp.write("0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB + "0" + TAB)

                if login in dagAll:
                        totalCount = totalAll[login][0]
                        fp.write(str(totalCount) + TAB)
                        dags = dagAll[login]
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

reportlib.finish_nonps(fp)
