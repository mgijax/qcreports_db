'''
#
# GXD HT Sample Annotations
#
# Report lists all curated samples and their values
#
# Report name: GXD HT Sample
#
# Sort:
#       Primary: Sample Name
#       Secondary: Species (Common Name)
#       Tertiary: Relevance
#
'''
 
import sys 
import os
import db
import reportlib

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

def go (form) :
    #
    # Main
    #

    sampleAllelePairDict = {}
    exptVarDict = {}

    db.sql('''
        select gh._Sample_key,
        tt.stage,
        t4.term as emapaTerm,
        gh._Genotype_key,
        e._Experiment_key,
        gh.name,
        gh.age,
        mo.commonName,
        t2.term as relevance,
        t3.term as sex,
        mn.note as sampleNote,
        a.accid as AEID,
        t1.term as studyType,
        t5.term as celltype,
        t6.term as rnaSeqType
        into temporary table samples
        from GXD_HTSample gh
        join MGI_Organism mo on (gh._Organism_key = mo._Organism_key)
        join GXD_HTExperiment e on (gh._Experiment_key = e._Experiment_key)
        join VOC_Term t1 on (e._StudyType_key = t1._Term_key)
        join VOC_Term t2 on (gh._Relevance_key = t2._term_key)
        join VOC_Term t3 on (gh._Sex_key = t3._term_key)
        join VOC_Term t6 on (gh._RNASeqType_key = t4._term_key)
        join ACC_Accession a on ( gh._Experiment_key = a._Object_key
            and a._MGIType_key = 42
            and a._LogicalDB_key in (189, 190)
            and a.preferred = 1)
        left outer join MGI_Note mn on ( gh._Sample_key = mn._Object_key and mn._Notetype_key = 1048 )
        left outer join GXD_TheilerStage tt on (gh._Stage_key = tt._Stage_key)
        left outer join VOC_Term t4 on (gh._Emapa_key = t4._Term_key)
        left outer join VOC_Term t5 on (gh._CellType_Term_key = t5._Term_key)
        order by a.accid, gh.name
    ''', None)

    db.sql('''create index idx1 on samples(_Experiment_key)''', None)
    db.sql('''create index idx4 on samples(_Genotype_key)''', None)

    results = db.sql('''
    select s._Sample_key, s._Experiment_key, ap.* 
    from samples s, GXD_AllelePair ap
    where s._genotype_key = ap._genotype_key
    order by s._experiment_key, s._sample_key
    ''', 'auto')

    for r in results:

        sampleKey = r['_Sample_key']

        if sampleKey not in sampleAllelePairDict:
            sampleAllelePairDict[sampleKey] = []

        allele1 = r['_Allele_key_1']
        allele2 =  r['_Allele_key_2']

        if allele2 == None:
            allele2 = ''

        alleleKeyPair = '%s/%s' % (allele1, allele2)
        sampleAllelePairDict[sampleKey].append(alleleKeyPair)

    results = db.sql('''
    select s._sample_key, s._Experiment_key, t.term
    from samples s, GXD_HTExperimentVariable ev, VOC_Term t
    where s._Experiment_key = ev._Experiment_key
    and ev._Term_key = t._term_key
    ''', 'auto')

    for r in results:
        experimentKey = r['_Experiment_key']
        term = r['term']
        if experimentKey not in exptVarDict:
            exptVarDict[experimentKey] = []
        if term not in exptVarDict[experimentKey]:
            exptVarDict[experimentKey].append(r['term'])

    results = db.sql('''select * from samples''', 'auto')

    # Write header
    sys.stdout.write('Sample Name'+ TAB)
    sys.stdout.write('Common Name' + TAB)
    sys.stdout.write('Relevance'+ TAB)
    sys.stdout.write('HasAllelePair?' + TAB)
    sys.stdout.write('Age' + TAB)
    sys.stdout.write('Sex' + TAB)
    sys.stdout.write('TS' + TAB)
    sys.stdout.write('Structure' + TAB)
    sys.stdout.write('Cell Type' + TAB)
    sys.stdout.write('RNA-Seq Type'+ TAB)
    sys.stdout.write('Exp ID' + TAB)
    sys.stdout.write('Study Type' + TAB)
    sys.stdout.write('ExptVars' + TAB)
    sys.stdout.write('Sample Note' + CRT)

    for r in results:

        sampleKey = r['_Sample_key']
        exptKey = r['_Experiment_key']

        note = r['sampleNote']
        if note == None:
            note = ''
        else:
            note = note.replace('/n', '') # rm extraneous newlines

        # sampleAllelePairDict (_Sample_key)
        hasAllelePairs = 'No'
        if sampleKey in sampleAllelePairDict:
            hasAllelePairs = 'Yes'

        # exptVarDict (exptKey)
        exptVarList = []
        if exptKey in exptVarDict:
            exptVarList = exptVarDict[exptKey]

        cellType = r['celltype']
        if cellType == None:
            cellType = ''

        emapaTerm = r['emapaTerm']
        if emapaTerm == None:
            emapaTerm = ''

        sys.stdout.write(r['name'] + TAB)
        sys.stdout.write(r['commonName'] + TAB)
        sys.stdout.write(r['relevance'] + TAB)
        sys.stdout.write(hasAllelePairs + TAB)
        sys.stdout.write(r['age'] + TAB)
        sys.stdout.write(r['sex'] + TAB)
        sys.stdout.write(str(r['stage']) + TAB)
        sys.stdout.write(emapaTerm + TAB)
        sys.stdout.write(cellType + TAB)
        sys.stdout.write(r['rnaSeqType'] + TAB)
        sys.stdout.write(r['AEID'] + TAB)
        sys.stdout.write(r['studyType'] + TAB)
        sys.stdout.write(str.join('|', exptVarList) + TAB)
        sys.stdout.write(note + CRT)

    sys.stdout.flush()
