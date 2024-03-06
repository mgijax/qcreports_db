'''
#
# GO_MGIGAF.py
#
# A MGI GAF file; used by GO_stats.py
#       
# GAF2.2 : see below
# fp.write('!gaf-version: 2.2\n')
#
# For GAF2.2
# If the annotation has the value GO:0008150 (biological_process) in column 5, 
#       then the value in column 4 should be involved_in.
# If the annotation has the value GO:0003674 (molecular_function) in column 5, 
#       then the value in column 4 should be enables.
# If the annotation has the value GO:0005575 (cellular_component) in column 5, 
#       then the value in column 4 should be is_active_in.
#
'''

import sys
import os
import mgi_utils
import reportlib
import db
import go_isoforms

goloadpath = os.environ['GOLOAD'] + '/lib'
sys.path.insert(0, goloadpath)
import ecolib

db.setTrace()

TAB = reportlib.TAB
CRT = reportlib.CRT

MGIPREFIX = 'MGI'

# see doSetup()
dag = {}
syns = {}
pubMedId = {}
doiId = {}

# mapping of load reference keys to GO_REF IDs/per TR11772
# see _LogicalDB_key = 185 (GO_REF)
goRefDict = {}

# gaf lookups
# see doGAFCol16() : list of column 16 object/evidence/printable format
# isoformProtein lookup
gafCol16Lookup = {}
isoformsProtein = {}

# translate dag to qualifier
dagQualifierGAF = {'C':'located_in', 'P':'acts_upstream_of_or_within', 'F':'enables'}
goQualifierGAF = {}

#
# begin doSetup1()
# query for all GO annotations
#
def doSetup1():

    #
    # retrieve data set to process
    #
    #   and m.symbol = 'Asap1'
    #   and m.symbol = 'Mbd2'
    #   and m.symbol = 'Adipoq'
    #   and m.symbol = 'Birc3'
    #	and m.symbol = 'Hk1'
    #

    db.sql('drop table if exists gomarker1', None)
    db.commit()

    db.sql('''
        -- any mouse marker that has feature types
        select distinct a._Term_key, t.term, ta.accID as termID, q.term as qualifier, a._Object_key, 
            e._AnnotEvidence_key, e.inferredFrom, e._EvidenceTerm_key, 
            e._Refs_key, e._CreatedBy_key, e._ModifiedBy_key, e.creation_date, e.modification_date,
            m.symbol, m.name, m._Marker_Type_key, vf.term as featureType
        into temporary table gomarker1 
        from VOC_Annot a, 
             ACC_Accession ta, 
             VOC_Term t, 
             VOC_Evidence e, 
             MRK_Marker m, 
             VOC_Annot v,
             VOC_Term vf,
             VOC_Term q,
             MGI_User u
        where a._AnnotType_key = 1000 
        and a._Annot_key = e._Annot_key 
        and a._Object_key = m._Marker_key 
        and m._Marker_Status_key = 1
        and a._Term_key = t._Term_key 
        and a._Term_key = ta._Object_key 
        and ta._MGIType_key = 13 
        and ta.preferred = 1 
        and m._Marker_key = v._Object_key
        and v._AnnotType_key = 1011
        and v._Term_key = vf._Term_key
        and a._Qualifier_key = q._Term_key 
        and e._ModifiedBy_key = u._User_key

        -- specific for complex/cluster/region as these do not have feature types
        union
        select distinct a._Term_key, t.term, ta.accID as termID, q.term as qualifier, a._Object_key, 
            e._AnnotEvidence_key, e.inferredFrom, e._EvidenceTerm_key, 
            e._Refs_key, e._CreatedBy_key, e._ModifiedBy_key, e.creation_date, e.modification_date,
            m.symbol, m.name, m._Marker_Type_key, 'biological_region'
        from VOC_Annot a, 
             ACC_Accession ta, 
             VOC_Term t, 
             VOC_Evidence e, 
             MRK_Marker m, 
             VOC_Term q,
             MGI_User u
        where a._AnnotType_key = 1000 
        and a._Annot_key = e._Annot_key 
        and a._Object_key = m._Marker_key 
        and m._Marker_Status_key = 1
        and m._Marker_Type_key = 10
        and a._Term_key = t._Term_key 
        and a._Term_key = ta._Object_key 
        and ta._MGIType_key = 13 
        and ta.preferred = 1 
        and a._Qualifier_key = q._Term_key 
        and e._ModifiedBy_key = u._User_key
        ''', None)
    db.sql('create index gomarker1_idx1 on gomarker1(_Object_key)', None)
    db.sql('create index gomarker1_idx2 on gomarker1(_EvidenceTerm_key)', None)
    db.sql('create index gomarker1_idx3 on gomarker1(_Refs_key)', None)
    db.sql('create index gomarker1_idx4 on gomarker1(_ModifiedBy_key)', None)
    db.sql('create index gomarker1_idx5 on gomarker1(_AnnotEvidence_key)', None)

    doSetup()

#
# begin doSetup2()
# query for all GO annotations except NOCTUA and GO_Central
#
def doSetup2():

    #
    # retrieve data set to process
    #
    #   and m.symbol = 'Asap1'
    #   and m.symbol = 'Mbd2'
    #   and m.symbol = 'Adipoq'
    #   and m.symbol = 'Birc3'
    #	and m.symbol = 'Hk1'
    #

    db.sql('drop table if exists gomarker1;', None)
    db.commit()

    db.sql('''
        -- any mouse marker that has feature types
        select distinct a._Term_key, t.term, ta.accID as termID, q.term as qualifier, a._Object_key, 
            e._AnnotEvidence_key, e.inferredFrom, e._EvidenceTerm_key, 
            e._Refs_key, e._CreatedBy_key, e._ModifiedBy_key, e.creation_date, e.modification_date,
            m.symbol, m.name, m._Marker_Type_key, vf.term as featureType
        into temporary table gomarker1 
        from VOC_Annot a, 
             ACC_Accession ta, 
             VOC_Term t, 
             VOC_Evidence e, 
             MRK_Marker m, 
             VOC_Annot v,
             VOC_Term vf,
             VOC_Term q,
             MGI_User u
        where a._AnnotType_key = 1000 
        and a._Annot_key = e._Annot_key 
        and a._Object_key = m._Marker_key 
        and m._Marker_Status_key = 1
        and a._Term_key = t._Term_key 
        and a._Term_key = ta._Object_key 
        and ta._MGIType_key = 13 
        and ta.preferred = 1 
        and m._Marker_key = v._Object_key
        and v._AnnotType_key = 1011
        and v._Term_key = vf._Term_key
        and a._Qualifier_key = q._Term_key 
        and e._ModifiedBy_key = u._User_key

        -- specific for complex/cluster/region as these do not have feature types
        union
        select distinct a._Term_key, t.term, ta.accID as termID, q.term as qualifier, a._Object_key, 
            e._AnnotEvidence_key, e.inferredFrom, e._EvidenceTerm_key, 
            e._Refs_key, e._CreatedBy_key, e._ModifiedBy_key, e.creation_date, e.modification_date,
            m.symbol, m.name, m._Marker_Type_key, 'biological_region'
        from VOC_Annot a, 
             ACC_Accession ta, 
             VOC_Term t, 
             VOC_Evidence e, 
             MRK_Marker m, 
             VOC_Term q,
             MGI_User u
        where a._AnnotType_key = 1000 
        and a._Annot_key = e._Annot_key 
        and a._Object_key = m._Marker_key 
        and m._Marker_Status_key = 1
        and m._Marker_Type_key = 10
        and a._Term_key = t._Term_key 
        and a._Term_key = ta._Object_key 
        and ta._MGIType_key = 13 
        and ta.preferred = 1 
        and a._Qualifier_key = q._Term_key 
        and e._ModifiedBy_key = u._User_key

        ''', None)
    db.sql('create index gomarker1_idx1 on gomarker1(_Object_key)', None)
    db.sql('create index gomarker1_idx2 on gomarker1(_EvidenceTerm_key)', None)
    db.sql('create index gomarker1_idx3 on gomarker1(_Refs_key)', None)
    db.sql('create index gomarker1_idx4 on gomarker1(_ModifiedBy_key)', None)
    db.sql('create index gomarker1_idx5 on gomarker1(_AnnotEvidence_key)', None)

    doSetup()

#
# begin doSetup()
#
def doSetup():
    global dag
    global syns
    global pubMedId, doiId
    global goQualifierGAF
    global goRefDict

    # since this is called twice...reset
    dag = {}
    syns = {}
    pubMedId = {}
    doiId = {}
    goQualifierGAF = {}
    goRefDict = {}

    #
    # retrieve all dag abbrevations for each term
    #
    results = db.sql('select distinct _Object_key, rtrim(dagAbbrev) as dagAbbrev from DAG_Node_View where _Vocab_key = 4', 'auto')
    for r in results:
        dag[r['_Object_key']] = r['dagAbbrev']

    #
    # retrieve synonyms for markers in data set
    #
    results = db.sql('''
        select distinct g._Object_key, s.synonym 
        from gomarker1 g, MGI_Synonym s, MGI_SynonymType st 
        where g._Object_key = s._Object_key 
        and s._MGIType_key = 2 
        and s._SynonymType_key = st._SynonymType_key 
        and st.synonymType = 'exact'
        order by g._Object_key
        ''', 'auto')
    for r in results:
        key = r['_Object_key']
        value = r['synonym']
        if key not in syns:
            syns[key] = []
        syns[key].append(value)

    #
    # resolve foreign keys and store in "results" table
    #
    db.sql('drop table if exists gomarker2', None)
    db.commit()
    db.sql('''
        select distinct g._Refs_key, g._Term_key, g.termID, g.qualifier, g.inferredFrom, 
            g._Object_key, g._AnnotEvidence_key, g._EvidenceTerm_key, g.symbol, g.name, g._Marker_Type_key, g.featureType,
            to_char(g.creation_date, 'YYYY-MM-DD') as cDate,
            to_char(g.modification_date, 'YYYY-MM-DD') as mDate,
            to_char(g.modification_date, 'YYYYMMDD') as gafDate,
            g._CreatedBy_key,
            g._ModifiedBy_key,
            ma.accID as markerID, 
            b.accID as refID, 
            rtrim(t.abbreviation) as evidenceCode, 
            u.login as assignedBy
        into temporary table gomarker2 
        from gomarker1 g, ACC_Accession ma, ACC_Accession b, VOC_Term t, MGI_User u 
        where g._Object_key = ma._Object_key 
        and ma._MGIType_key = 2 
        and ma.prefixPart = 'MGI:' 
        and ma._LogicalDB_key = 1 
        and ma.preferred = 1 
        and g._Refs_key = b._Object_key 
        and b._MGIType_key = 1 
        and b.prefixPart = 'MGI:' 
        and b._LogicalDB_key = 1 
        and g._EvidenceTerm_key = t._Term_key 
        and g._ModifiedBy_key = u._User_key
        ''', None)

    db.sql('create index gomarker2_idx1 on gomarker2(symbol)', None)
    db.sql('create index gomarker2_idx2 on gomarker2(_Refs_key)', None)
    db.sql('create index gomarker2_idx3 on gomarker2(_AnnotEvidence_key)', None)
    db.sql('create index gomarker2_idx4 on gomarker2(_Object_key)', None)
    db.sql('create index gomarker2_idx5 on gomarker2(_EvidenceTerm_key)', None)
    
    #
    # resolve PubMed IDs for References
    #
    results = db.sql('''
        select distinct r._Refs_key, a.pubmedid
        from gomarker2 r, BIB_Citation_Cache a
        where r._Refs_key = a._Refs_key 
        and a.pubmedid is not null
        ''', 'auto')
    for r in results:
        key = r['_Refs_key']
        value = r['pubmedid']
        pubMedId[key] = value

    #
    # resolve DOI IDs for References
    #
    results = db.sql('''
        select distinct r._Refs_key, a.doiid
        from gomarker2 r, BIB_Citation_Cache a
        where r._Refs_key = a._Refs_key 
        and a.doiid is not null
        ''', 'auto')
    for r in results:
        key = r['_Refs_key']
        value = r['doiid']
        doiId[key] = value

    #
    # gpadCol3 : go_qualifier_id
    # go_qualifier_id -> value -> RO id
    #
    results = db.sql('''
        select distinct a._AnnotEvidence_key, t.term, p.value, t2.note
        from gomarker2 a, VOC_Evidence_Property p,  VOC_Term t, VOC_Term t2
        where a._AnnotEvidence_key = p._AnnotEvidence_key
        and p._PropertyTerm_key = t._Term_key
        and t.term in ('go_qualifier_id')
        and p.value = t2.term
        and t2.note is not null
        ''', 'auto')
    for r in results:
        key = r['_AnnotEvidence_key']

        value = r['value']
        if key not in goQualifierGAF:
            goQualifierGAF[key] = []
        goQualifierGAF[key].append(value)

    #print(goQualifierGAF)

    results = db.sql('select _Object_key, accID from ACC_Accession where _LogicalDB_key = 185', 'auto')
    for r in results:
        key = r['_Object_key']
        value = r['accID']
        goRefDict[key] = value
    #print(goRefDict)

#
# end doSetup()
#

#
# begin doGAFCol16()
#
def doGAFCol16():

    global gafCol16Lookup

    #
    # list of object/evidence/stanza that are GO-properties
    #
    # objectKey = marker key:annotation/evidence key (must match objectKey in doGAFFinish())
    #
    # exclude: annotations where evidence = ISO (3251466)
    # exclude: certain properties
    #

    gafCol16Lookup = {}

    cmd = '''
    select r.symbol, r._Object_key, r._AnnotEvidence_key, t1.term as property, p.value, p.stanza
            from gomarker2 r, VOC_Evidence_Property p, VOC_Term t1, VOC_Term t2
            where r._EvidenceTerm_key = t2._Term_key
            and t2.abbreviation not in ('ISO')
            and r._AnnotEvidence_key = p._AnnotEvidence_key
            and p._PropertyTerm_key = t1._Term_key
            and t1.term not in (
                'anatomy',
                'cell type',
                'contributor',
                'dual-taxon ID',
                'evidence',
                'external ref',
                'go_qualifier_id',
                'go_qualifier_term',
                'individual',
                'model-state',
                'modification',
                'noctua-model-id',
                'target',
                'text'
            )
            and t2.note is not null
            order by r.symbol, 
                r._Object_key, 
                r._AnnotEvidence_key, 
                p.stanza, 
                p.sequenceNum,
                property
    '''

    results = db.sql(cmd, 'auto')
    stanza = 1

    for r in results:
        objectKey = str(r['_Object_key']) + ':' + str(r['_AnnotEvidence_key'])
        value = r['value'].replace('MGI:', 'MGI:MGI:')

        # xxxx ; zzzz -> zzzz
        tokens = value.split(';')
        value = tokens[-1]
        value = value.strip()

        # EMAPA:xxx TS:xxx -> EMAPA:xxx
        if value.startswith('EMAPA:'):
                value = value.split(' ')[0]

        if objectKey not in gafCol16Lookup:
                gafCol16Lookup[objectKey] = []
                stanza = 0

        if stanza == 0:
                sep = ''
        elif r['stanza'] != stanza:
                sep = '|'
        else:
                sep = ','

        gafCol16Lookup[objectKey].append(sep + r['property'] + '(' + value + ')')
        stanza = r['stanza']

    #print(gafCol16Lookup)

## end doGAFCol16()

#
# begin doIsoform()
#
def doIsoform():
    global isoformsProtein

    isoformsProtein = {}

    # Query the valid _term_keys for properties
    isoformProcessor = go_isoforms.Processor()
    sanctionedPropertyKeys = isoformProcessor.querySanctionedPropertyTermKeys()

    propertyKeyClause = ",".join([str(k) for k in sanctionedPropertyKeys])

    results = db.sql('''
        select r._Object_key, r._AnnotEvidence_key, p.value
        from gomarker2 r, VOC_Evidence_Property p
        where r._AnnotEvidence_key = p._AnnotEvidence_key
        and p._PropertyTerm_key in (%s)
        order by r._Object_key, r._AnnotEvidence_key, p.stanza, p.sequenceNum
        ''' % propertyKeyClause, 'auto')

    for r in results:
        key = str(r['_Object_key']) + ':' + str(r['_AnnotEvidence_key'])
        value = r['value']
        isoformValues = isoformProcessor.processValue(value)
        for isoform in isoformValues:
            isoformsProtein.setdefault(key, []).append(isoform)

    #print(isoformProtein)

#
# end doIsoform()
#

#
# begin doGAFFinish()
#
def doGAFFinish():

    #
    # process results
    #
    results = db.sql('select * from gomarker2 order by symbol, termID', 'auto')

    for r in results:

        reportRow = ''    

        if r['_Term_key'] not in dag:
            continue

        if dag[r['_Term_key']] not in dagQualifierGAF:
            continue

        objectKey = str(r['_Object_key']) + ':' + str(r['_AnnotEvidence_key'])
        key = r['_AnnotEvidence_key']

        #!1  DB               
        #!2  DB Object ID    
        #!3  DB Object Symbol
        reportRow = MGIPREFIX + TAB
        reportRow = reportRow + str(r['markerID']) + TAB
        reportRow = reportRow + r['symbol'] + TAB

        #
        # GO-Qualifier : value where GO-Property = “go_qualifier_id”
        # For example : GO-Property = “go_qualifier_id”, value = “part_of”
        #
        # MGI-Qualifier :  MGI original qualifier list before GO started
        #       empty
        #       NOT
        #       colocalizes_with
        #       NOT|colocalizes_with
        #       contributes_to
        #       NOT|contributes_to
        #
        # Default Qualifier:
        # {'C':'located_in', 'P':'acts_upstream_of_or_within', 'F':'enables'
        #
        # If the annotation has the value GO:0008150 (biological_process) in column 5, 
        #       then the value in column 4 should be involved_in.
        # else if the annotation has the value GO:0003674 (molecular_function) in column 5, 
        #       then the value in column 4 should be enables.
        # else if the annotation has the value GO:0005575 (cellular_component) in column 5, 
        #       then the value in column 4 should be is_active_in.
        # else if the Annotation contains a GO-Qualifier, then use the “go_qualifier”/value
        #       If MGI-Qualifier = NOT, then attach NOT to front of GO-Qualifier
        #       For example :  NOT|enables
        # else if the MGI-Qualifier = "NOT, then "NOT:" + Default Qualifier
        # else if the MGI-Qualifier is not empty, then use the MGI-Qualifier value
        # else if the Annotation/Inferred From contains “InterPro:”, then use “involved_in”
        # else use Default Qualifier
        #

        #!4  Qualifier      
        qualifier = ""
        createAnotherRow = 0
        if r['termID'] == 'GO:0008150':
                qualifier = 'involved_in'
        elif r['termID'] == 'GO:0003674':
                qualifier = 'enables'
        elif r['termID'] == 'GO:0005575':
                qualifier = 'is_active_in'
        elif key in goQualifierGAF:
            if r['qualifier'] == 'NOT':
               qualifier = 'NOT|'
            qualifier = qualifier + goQualifierGAF[key][0]
            # only one go_qualifier_id per row
            createAnotherRow = 1
        elif r['qualifier'] == 'NOT':
            qualifier = 'NOT|' + dagQualifierGAF[dag[r['_Term_key']]]
        elif r['qualifier'] != None:
            qualifier = r['qualifier'].strip()
        elif r['inferredFrom'] != None and r['inferredFrom'].find('InterPro:') >= 0 and dag[r['_Term_key']] == 'P':
            qualifier = 'involved_in'
        else:
            qualifier = dagQualifierGAF[dag[r['_Term_key']]]
        reportRow = reportRow + qualifier + TAB

        #!5  GO ID         
        reportRow = reportRow + r['termID'] + TAB

        #!6  DB:Reference (|DB:Reference) 
        references = []
        # If a GO_REF ID is available, use the GO_REF ID
        if r['_Refs_key'] in goRefDict:
                references.append(goRefDict[r['_Refs_key']])
        # elif a PMID is available, use the PMID
        elif r['_Refs_key'] in pubMedId:
            references.append('PMID:' + pubMedId[r['_Refs_key']])
        # elif a DOI is available, use the DOI ID
        elif r['_Refs_key'] in doiId:
            references.append('DOI:' + doiId[r['_Refs_key']])
        # else, use the MGI_ID
        else:
            references.append(r['markerID'])
        reportRow = reportRow + '|'.join(references) + TAB

        #!7  Evidence Code               
        reportRow = reportRow + r['evidenceCode'] + TAB

        #!8  With (or) From             
        inferredFrom = mgi_utils.prvalue(r['inferredFrom']).replace('MGI:', 'MGI:MGI:')
        reportRow = reportRow + inferredFrom + TAB

        #!9  Aspect                     
        #!10 DB Object Name             
        reportRow = reportRow + dag[r['_Term_key']] + TAB
        reportRow = reportRow + r['name'] + TAB

        #!11 DB Object Synonym (|Synonym)
        if r['_Object_key'] in syns:
            reportRow = reportRow + '|'.join(syns[r['_Object_key']]) + TAB
        else:
            reportRow = reportRow + TAB

        #!12 DB Object Type             
        if r['_Marker_Type_key'] == 1 and r['featureType'] == 'unclassified gene':
                reportRow = reportRow + 'gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'protein coding gene':
                reportRow = reportRow + 'protein_coding_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'non-coding RNA gene':
                reportRow = reportRow + 'ncRNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'heritable phenotypic marker':
                reportRow = reportRow + 'genetic_marker' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'antisense lncRNA gene':      
                reportRow = reportRow + 'antisense_lncRNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'bidirectional promoter lncRNA gene':  
                reportRow = reportRow + 'bidirectional_promoter_lncRNA' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'lincRNA gene':        
                reportRow = reportRow + 'lincRNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'lncRNA gene': 
                reportRow = reportRow + 'lncRNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'miRNA gene':  
                reportRow = reportRow + 'miRNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'non-coding RNA gene': 
                reportRow = reportRow + 'ncRNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'ribozyme gene':       
                reportRow = reportRow + 'ribozyme_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'RNase MRP RNA gene':  
                reportRow = reportRow + 'RNase_MRP_RNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'RNase P RNA gene':    
                reportRow = reportRow + 'RNase_P_RNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'rRNA gene':   
                reportRow = reportRow + 'rRNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'scRNA gene':  
                reportRow = reportRow + 'scRNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'sense intronic lncRNA gene':  
                reportRow = reportRow + 'sense_intronic_ncRNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'sense overlapping lncRNA gene':       
                reportRow = reportRow + 'sense_overlap_ncRNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'snoRNA gene': 
                reportRow = reportRow + 'snoRNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'snRNA gene':  
                reportRow = reportRow + 'snRNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'SRP RNA gene':        
                reportRow = reportRow + 'SRP_RNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'telomerase RNA gene': 
                reportRow = reportRow + 'telomerase_RNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'tRNA gene':   
                reportRow = reportRow + 'tRNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'unclassified non-coding RNA gene':    
                reportRow = reportRow + 'ncRNA_gene' + TAB
        elif r['_Marker_Type_key'] == 1 and r['featureType'] == 'gene segment':
                reportRow = reportRow + 'gene_segment' + TAB
        elif r['_Marker_Type_key'] == 7:
                reportRow = reportRow + 'pseudogene' + TAB
        elif r['_Marker_Type_key'] == 10:
                reportRow = reportRow + 'biological_region' + TAB
        else:
                reportRow = reportRow + 'bad feature type = ' + r['featureType'] + TAB

        #!13 Taxon(|taxon)             
        reportRow = reportRow + 'taxon:10090' + TAB

        #!14 Date                     
        reportRow = reportRow + str(r['gafDate']) + TAB

        #!15 Assigned By             
        assignedBy = r['assignedBy'].replace('GO_', '')
        assignedBy = assignedBy.replace('Central', 'GO_Central')
        reportRow = reportRow + assignedBy + TAB

        #!16 Annotation Extension   
        # column 16
        # contains property/value information
        properties = ''
        if objectKey in gafCol16Lookup:
            properties = ''.join(gafCol16Lookup[objectKey])
        reportRow = reportRow + properties + TAB

        #!17 Gene Product Form ID  
        # if isoformProtein = true
        #    then use isoformsProtein
        isoforms = ''
        if objectKey in isoformsProtein:
            isoforms = '|'.join(isoformsProtein[objectKey])
        reportRow = reportRow + isoforms + CRT

        fp.write(reportRow)

#
# end doGAFFinish()
#

#
# main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)
doSetup1()
doGAFCol16()
doIsoform()
doGAFFinish()
reportlib.finish_nonps(fp)

