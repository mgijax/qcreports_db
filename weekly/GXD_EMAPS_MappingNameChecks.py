#!/usr/local/bin/python

'''
#
# GXD_EMAPS_MappingNameChecks.py  /01/10/2014
#
# Report:
#       
#	AD Term names and EMAPS Term Names that do not match
#
# Fields:
#	1. AD MGI ID
#	2. AD Theiler Stage
#	3. AD Print Name
#	4. EMAPS ID
#	5. EMAPS Theiler Stage
#	6. EMAPS term name
# 
# Usage:
#       GXD_EMAPS_MappingNameChecks.py
#
# History:
#
# oblod	01/10/2014
#	- TR11468 GXD Anatomy Project 
#
'''
 
import sys 
import os
import string
import reportlib

try:
    if os.environ['DB_TYPE'] == 'postgres':
        import pg_db
        db = pg_db
        db.setTrace()
        db.setAutoTranslateBE()
    else:
        import db
except:
    import db


CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

title = 'AD Term names and EMAPS Term names that do not match'
fp = reportlib.init(sys.argv[0], title = title, outputdir = os.environ['QCOUTPUTDIR'])

fp.write('AD MGI ID%sAD Theiler Stage%sAD term name%sEMAPS ID%sEMAPS Theiler Stage%sEMAPS term name%s' % (TAB, TAB, TAB, TAB, TAB, CRT))

results = db.sql('''select mem.accID, 
	    gts.stage as adStage, 
	    substring(gs.printName, 1,80) as adName, 
	    mem.emapsID,
	    vte.stage as emapsStage,
	    substring(voct.term, 1,80) as emapsName
	from GXD_Structure gs, GXD_TheilerStage gts, GXD_StructureName gsn, 
	    ACC_Accession aa1, ACC_MGIType ty1, MGI_EMAPS_Mapping mem, 
	    ACC_Accession aa2, ACC_MGIType ty2, VOC_Term voct, 
	    VOC_Term_EMAPS vte 
	where gs._Structure_key = aa1._Object_key 
	and gs._StructureName_key = gsn._StructureName_key 
	and gs._Stage_key = gts._Stage_key 
	and aa1.accId = mem.accID 
	and aa1._MGIType_key = ty1._MGIType_key 
	and ty1.tableName = 'GXD_Structure' 
	and mem.emapsID = aa2.accId 
	and aa2._MGIType_key = ty2._MGIType_key 
	and ty2.tableName = 'VOC_Term' 
	and aa2._Object_key = voct._Term_key 
	and voct._Term_key = vte._Term_key 
	and (case when voct.term = gsn.structure then 1 else 0 end) = 0
       ''', 'auto')

for r in results:
    fp.write('%s%s%s%s%s%s%s%s%s%s%s%s' % (r['accID'], TAB, r['adStage'], TAB, r['adName'], TAB, r['emapsID'], TAB, r['emapsStage'], TAB, r['emapsName'], CRT))

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)	# non-postscript file
