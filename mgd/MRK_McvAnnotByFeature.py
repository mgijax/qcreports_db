#!/usr/local/bin/python

'''
#
# MRK_McvAnnotByFeature.py 06/14/10
#
# Report:
#      Counts of curated MCV annotations by Feature Type 
#
# Usage:
#	
#       mcvAnnotByFeature.py
#
# History:
#
# lec	10/27/2011
#	- converted outer join to ANSI standard as part of postgres move
#
# sc	06/14/10
#	- created
#
'''
 
import sys 
import os
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
TAB = reportlib.TAB

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])
fp.write('Curated MCV Annotations by Feature%s%s' %(CRT, CRT))
fp.write('MCV Feature%sFeature Count%s' % (TAB, CRT) )
fp.write('-'*80 + CRT)

db.sql('''
	select t.term as feature, 0 as featureCount
	into #notUsed
	from VOC_Term t
	where t._Vocab_key = 79
	and not exists (select 1
	from VOC_annot va 
	where va._AnnotType_key = 1011
		and va._Term_key = t._Term_key)
	''', None)

db.sql('''
	select va.*, t.term as feature
        into #mcv
        from VOC_Annot va
	LEFT OUTER JOIN VOC_Term t on (va._Term_key = t._Term_key)
        where va._AnnotType_key = 1011
	''', None)

results = db.sql('''
	select feature, count(feature) as featureCount
	from #mcv
	group by feature
	union
	select feature, featureCount
	from #notUsed
	order by feature
	''', 'auto')

for r in results:
    fp.write('%s%s%s%s%s%s' % (r['feature'], TAB, TAB, TAB, r['featureCount'], CRT))
fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)

