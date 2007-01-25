#!/usr/local/bin/python

'''
#
# SEQ_NMs.py
#
# Report:
#	TR 8125
#
#       Tab-delimited file
#
# Usage:
#       SEQ_NMs.py
#
# Used by:
#       Deb Reed and Ken Frazer
#
# Notes:
#
# History:
#
# 01/24/2007	lec
#	- new
#
'''
 
import sys
import os
import string
import db
import mgi_utils
import reportlib

TAB = reportlib.TAB
CRT = reportlib.CRT

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

#
# RefSeq sequences that are not associated with any marker
#

db.sql('select s._Sequence_key ' + \
	'into #sequence ' + \
	'from SEQ_Sequence s ' + \
	'where s._SequenceProvider_key = 316372 ' + \
	'and s._SequenceStatus_key = 316342 ' + \
	'and not exists (select 1 from SEQ_Marker_Cache m where s._Sequence_key = m._Sequence_key)', None)
db.sql('create index idx1 on #sequence(_Sequence_key)', None)

#
# ...NMs
#

db.sql('select s._Sequence_key, a.accID ' + \
	'into #acc ' + \
	'from #sequence s, ACC_Accession a ' + \
	'where s._Sequence_key = a._Object_key ' + \
	'and a._MGIType_key = 19 ' + \
	'and a.prefixPart = "NM_"', None)
db.sql('create index idx1 on #acc(accID)', None)

#
# cache NMs in EntrezGene
#

db.sql('select eg.rna, eg.geneID ' + \
	'into #eg ' + \
	'from %s..DP_EntrezGene_Accession eg ' % (os.environ['RADAR_DBNAME']) + \
	'where eg.taxID = 10090 ' + \
	'and eg.rna like "NM_%" ', None)
db.sql('create index idx1 on #eg(rna)', None)

fp.write(CRT + "NM's falling into EG Buckets" + 2*CRT)
fp.write(string.ljust('_NM Acc ID', 35))
fp.write(string.ljust('EG ID of _NM', 35) + CRT)

results = db.sql('select distinct a.accID, eg.geneID ' + \
	'from #acc a, #eg eg ' + \
	'where a.accID = eg.rna ' + \
	'order by a.accID ', 'auto')
for r in results:
    fp.write(string.ljust(r['accID'], 35))
    fp.write(string.ljust(r['geneID'], 35) + CRT)
fp.write('\n(%d rows affected)\n' % (len(results)))

fp.write(CRT + "NM's not in EG Buckets" + 2*CRT)
fp.write(string.ljust('_NM Acc ID', 35))
fp.write(string.ljust('EG ID of _NM', 35) + CRT)

results = db.sql('select a.accID from #acc a ' + \
	'where not exists (select 1 from #eg eg where a.accID = eg.rna) ' + \
	'order by a.accID', 'auto')
for r in results:
    fp.write(string.ljust(r['accID'], 35) + CRT)
fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.finish_nonps(fp)

