#!/usr/local/bin/python

'''
#
# SEQ_Marker.py 05/27/2004
#
# Report:
#	TR 5853
#
#       Tab-delimited file
#       Sequences Annotated to Mouse Markers
#
#	Sequence ID (primary)
#	Sequence Type
#	Length
#	Strain
#	Description
#	Clone Collection
#	Marker Accession ID
#	Marker Symbol
#	Marker Type
#
# Usage:
#       SEQ_Marker.py
#
# Used by:
#       Donnie Qi
#
# Notes:
#
# History:
#
# lec	05/27/2004
#	- new
#
'''
 
import sys
import os
import string
import regsub
import db
import mgi_utils
import reportlib

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)

cmds = []

cmds.append('select distinct _Sequence_key, _Marker_key into #seqmarker from SEQ_Marker_Cache')
cmds.append('create index idx_key1 on #seqmarker(_Sequence_key)')
cmds.append('create index idx_key2 on #seqmarker(_Marker_key)')

cmds.append('select distinct _Sequence_key into #uniqueseq from #seqmarker')
cmds.append('create index idx_key on #uniqueseq(_Sequence_key)')

cmds.append('select distinct _Marker_key into #uniquemrk from #seqmarker')
cmds.append('create index idx_key on #uniquemrk(_Marker_key)')

# select Seq IDs

cmds.append('select a.accID, a._Object_key ' + \
	'into #accSeq ' + \
	'from #uniqueseq s, ACC_Accession a ' + \
	'where s._Sequence_key = a._Object_key ' + \
	'and a._MGIType_key = 19 ' + \
	'and a.preferred = 1')

cmds.append('create index idx_key on #accSeq(_Object_key)')

# select MGI IDs

cmds.append('select a.accID, a._Object_key ' + \
	'into #accMrk ' + \
	'from #uniquemrk s, ACC_Accession a ' + \
	'where s._Marker_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1')

cmds.append('create index idx_key on #accMrk(_Object_key)')

# select other marker attributes

cmds.append('select markerID = a.accID, m._Marker_key, m.symbol, markerType = t.name ' + \
	'into #markers ' + \
	'from #accMrk a, MRK_Marker m, MRK_Types t ' + \
	'where a._Object_key = m._Marker_key ' + \
	'and m._Marker_Type_key = t._Marker_Type_key')

cmds.append('create index idx_key on #markers(_Marker_key)')

# select Sequence strain

cmds.append('select s._Sequence_key, ps.strain ' + \
	'into #seqStrain ' + \
	'from #uniqueseq s, SEQ_Source_Assoc sa, PRB_Source ss, PRB_Strain ps ' + \
	'where s._Sequence_key = sa._Sequence_key ' + \
	'and sa._Source_key = ss._Source_key ' + \
	'and ss._Strain_key = ps._Strain_key')

cmds.append('create index idx_key on #seqStrain(_Sequence_key)')

# select Sequence attributes

cmds.append('select a.accID, _Sequence_key = a._Object_key, sq.length, sq.description, seqType = t.term ' + \
	'into #seqAttr ' + \
	'from #accSeq a, SEQ_Sequence sq, VOC_Term t ' + \
	'where a._Object_key = sq._Sequence_key ' + \
	'and sq._SequenceType_key = t._Term_key ')

cmds.append('create index idx_key on #seqAttr(_Sequence_key)')

cmds.append('select s._Sequence_key, s.accID, s.length, s.description, s.seqType, ps.strain ' + \
	'into #sequences ' + \
	'from #seqAttr s, #seqStrain ps ' + \
	'where s._Sequence_key = ps._Sequence_key')

cmds.append('create index idx_key on #sequences(_Sequence_key)')

cmds.append('select s._Sequence_key, cl.name ' + \
	'into #seqCloneSet ' + \
	'from #uniqueSeq s, SEQ_Source_Assoc sa, MGI_SetMember sm, MGI_Set_CloneLibrary_View cl ' + \
	'where s._Sequence_key = sa._Sequence_key ' + \
	'and sa._Source_key = sm._Object_key ' + \
	'and sm._Set_key = cl._Set_key ')

#
# This is what we'll process...
#

# clone set info

cmds.append('select _Sequence_key, name from #seqCloneSet')

# sequence info with cross-reference to marker
cmds.append('select s.*, ms._Marker_key, m.markerID, m.symbol, m.markerType ' + \
	'from #sequences s, #seqmarker ms, #markers m ' + \
	'where s._Sequence_key = ms._Sequence_key ' + \
	'and ms._Marker_key = m._Marker_key ' + \
	'order by s.accID')

results = db.sql(cmds, 'auto')

cloneSet = {}
for r in results[-2]:
	key = r['_Sequence_key']
	value = r['name']
	if not cloneSet.has_key(key):
		cloneSet[key] = []
	cloneSet[key].append(value)
	
for r in results[-1]:

    fp.write(r['accID'] + reportlib.TAB + \
	r['seqType'] + reportlib.TAB + \
	mgi_utils.prvalue(r['length']) + reportlib.TAB + \
	r['strain'] + reportlib.TAB + \
	mgi_utils.prvalue(r['description']) + reportlib.TAB)

    if cloneSet.has_key(r['_Sequence_key']):
	fp.write(string.join(cloneSet[r['_Sequence_key']], ','))

    fp.write(reportlib.TAB + \
        r['markerID'] + reportlib.TAB + \
	r['symbol'] + reportlib.TAB + \
	r['markerType'] + reportlib.CRT)

reportlib.finish_nonps(fp)

