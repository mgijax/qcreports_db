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

title = 'Check 9 - AD Terms that do not map to EMAPS Ids'
fp = reportlib.init(sys.argv[0], title = title, outputdir = os.environ['QCOUTPUTDIR'])

fp.write('AD MGI ID%sAD Theiler Stage%sAnnotation Count%sPrint Name%s' % (TAB, TAB, TAB, CRT))

results = db.sql('''

	select
		gs._Structure_key,
		count(gs._Structure_key) as "SCount"
	into #tmp_olin
	from
		GXD_Structure gs,
		ACC_Accession acc
	LEFT OUTER JOIN
		MGI_EMAPS_Mapping mem on (acc.accId = mem.accId)
	LEFT OUTER JOIN
		GXD_Expression ge on (acc._Object_key = ge._Structure_key)
	where
		gs._Structure_key = acc._Object_key and
		acc._MGIType_key = 38 and
		acc.prefixPart = "MGI:" and
		mem.accId is NULL and
		ge._Structure_key is not NULL
	group by
		gs._Structure_key
union
	select
		gs._Structure_key,
		0 as "SCount"
	from
		GXD_Structure gs,
		ACC_Accession acc
	LEFT OUTER JOIN
		MGI_EMAPS_Mapping mem on (acc.accId = mem.accId)
	LEFT OUTER JOIN
		GXD_Expression ge on (acc._Object_key = ge._Structure_key = 1)
	where
		gs._Structure_key = acc._Object_key and
		acc._MGIType_key = 38 and
		acc.prefixPart = "MGI:" and
		mem.accId is NULL and
		ge._Structure_key is NULL
	group by
		gs._Structure_key
       ''', 'auto')

results = db.sql('''
select
	acc.accId,
	gts.stage,
	olin.Scount,
	gs.printname
from
	#tmp_olin olin,
	GXD_Structure gs,
	ACC_Accession acc,
	GXD_TheilerStage gts
where
	olin._Structure_key = gs._Structure_key and
	gs._Structure_key = acc._Object_key and
	gs._Stage_key = gts._Stage_key and
	acc._MGIType_key = 38 and
	acc.prefixPart = "MGI:"
order by
	olin.SCount desc, gs.printname
       ''', 'auto')

for r in results:
    fp.write('%s%s%s%s%s%s%s%s' % (r['accId'], TAB, r['stage'], TAB, r['Scount'], TAB, r['printname'], CRT))

fp.write('\n(%d rows affected)\n' % (len(results)))

results = db.sql(''' drop table #tmp_olin ''', 'auto')

reportlib.finish_nonps(fp)	# non-postscript file
