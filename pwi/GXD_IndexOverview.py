
'''
#
# TR11107
#
# Report:
#
# exclude RNase protection, Nuclease S1, Primer Extension, cDNA clones
#       (74725, 74726, 74727, 74728)
#
#       1. Gene
#       2. MGI ID
#       3. J
#       4. Author
#       5. Journal
#       6. Year of publication
#       7. Number of index records in J
#       8. Priority score
#       9. Tags
#       10. Number of Alleles
#       11. Conditional menu choice
#       12. Recombinase
#       13. Full Coded? (Y/N)
#       14. Total # of age/assay combo (purple/blue dots on gxd_index module)
#       15. Total # of ages analyzed
#       16-57: 0.5, 1, 1.5...20, E, A (42)
#       58. Total # of Assay Types analyzed 
#       59-66.  Assay Types
#       67. Title
#
# Usage:
#       GXD_IndexOverview.py MGI:xxxxx
#
# History:
#
# lec   08/06/2012
#
# jer   10/02/2015 Removed references to title2 and authors2, which no longer exist.
#
'''

import sys
import os
import mgi_utils
import reportlib
import db

#db.setTrace(False)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# input file format:
#
# MGI:xxxx
# MGI:xxxx
# ...
#

runUber = 0
try:
    if sys.argv[1] == 'uber':
        runUber = 1
except:
    pass

print(runUber)
accidquery = ''
if not runUber:
    accids = []
    inFileName = os.environ['HOME'] + '/mgireport/GXD_IndexOverview.txt'
    inFile = open(inFileName, 'r')
    for r in inFile.readlines():
        value = r[:-1].replace('\t\t\r', '')
        value = value.replace('\r', '')
        accids.append(value)
    inFile.close()
    accidquery = "('" + "','".join(accids) + "')"

#
# assay terms
#
assay = []
results = db.sql('''
        select term from VOC_Term 
        where _Vocab_key = 12 
        and _Term_key not in (74725, 74726, 74727, 74728)
        order by _Term_key
        ''', 'auto')
for r in results:
    assay.append(r['term'])

#
# stage terms
#
stage = []
results = db.sql('''
        select term from VOC_Term where _Vocab_key = 13 order by _Term_key
        ''', 'auto')
for r in results:
    stage.append(r['term'])

sys.stdout.write('Gene' + TAB)
sys.stdout.write('MGI ID' + TAB)
sys.stdout.write('J#' + TAB)
sys.stdout.write('Author' + TAB)
sys.stdout.write('Journal' + TAB)
sys.stdout.write('Year of publication' + TAB)
sys.stdout.write('# index records in J#' + TAB)
sys.stdout.write('Priority score' + TAB)
sys.stdout.write('Tags' + TAB)
sys.stdout.write('# allele records in J#' + TAB)
sys.stdout.write('Conditional menu choice' + TAB)
sys.stdout.write('Recombinase' + TAB)
sys.stdout.write('Full Coded? (Y/N)' + TAB)
sys.stdout.write('# index results (red dots) in record' + TAB)
sys.stdout.write('# ages analyzed' + TAB)

for r in stage:
    sys.stdout.write(r + TAB)

sys.stdout.write('# Assay Types analyzed ' + TAB)

for r in assay:
    sys.stdout.write(r + TAB)

sys.stdout.write('Title' + CRT)

#
# select GXD indexes
#

sql = '''
        select g._Index_key, g._Marker_key, g._Refs_key, m.symbol, a.accID,
               aa.accID as jnumID, r.authors, r.journal, r.year, r.title,
               t1.term as priorityscore,
               t2.term as conditionalmutations
        into temporary table gxdindex
        from GXD_Index g, 
             MRK_Marker m, 
             ACC_Accession a, 
             ACC_Accession aa, 
             BIB_Refs r,
             VOC_Term t1,
             VOC_Term t2
        where g._Marker_key = m._Marker_key
        and g._Marker_key = a._Object_key
        and a._MGIType_key = 2
        and a._LogicalDB_key = 1
        and a.preferred = 1
        and g._Refs_key = aa._Object_key
        and aa._MGIType_key = 1
        and aa._LogicalDB_key = 1
        and aa.prefixPart = 'J:'
        and aa.preferred = 1
        and g._Refs_key = r._Refs_key
        and g._Priority_key = t1._Term_key
        and g._ConditionalMutants_key = t2._Term_key
        '''

if len(accidquery) > 0:
    sql = sql + '\nand a.accID in %s' % (accidquery)

db.sql(sql, None)
db.sql('create index gxdindex_idx1 on gxdindex(_Marker_key)', None)

#
# index count by J#
#

indexByJnum = {}
results = db.sql('''
        select _Refs_key, count(*) as jnum_count
        from GXD_Index
        group by _Refs_key
        ''', 'auto')
for r in results:
    key = r['_Refs_key']
    value = r['jnum_count']
    if key not in indexByJnum:
        indexByJnum[key] = []
    indexByJnum[key].append(value)

#
# full-coded count
#

fullcodedByJnum = []
results = db.sql('''
        select distinct a._Refs_key 
        from gxdindex g, GXD_Assay a
        where g._Refs_key = a._Refs_key
        and a._AssayType_key not in (10,11)
        ''', 'auto')
for r in results:
    fullcodedByJnum.append(r['_Refs_key'])
    #key = r['_Marker_key']
    #value = r['_Refs_key']
    #if key not in fullcodedByJnum:
    #    fullcodedByJnum[key] = []
    #fullcodedByJnum[key].append(value)

#
# index-assay-stage
#

indexAssayStage = {}
results = db.sql('''
        select distinct s._Index_key, s._IndexAssay_key, s._StageID_key
        from gxdindex g, GXD_Index_Stages s
        where g._Index_key = s._Index_key
        ''', 'auto')
for r in results:
    key = r['_Index_key']
    value = r
    if key not in indexAssayStage:
        indexAssayStage[key] = []
    indexAssayStage[key].append(value)

#
# unique index-stage
#

uniqIndexStage = {}
results = db.sql('''
        select distinct s._Index_key, s._StageID_key
        from gxdindex g, GXD_Index_Stages s
        where g._Index_key = s._Index_key
        and s._IndexAssay_key not in (74725, 74726, 74727, 74728)
        ''', 'auto')
for r in results:
    key = r['_Index_key']
    value = r['_StageID_key']
    if key not in uniqIndexStage:
        uniqIndexStage[key] = []
    uniqIndexStage[key].append(value)

#
# index-stage
#

indexStage = {}
results = db.sql('''
        select s._Index_key, s._StageID_key, t.term, count(s._StageID_key) as index_count
        from gxdindex g, GXD_Index_Stages s, VOC_Term t
        where g._Index_key = s._Index_key
        and s._StageID_key = t._Term_key
        and s._IndexAssay_key not in (74725, 74726, 74727, 74728)
        group by s._Index_key, s._StageID_key, t.term
        ''', 'auto')
for r in results:
    key = r['_Index_key']
    value = r
    if key not in indexStage:
        indexStage[key] = []
    indexStage[key].append(value)

#
# unique index-assay
#

uniqIndexAssay = {}
results = db.sql('''
        select distinct s._Index_key, s._IndexAssay_key
        from gxdindex g, GXD_Index_Stages s
        where g._Index_key = s._Index_key
        and s._IndexAssay_key not in (74725, 74726, 74727, 74728)
        ''', 'auto')
for r in results:
    key = r['_Index_key']
    value = r['_IndexAssay_key']
    if key not in uniqIndexAssay:
        uniqIndexAssay[key] = []
    uniqIndexAssay[key].append(value)

#
# recombinase count by distinct J#/Allele where:
# allele status != 'Deleted'
# allele type = 'transgenic' or 'targeted'
# allele attribute = Recombinase
# not exists allele attribute 'inducible'
# allele ref exists in gxd_index
#
recombinaseByJnum = {}
results = db.sql('''
        WITH alleles AS (
        select distinct r._Refs_key, a._Allele_key
        from MGI_Reference_Allele_View r, ALL_Allele a, VOC_Annot v
        where r._Object_key = a._Allele_key
        and a._Allele_Status_key not in (847112)
        and a._Allele_Type_key in (847126, 847116)
        and a._Allele_key = v._Object_key
        and v._Term_key = 11025588
        and v._AnnotType_key = 1014
        and not exists (select 1 from ALL_Allele a, VOC_Annot v
                        where r._Object_key = a._Allele_key
                        and a._Allele_Status_key not in (847112)
                        and a._Allele_Type_key in (847126, 847116)
                        and a._Allele_key = v._Object_key
                        and v._Term_key = 11025592
                        and v._AnnotType_key = 1014
                        )
        )
        select a._Refs_key, count(*) as jnum_count
                from alleles a
                where exists (select 1 from gxd_index g
                        where a._Refs_key = g._Refs_key
        )
        group by a._Refs_key
        ''', 'auto')
for r in results:
    key = r['_Refs_key']
    value = r['jnum_count']
    if key not in recombinaseByJnum:
        recombinaseByJnum[key] = []
    recombinaseByJnum[key].append(value)

#
# index-assay
#

indexAssay = {}
results = db.sql('''
        select s._Index_key, s._IndexAssay_key, t.term, count(s._IndexAssay_key) as index_count
        from gxdindex g, GXD_Index_Stages s, VOC_Term t
        where g._Index_key = s._Index_key
        and s._IndexAssay_key not in (74725, 74726, 74727, 74728)
        and s._IndexAssay_key = t._Term_key
        group by s._Index_key, s._IndexAssay_key, t.term
        ''', 'auto')
for r in results:
    key = r['_Index_key']
    value = r
    if key not in indexAssay:
        indexAssay[key] = []
    indexAssay[key].append(value)

#
# allele  by J#
#

alleleByJnum = {}
results = db.sql('''
        select distinct _Refs_key, count(distinct _object_key) as allele_count
        from MGI_Reference_Assoc
        where _MGIType_key = 11
        group by _Refs_key
        ''', 'auto')
for r in results:
    key = r['_Refs_key']
    value = r['allele_count']
    if key not in alleleByJnum:
        alleleByJnum[key] = []
    alleleByJnum[key].append(value)

# 
# tags
#
tags = {}
results = db.sql('''
        select distinct t._Refs_key, tt.term
        from gxdindex g, BIB_Workflow_Tag t, VOC_Term tt
        where g._Refs_key = t._Refs_key
        and t._tag_key = tt._term_key
        and tt.term like 'GXD:%'
        and tt.abbreviation like 'To be used for full-coding priorities%'
        ''', 'auto')
for r in results:
    key = r['_Refs_key']
    value = r['term'].replace('GXD:','')
    if key not in tags:
        tags[key] = []
    tags[key].append(value)
#print(tags[229890])

#
# to print...
#
results = db.sql('select * from gxdindex order by symbol', 'auto')

for r in results:

    mKey = r['_Marker_key']
    rKey = r['_Refs_key']
    iKey = r['_Index_key']

#       1. Gene
    sys.stdout.write(r['symbol'] + TAB)

#       2. MGI ID
    sys.stdout.write(r['accID'] + TAB)

#       3. J
    sys.stdout.write(r['jnumID'] + TAB)

#       4. Author

    authors = r['authors'].split(';')
    lastauthor = authors[-1]
    sys.stdout.write(lastauthor + TAB)

#       5. Journal
    sys.stdout.write(mgi_utils.prvalue(r['journal']) + TAB)

#       6. Year of publication
    sys.stdout.write(mgi_utils.prvalue(str(r['year'])) + TAB)

#       7. Number of index records by J:
    if rKey in indexByJnum:
        sys.stdout.write(str(indexByJnum[rKey][0]))
    sys.stdout.write(TAB)

#       8. Priority score
    sys.stdout.write(r['priorityscore'] + TAB)

#       9. Tags
    if rKey in tags:
        sys.stdout.write('|'.join(tags[rKey]) + TAB)
    else:
        sys.stdout.write(TAB)

#       10. Number of Alleles
    if rKey in alleleByJnum:
        sys.stdout.write(str(alleleByJnum[rKey][0]) + TAB)
    else:
        sys.stdout.write(TAB)

#       11. Conditional menu choice
    sys.stdout.write(r['conditionalmutations'] + TAB)

#       12. Recombinase
    if rKey in recombinaseByJnum:
        sys.stdout.write(str(recombinaseByJnum[rKey][0]) + TAB)
    else:
        sys.stdout.write(TAB)

#       13. Full Coded? (Y/N)
    fullcode = 'N'
    if rKey in fullcodedByJnum:
        fullcode = 'Y'
    sys.stdout.write(fullcode + TAB)

#       14. Total # of age/assay combo (purple/blue dots on gxd_index module)
    if iKey in indexAssayStage:
        sys.stdout.write(str(len(indexAssayStage[iKey])) + TAB)
    else:
        sys.stdout.write(TAB)

#       15. Total # of ages analyzed
    if iKey in uniqIndexStage:
        sys.stdout.write(str(len(uniqIndexStage[iKey])) + TAB)
    else:
        sys.stdout.write(TAB)

#       16-57: 0.5, 1, 1.5...20, E, A (42)
    slist = {}
    if iKey in indexStage:
        for s in indexStage[iKey]:
            thisStage = s['term']
            thisCount = s['index_count']
            slist[thisStage] = []
            slist[thisStage].append(thisCount)

    for ss in stage:
        if ss in slist:
            sys.stdout.write(str(slist[ss][0]) + TAB)
        else:
            sys.stdout.write(TAB)

#       58. Total # of Assay Types analyzed 
    if iKey in uniqIndexAssay:
        sys.stdout.write(str(len(uniqIndexAssay[iKey])) + TAB)
    else:
        sys.stdout.write(TAB)

#       59-66.  Assay Types
    slist = {}
    if iKey in indexAssay:
        for s in indexAssay[iKey]:
            thisAssay = s['term']
            thisCount = s['index_count']
            slist[thisAssay] = []
            slist[thisAssay].append(thisCount)

    for ss in assay:
        if ss in slist:
            sys.stdout.write(str(slist[ss][0]) + TAB)
        else:
            sys.stdout.write(TAB)

#       67. Title
    sys.stdout.write(mgi_utils.prvalue(r['title']) + CRT)
        
sys.stdout.flush()

