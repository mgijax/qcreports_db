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

fp = reportlib.init(sys.argv[0], title = "Molecular Segment with the Problem Sequence Note associated with more than one GenBank Seqid or associated with no GenBank ID", outputdir = os.environ['QCREPORTOUTPUTDIR'])

cmds = []

# Select probes w/ problem note
cmds.append('select _Probe_key ' + \
      'into #probes ' + \
      'from PRB_Notes ' + \
      'where note like "%staff have found evidence of artifact in the sequence of this molecular%"')

# Select probes w/ Seq IDs
cmds.append('select distinct p._Probe_key, a.accID ' + \
'into #probeseqs ' + \
'from #probes p, PRB_Acc_View a ' + \
'where p._Probe_key = a._Object_key  ' + \
'and a._LogicalDB_key = 9 ')

# Select probes with more than one Seq ID
cmds.append('select * into #formgi from #probeseqs group by accID having count(*) > 1')

# Select MGI Acc ID for probes with > 1 Seq ID
cmds.append('select m.*, probeID = pa.accID ' + \
'from #formgi m, PRB_Acc_View pa ' + \
'where m._Probe_key = pa._Object_key ' + \
'and pa.prefixPart = "MGI:" ' + \
'order by m._Probe_key')

results = db.sql(cmds, 'auto')

prevProbe = ''
sequences = []

for r in results[-1]:

	if prevProbe != r['_Probe_key']:
		if len(sequences) > 0:
			fp.write(string.join(sequences, ','))
		sequences = ''

		if prevProbe != '':
			fp.write(reportlib.CRT)

		fp.write(mgi_utils.prvalue(r['probeID']) + reportlib.TAB)

		prevProbe = r['_Probe_key']
		sequences = []

	if r['accID'] is not None:
        	sequences.append(r['accID'])

fp.write(string.join(sequences, ','))
reportlib.finish_nonps(fp)

