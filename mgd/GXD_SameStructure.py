
'''
#
# GXD_SameStructure.py (TR 6677, TR 6724)
#
# Report:
#
# 	Multiple annotations to the same Structure for the same Specimen/Gel Lane
#
#	Output fields:
#		J number of paper
#		MGI id of assay
#		Name of offending specimen/gel lane
#               EMAPA Term
#               Stage
#               Cell Type Term
#
#	Sort by: J number
#
# Usage:
#       GXD_SameStructure.py
#
# Notes:
#	- all reports use mgireport directory for output file
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
#
# sc    12/09/2021
#       - YAKS project; added cell type term column
#
# lec	05/01/2008
#	- TR 8775; on select GXD assay types
#
# lec	04/11/2005
#	 - converted to QC report
#
# sc	03/29/2005
#	- created
#
'''
 
import sys 
import os
import string
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], 'GXD Specimens/Lanes that use the same Structure > 1', outputdir = os.environ['QCOUTPUTDIR'])

fp.write(str.ljust('J:', 15))
fp.write(str.ljust('Assay ID', 15))
fp.write(str.ljust('Label', 35))
fp.write(str.ljust('EMAPA-Term', 50))
fp.write(str.ljust('Stage', 10))
fp.write(str.ljust('CellType-Term', 50))
fp.write(CRT)
fp.write(str.ljust('----------', 15))
fp.write(str.ljust('----------', 15))
fp.write(str.ljust('----------', 35))
fp.write(str.ljust('----------', 50))
fp.write(str.ljust('-----', 10))
fp.write(str.ljust('----------', 50))
fp.write(2*CRT)

# get the all specimen/structure pairs

db.sql('''
    select gr._Specimen_key, grs._EMAPA_Term_key , grs._Stage_key, gr._result_key
    into temporary table specstructs
    from GXD_Assay a, GXD_Specimen s, GXD_InSituResult gr, GXD_ISResultStructure grs
    where a._AssayType_key in (1,2,3,4,5,6,8,9)
    and a._Assay_key = s._Assay_key
    and s._Specimen_key = gr._Specimen_key
    and gr._Result_key = grs._Result_key
    ''', None)

db.sql('create index specs_idx1 on specstructs (_result_key)', None)

# get the cell types
db.sql('''
    select ct._celltype_term_key, s._Specimen_key, s._EMAPA_Term_key , s._Stage_key
    into temporary table specstructs_ct
    from specstructs s
    left outer join GXD_ISResultCelltype ct on (s._result_key = ct._result_key)
    ''', None)

db.sql('create index specs_ct_idx1 on specstructs_ct (_Specimen_key)', None)
db.sql('create index specs_ct_idx2 on specstructs_ct (_EMAPA_Term_key)', None)

# get the duplicates

db.sql('''
    select * into temporary table dupspecimens 
    from specstructs_ct 
    group by _Specimen_key, _EMAPA_Term_key, _Stage_key, _celltype_term_key  having count(*) > 1
    ''', None)

db.sql('create index dupspec_idx1 on dupspecimens (_Specimen_key)', None)
db.sql('create index dupspec_idx2 on dupspecimens (_EMAPA_Term_key)', None)
db.sql('create index dupspec_idx3 on dupspecimens (_celltype_term_key)', None)

# get the specimen label _Refs_key and  _Assay_key, and structure for each dup

db.sql('''
    select distinct ss.*, gs.specimenLabel, ga._Refs_key, gs._Assay_key, s1.term as emapaTerm, t.stage
    into temporary table specimens
    from dupspecimens ss, GXD_Specimen gs, GXD_Assay ga, VOC_Term s1, GXD_TheilerStage t
    where ss._Specimen_key= gs._Specimen_key
    and gs._Assay_key = ga._Assay_key
    and ss._EMAPA_Term_key = s1._Term_key
    and ss._Stage_key = t._Stage_key
    ''', None)

db.sql('''create index specimens_idx1 on specimens(_celltype_term_key)''', None)
   
# get the cell type term
db.sql('''
    select s.*, t.term as celltypeTerm
    into temporary table specimens_ct
    from specimens s
    left outer join VOC_Term t on (s._celltype_term_key = t._term_key) 
     ''', None)

db.sql('''create index specimens_ct_idx1 on specimens(_refs_key)''', None)
    

db.sql('''
    select gr._GelLane_key, grs._EMAPA_Term_key, grs._Stage_key
    into temporary table gelstructs 
    from GXD_Assay a, GXD_GelLane gr, GXD_GelLaneStructure grs 
    where a._AssayType_key in (1,2,3,4,5,6,8,9) 
    and a._Assay_key = gr._Assay_key 
    and gr._GelLane_key = grs._GelLane_key
    ''', None)

db.sql('create index gel_idx1 on gelstructs (_GelLane_key)', None)
db.sql('create index gel_idx2 on gelstructs (_EMAPA_Term_key)', None)

# get the duplicates

db.sql('''
    select * into temporary table dupgels 
    from gelstructs 
    group by _GelLane_key, _EMAPA_Term_key, _Stage_key having count(*) > 1
    ''', None)

db.sql('create index dupgel_idx1 on dupgels (_GelLane_key)', None)
db.sql('create index dupgel_idx2 on dupgels (_EMAPA_Term_key)', None)

# get the gel label _Refs_key and  _Assay_key, and structure for each dup

db.sql('''
    select distinct ss.*, gs.laneLabel, ga._Refs_key, gs._Assay_key, s.term as emapaTerm, '' as celltypeTerm, t.stage
    into temporary table gels
    from dupgels ss, GXD_GelLane gs, GXD_Assay ga, VOC_Term s, GXD_TheilerStage t
    where ss._GelLane_key= gs._GelLane_key
    and gs._Assay_key = ga._Assay_key
    and ss._EMAPA_Term_key = s._Term_key
    and ss._Stage_key = t._Stage_key
    ''', None)

# get the MGI and Jnum ids

db.sql('''
    select distinct ss.specimenLabel, ss.emapaTerm, ss.celltypeTerm, ss.stage,
           a1.accid as mgiID, a2.accid as jnumID, a2.numericPart 
    into temporary table finalSpecimen 
    from specimens_ct ss, ACC_Accession a1, ACC_Accession a2 
    where ss._Assay_key = a1._Object_key 
    and a1._MGIType_key = 8 
    and a1._LogicalDB_key = 1 
    and a1.prefixPart = 'MGI:' 
    and ss._Refs_key = a2._Object_key 
    and a2._MGIType_key = 1 
    and a2._LogicalDB_key = 1 
    and a2.prefixPart = 'J:' 
    order by a2.numericPart, ss.specimenLabel
    ''', None)

db.sql('''
    select distinct ss.laneLabel, ss.emapaTerm, ss.celltypeTerm, ss.stage,
           a1.accid as mgiID, a2.accid as jnumID, a2.numericPart 
    into temporary table finalGel 
    from gels ss, ACC_Accession a1, ACC_Accession a2 
    where ss._Assay_key = a1._Object_key 
    and a1._MGIType_key = 8 
    and a1._LogicalDB_key = 1 
    and a1.prefixPart = 'MGI:' 
    and ss._Refs_key = a2._Object_key 
    and a2._MGIType_key = 1 
    and a2._LogicalDB_key = 1 
    and a2.prefixPart = 'J:' 
    order by a2.numericPart, ss.laneLabel
    ''', None)

finalDict = {}
results = db.sql('''
        select specimenLabel, emapaTerm, celltypeTerm, stage, mgiID, jnumID, numericPart 
        from finalSpecimen''', 'auto')
for r in results:
    key = r['numericPart']
    if key not in finalDict:
        finalDict[key] = []
    finalDict[key].append(r)

results = db.sql('''select laneLabel, emapaTerm, celltypeTerm, stage, mgiID, jnumID, numericPart 
        from finalGel''', 'auto')
rowCount = len(results)
for r in results:
    key = r['numericPart']
    if key not in finalDict:
        finalDict[key] = []
    finalDict[key].append(r)

sortOrder = sorted(finalDict.keys())
for k in sortOrder:
    rList = finalDict[k]
    for r in rList:
        celltypeTerm = r['celltypeTerm']
        if celltypeTerm == None:
            celltypeTerm = ''
        fp.write(str.ljust(r['jnumID'], 15))
        fp.write(str.ljust(r['mgiID'], 15))
        fp.write(str.ljust(r['specimenLabel'], 35))
        fp.write(str.ljust(r['emapaTerm'], 50))
        fp.write(str.ljust(str(r['stage']), 10))
        fp.write(str.ljust(celltypeTerm, 50))
        fp.write(CRT)

fp.write('\n(%d rows affected)\n' % (rowCount))

reportlib.finish_nonps(fp)	# non-postscript file
