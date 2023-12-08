
'''
#
# TR12901
#
# Report:
#	
# 	1) List all strains flagged as .Non-standard. and 
#	A. have no strain attributes 
#	B. created by anyone except .csmith., .mberry. and .strainautoload.
#
#	2) List all strains flagged as .Non-standard. and 
#	A. have no strain attributes 
#	B. created by .csmith., .mberry. and .strainautoload.      
#
#	Columns:
#	1) creation date 
#	2) MGI ID
#	3) any external ID (ie jax, mmrrc, etc), pipe delimited if more than one
#	4) strain name
#	5) created by       
#
#	Sort: creation date, most recent first. 
#
# Usage:
#       PRB_Strain_NonStdNoAttributes.py
#
# Notes:
#
# History:
#
#	TR12850 sc - created
#
'''
 
import sys 
import os 
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#
accidDict1 = {}
accidDict2 = {}
fp = reportlib.init(sys.argv[0], 'Strains flagged as "Non-standard" and have no strain attributes', os.environ['QCOUTPUTDIR'])
fp.write('\nReport 1: Created by anyone except csmith, mberry and strainautoload\n\n')

fp.write('Creation Date%sMGI ID%sExternal ID(s)%sStrain name%sPrivate(Y/N)%sCreated By%s' % (TAB, TAB, TAB, TAB, TAB, CRT))

db.sql('''select distinct s._Strain_key, s.private, s.creation_date as rawDate, to_char(s.creation_date, 'MM/dd/yyyy') as creation_date, s.strain, u.name, a.accid as strainID
    into temporary table strains1
    from PRB_Strain s, MGI_User u, ACC_Accession a
    where s.standard = 0
    and s._CreatedBy_key = u._User_key
    and s._CreatedBy_key not in (1065, 1421, 1521) --csmith, mberry, strainautoload
    and s._Strain_key = a._Object_key
    and a._MGIType_key = 10
    and a._LogicalDB_key = 1
    and a.preferred = 1
    and a.prefixPart = 'MGI:'
    and not exists (select 1 
    from PRB_Strain_Attribute_View sav
    where s._Strain_key = sav._Strain_key) ''', None)

results = db.sql('''select a._Object_key as _Strain_key, a.accid, ldb.name
    from ACC_Accession a, strains1 s, ACC_LogicalDB ldb
    where a._Object_key = s._Strain_key
    and a._MGIType_key = 10
    and a.preferred = 1
    and a._LogicalDB_key != 1
    and a._LogicalDB_key = ldb._LogicalDB_key''', 'auto')
for r in results:
    strainKey = r['_Strain_key']
    if strainKey not in accidDict1:
        accidDict1[strainKey] = []
    accidDict1[strainKey].append(r)

results = db.sql('''select * from strains1
        order by rawDate desc''', 'auto')
for r in results:
    strainKey = r['_Strain_key']
    private = 'N' # default
    if r['private'] == 1:
        private = 'Y'
    creation_date = r['creation_date']
    strain = r['strain']
    created_by = r['name']
    strainID = r['strainID']
    otherIDs = []
    if strainKey in accidDict1:
        for res in accidDict1[strainKey]:
            otherIDs.append(res['accid'])
    fp.write('%s%s%s%s%s%s%s%s%s%s%s%s' % (creation_date, TAB, strainID, TAB, ', '.join(otherIDs), TAB, strain, TAB, private, TAB, created_by, CRT)) 

fp.write('%sTotal: %s' % (CRT, len(results)))

fp.write('\n\nReport 2: Created by csmith, mberry and strainautoload\n\n')

fp.write('Creation Date%sMGI ID%sExternal ID(s)%sStrain name%s Private(Y/N)%sCreated By%s' % (TAB, TAB, TAB, TAB, TAB, CRT))

db.sql('''select distinct s._Strain_key, s.private, s.creation_date as rawDate, to_char(s.creation_date, 'MM/dd/yyyy') as creation_date, s.strain, u.name, a.accid as strainID
    into temporary table strains2
    from PRB_Strain s, MGI_User u, ACC_Accession a
    where s.standard = 0
    and s._CreatedBy_key = u._User_key
    and s._CreatedBy_key in (1065, 1421, 1521) --csmith, mberry, strainautoload
    and s._Strain_key = a._Object_key
    and a._MGIType_key = 10
    and a._LogicalDB_key = 1
    and a.preferred = 1
    and a.prefixPart = 'MGI:'
    and not exists (select 1
    from PRB_Strain_Attribute_View sav
    where s._Strain_key = sav._Strain_key) ''', None)

results = db.sql('''select a._Object_key as _Strain_key, a.accid, ldb.name
    from ACC_Accession a, strains2 s, ACC_LogicalDB ldb
    where a._Object_key = s._Strain_key
    and a._MGIType_key = 10
    and a.preferred = 1
    and a._LogicalDB_key != 1
    and a._LogicalDB_key = ldb._LogicalDB_key''', 'auto')
for r in results:
    strainKey = r['_Strain_key']
    if strainKey not in accidDict1:
        accidDict1[strainKey] = []
    accidDict1[strainKey].append(r)

results = db.sql('''select * from strains2
        order by rawDate desc''', 'auto')
for r in results:
    strainKey = r['_Strain_key']
    private = 'N' # default
    if r['private'] == 1:
        private = 'Y'
    creation_date = r['creation_date']
    strain = r['strain']
    created_by = r['name']
    strainID = r['strainID']
    otherIDs = []
    if strainKey in accidDict1:
        for res in accidDict1[strainKey]:
            otherIDs.append(res['accid'])
    fp.write('%s%s%s%s%s%s%s%s%s%s%s%s' % (creation_date, TAB, strainID, TAB, ', '.join(otherIDs), TAB, strain, TAB, private, TAB, created_by, CRT))

fp.write('%sTotal: %s' % (CRT, len(results)))

reportlib.finish_nonps(fp)
