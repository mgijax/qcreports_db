#!/usr/local/bin/python

'''
#
# GXD_EMAPS_MappingAdUnmappedChecks.sql  /01/10/2014
#
# Report:
#       
#	AD Term names and EMAPS Term Names that do not match
#
# Fields:
#	1. AD MGI ID
#	2. AD Theiler Stage
#	3. Annotation Count
#	4. Print Name
# 
# Usage:
#       GXD_EMAPS_MappingAdUnmappedChecks.py
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

title = 'AD Terms test do not map to EMAPS Id''s'
fp = reportlib.init(sys.argv[0], title = title, outputdir = os.environ['QCOUTPUTDIR'])

fp.write('AD MGI ID%sAD Theiler Stage%sAnnotation Count%sPrint Name%s' % (TAB, TAB, TAB, CRT))

results = db.sql('''

select
	acc.accId,
	gts.stage,
	(case when vacc.annotCount = NULL then 0 else vacc.annotCount end) as "acount",
	gs.printname
from
	ACC_Accession acc,
	GXD_TheilerStage gts,
	GXD_StructureName gsn,
	GXD_Structure gs
LEFT OUTER JOIN
	VOC_Annot_Count_Cache vacc on (gs._Structure_key = vacc._Term_key and vacc.annotType = 'AD')
where
	acc._MGIType_key = 38 and
	acc.prefixPart = "MGI:" and
	gs._Structure_key = acc._Object_key and
	gs._Structure_key in (
		select
			gs._Structure_key
		from
			GXD_Structure gs,
			ACC_Accession acc
		LEFT OUTER JOIN
			MGI_EMAPS_Mapping mem on (acc.accId = mem.accId)
		where
			gs._Structure_key = acc._Object_key and
			gs._Stage_key = gts._Stage_key and
			gs._StructureName_key = gsn._StructureName_key and
			acc._MGIType_key = 38 and
			acc.prefixPart = "MGI:" and
			mem.accId is NULL
	)
order by 
	vacc.annotCount desc
       ''', 'auto')

for r in results:
    fp.write('%s%s%s%s%s%s%s%s%s%s%s%s' % (r['accId'], TAB, r['stage'], TAB, r['acount'], TAB, r['printname'], TAB, CRT))

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)	# non-postscript file
