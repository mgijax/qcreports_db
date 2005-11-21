#!/usr/local/bin/python

'''
#
# MGI_ProblemSequence.py 09/18/2001
# Companion to public report with the same name.
#
# Report:
#	TR 2943
#       Tab-delimited file
#
#	If a given Molecular Segment with the Problem Sequence Note is associated with 
#       more than one GenBank seqid, then information from this Segment should not go 
#       to the public NCBI Problem Sequence Report (since we can't be sure which is the
#       problem sequence), but to a discrepancy report. This tab-delimited report is for 
#       MGI use only, and should contain the following fields: 
#
#       1. MGI ID for the Molecular Segment 
#       2. GenBank Sequence Identifiers, comma delimited. 
#
# Problem Sequence Note:
#
# "MGI curatorial staff have found evidence of artifact in the sequence of this molecular"
# "segment. The artifact may have been introduced during the cloning process, or may be"
# "due to unreliable sequence data."
#
# Usage:
#       MGI_ProblemSequence.py
#
# Used by:
#       MGI Curatorial Group
#
# Notes:
#
# History:
#
# lec	09/18/2001
#	- new
#
'''
 
import sys
import os
import string
import db
import mgi_utils
import reportlib

#
# Main
#

fp = reportlib.init(sys.argv[0], title = "Molecular Segment with the Problem Sequence Note associated with more than one GenBank Seqid or associated with no GenBank ID", outputdir = os.environ['QCOUTPUTDIR'])

# Select probes w/ problem note
db.sql('select _Probe_key ' + \
      'into #probes ' + \
      'from PRB_Notes ' + \
      'where note like "%staff have found evidence of artifact in the sequence of this molecular%"', None)
db.sql('create index idx1 on #probes(_Probe_key)', None)

##

# Select probes w/ Seq IDs

db.sql('select distinct p._Probe_key, a.accID ' + \
	'into #probeseqs ' + \
	'from #probes p, ACC_Accession a ' + \
	'where p._Probe_key = a._Object_key  ' + \
	'and a._MGIType_key = 3 ' + \
	'and a._LogicalDB_key = 9 ', None)

# Select probes with more than one Seq ID

db.sql('select _Probe_key into #formgi from #probeseqs group by accID having count(*) > 1', None)
db.sql('create index idx1 on #formgi(_Probe_key)', None)

# Store Seq IDs for probes

results = db.sql('select p._Probe_key, p.accID ' + \
	'from #formgi m, #probeseqs p ' + \
	'where m._Probe_key = p._Probe_key', 'auto')
sequences = {}
for r in results:
    key = r['_Probe_key']
    value = r['accID']
    if not sequences.has_key(key):
	sequences[key] = []
    sequences[key].append(value)

# Select MGI Acc ID for probes with > 1 Seq ID

results = db.sql('select m._Probe_key, probeID = pa.accID ' + \
	'from #formgi m, ACC_Accession pa ' + \
	'where m._Probe_key = pa._Object_key ' + \
	'and pa._MGIType_key = 3 ' + \
	'and pa.prefixPart = "MGI:" ' + \
	'order by m._Probe_key', 'auto')

for r in results:
    fp.write(r['probeID'] + reportlib.TAB + \
	string.join(sequences[r['_Probe_key']], ',') + reportlib.CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.finish_nonps(fp)
