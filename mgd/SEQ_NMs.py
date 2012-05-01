#!/usr/local/bin/python

'''
#
# SEQ_NMs.py
#
# Report:
#	TR 8125
#
#
# NM sequences that are not associated with any MGI mouse marker
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

# mouse entrezgene load buckets

egbucketsdir = os.environ['DATALOADSOUTPUT'] + '/entrezgene/egload/reports/'

egbuckets = {'1:N' : 'bucket_one_to_many.txt',
	     '0:1' : 'bucket_zero_to_one.txt',
	     'N:1' : 'bucket_many_to_one.txt',
	     'N:M' : 'bucket_many_to_many.txt'
	     }

# define what field contains the EG ID in each bucket, and subtract 1

egfield = {'1:N' : 3,
	   '0:1' : 0,
	   'N:1' : 3,
	   'N:M' : 3
	   }

def searchBuckets(id):

    #
    # determine which bucket the EG ID is in by looking
    # at the EG ID field in each bucket
    #
    # IDs should be found in at most one bucket
    #

    whichBucket = 'not found'

    for b in egbuckets.keys():

	i = egfield[b]
        found = 0

	bfile = egbucketsdir + egbuckets[b]
        bfp = open(bfile, 'r')

	for line in bfp.readlines():
	    tokens = string.split(line[:-1], TAB)

	    # lines without ids

	    if len(tokens) < i:
		continue

	    # if id is found, we're done

	    if id == tokens[i]:
		found = 1
		break

	bfp.close()

	if found:
	    whichBucket = b

    return whichBucket

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
db.sql('create index sequences_idx1 on #sequence(_Sequence_key)', None)

#
# ...NMs
#

db.sql('select s._Sequence_key, a.accID ' + \
	'into #acc ' + \
	'from #sequence s, ACC_Accession a ' + \
	'where s._Sequence_key = a._Object_key ' + \
	'and a._MGIType_key = 19 ' + \
	'and a.prefixPart = "NM_"', None)
db.sql('create index acc_idx1 on #acc(accID)', None)

#
# cache NMs in EntrezGene
#

db.sql('select eg.rna, eg.geneID ' + \
	'into #eg ' + \
	'from %s..DP_EntrezGene_Accession eg ' % (os.environ['RADAR_DBNAME']) + \
	'where eg.taxID = 10090 ' + \
	'and eg.rna like "NM_%" ', None)
db.sql('create index eg_idx1 on #eg(rna)', None)

fp.write(CRT + "NM's falling into EG Buckets" + 2*CRT)
fp.write(string.ljust('NM Acc ID', 35))
fp.write(string.ljust('EG ID of NM', 35))
fp.write(string.ljust('MGI/EG Bucket', 35) + CRT)
fp.write(string.ljust('---------', 35))
fp.write(string.ljust('-----------', 35))
fp.write(string.ljust('-------------', 35) + CRT)

#
# retrieve results and sort them into their appropriate buckets
#

bresults = {}
results = db.sql('select distinct a.accID, eg.geneID ' + \
	'from #acc a, #eg eg ' + \
	'where a.accID = eg.rna ' + \
	'order by a.accID ', 'auto')
for r in results:
    bucket = searchBuckets(r['geneID'])
    if not bresults.has_key(bucket):
	bresults[bucket] = []
    bresults[bucket].append(r)

#
# sort the buckets and print them out
#

c = 0
bkeys = bresults.keys()
bkeys.sort()
for b in bkeys:
    for r in bresults[b]:
        fp.write(string.ljust(r['accID'], 35))
        fp.write(string.ljust(r['geneID'], 35))
        fp.write(string.ljust(b, 35) + CRT)
	c = c + 1
fp.write('\n(%d rows affected)\n' % (c))

#
# those NMs that are not in the EG file
#

fp.write(CRT + "NM's not in EG File" + 2*CRT)
fp.write(string.ljust('NM Acc ID', 35) + CRT)
fp.write(string.ljust('---------', 35) + CRT)

results = db.sql('select a.accID from #acc a ' + \
	'where not exists (select 1 from #eg eg where a.accID = eg.rna) ' + \
	'order by a.accID', 'auto')
for r in results:
    fp.write(string.ljust(r['accID'], 35) + CRT)
fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.finish_nonps(fp)

