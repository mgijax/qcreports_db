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
#	(excludes TIGR, DoTS, NIA Mouse Gene Index)
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

cmds.append('select distinct s._Sequence_key, s._Marker_key ' + \
	'into #seqmarker ' + \
	'from SEQ_Marker_Cache s, SEQ_Sequence ss, VOC_Term t ' + \
	'where s._Sequence_key = ss._Sequence_key ' + \
	'and ss._SequenceProvider_key = t._Term_key ' + \
	'and t.term not in ("DoTS", "TIGR Mouse Gene Index", "NIA Mouse Gene Index")')

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

# select Sequence attributes

cmds.append('select a.accID, _Sequence_key = a._Object_key, sq.length, sq.description, ' + \
	'sq._SequenceType_key, sq._SequenceProvider_key ' + \
	'into #seqAttr ' + \
	'from #accSeq a, SEQ_Sequence sq ' + \
	'where a._Object_key = sq._Sequence_key ')

cmds.append('create index idx_key1 on #seqAttr(_Sequence_key)')
cmds.append('create index idx_key2 on #seqAttr(_SequenceType_key)')
cmds.append('create index idx_key3 on #seqAttr(_SequenceProvider_key)')

cmds.append('select s._Sequence_key, t.term ' + \
	'into #seqType ' + \
	'from #seqAttr s, VOC_Term t ' + \
	'where s._SequenceType_key = t._Term_key ')

cmds.append('create index idx_key on #seqType(_Sequence_key)')

cmds.append('select s._Sequence_key, t.term ' + \
	'into #seqProvider ' + \
	'from #seqAttr s, VOC_Term t ' + \
	'where s._SequenceProvider_key = t._Term_key ')

cmds.append('create index idx_key on #seqProvider(_Sequence_key)')

cmds.append('select s._Sequence_key, ps.strain ' + \
	'into #seqStrain ' + \
	'from #uniqueseq s, SEQ_Source_Assoc sa, PRB_Source ss, PRB_Strain ps ' + \
	'where s._Sequence_key = sa._Sequence_key ' + \
	'and sa._Source_key = ss._Source_key ' + \
	'and ss._Strain_key = ps._Strain_key')

cmds.append('create index idx_key on #seqStrain(_Sequence_key)')

cmds.append('select s._Sequence_key, cl.name ' + \
	'into #seqCloneSet ' + \
	'from #uniqueSeq s, SEQ_Source_Assoc sa, MGI_SetMember sm, MGI_Set_CloneLibrary_View cl ' + \
	'where s._Sequence_key = sa._Sequence_key ' + \
	'and sa._Source_key = sm._Object_key ' + \
	'and sm._Set_key = cl._Set_key ')

#
# This is what we'll process...
#

# sequence type info
cmds.append('select _Sequence_key, term from #seqType')

# sequence provider info
cmds.append('select _Sequence_key, term from #seqProvider')

# sequence strain info
cmds.append('select _Sequence_key, strain from #seqStrain')

# clone set info
cmds.append('select _Sequence_key, name from #seqCloneSet')

# sequence info with cross-reference to marker
cmds.append('select s.*, ms._Marker_key, m.markerID, m.symbol, m.markerType ' + \
	'from #seqAttr s, #seqmarker ms, #markers m ' + \
	'where s._Sequence_key = ms._Sequence_key ' + \
	'and ms._Marker_key = m._Marker_key ' + \
	'order by s.accID')

results = db.sql(cmds, 'auto')

seqType = {}
for r in results[-5]:
	key = r['_Sequence_key']
	value = r['term']
	if not seqType.has_key(key):
		seqType[key] = []
	seqType[key].append(value)
	
seqProvider = {}
for r in results[-4]:
	key = r['_Sequence_key']
	value = r['term']
	if not seqProvider.has_key(key):
		seqProvider[key] = []
	seqProvider[key].append(value)
	
seqStrain = {}
for r in results[-3]:
	key = r['_Sequence_key']
	value = r['strain']
	if not seqStrain.has_key(key):
		seqStrain[key] = []
	seqStrain[key].append(value)
	
cloneSet = {}
for r in results[-2]:
	key = r['_Sequence_key']
	value = r['name']
	if not cloneSet.has_key(key):
		cloneSet[key] = []
	cloneSet[key].append(value)
	
for r in results[-1]:

    fp.write(r['accID'] + reportlib.TAB + \
	seqProvider[r['_Sequence_key']] + reportlib.TAB + \
	seqType[r['_Sequence_key']] + reportlib.TAB + \
	mgi_utils.prvalue(r['length']) + reportlib.TAB + \
	seqStrain[r['_Sequence_key']] + reportlib.TAB + \
	mgi_utils.prvalue(r['description']) + reportlib.TAB)

    if cloneSet.has_key(r['_Sequence_key']):
	fp.write(string.join(cloneSet[r['_Sequence_key']], ','))

    fp.write(reportlib.TAB + \
        r['markerID'] + reportlib.TAB + \
	r['symbol'] + reportlib.TAB + \
	r['markerType'] + reportlib.CRT)

reportlib.finish_nonps(fp)

