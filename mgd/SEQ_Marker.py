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

# select all distinct sequences/markers, excluding certain providers
cmds.append('select distinct s._Sequence_key, s._Marker_key ' + \
	'into #seqMarker ' + \
	'from SEQ_Marker_Cache s, SEQ_Sequence ss, VOC_Term t ' + \
	'where s._Sequence_key = ss._Sequence_key ' + \
	'and ss._SequenceProvider_key = t._Term_key ' + \
	'and t.term not in ("DoTS", "TIGR Mouse Gene Index", "NIA Mouse Gene Index")')

cmds.append('create index idx_key1 on #seqMarker(_Sequence_key)')
cmds.append('create index idx_key2 on #seqMarker(_Marker_key)')

# select unique sequences
cmds.append('select distinct _Sequence_key into #uniqueSeq from #seqMarker')
cmds.append('create index idx_key on #uniqueSeq(_Sequence_key)')

# select unique markers
cmds.append('select distinct _Marker_key into #uniqueMrk from #seqMarker')
cmds.append('create index idx_key on #uniqueMrk(_Marker_key)')

# select Seq IDs
cmds.append('select a.accID, a._Object_key ' + \
	'into #accSeq ' + \
	'from #uniqueSeq s, ACC_Accession a ' + \
	'where s._Sequence_key = a._Object_key ' + \
	'and a._MGIType_key = 19 ' + \
	'and a.preferred = 1')

cmds.append('create index idx_key on #accSeq(_Object_key)')

# select marker MGI IDs
cmds.append('select a.accID, a._Object_key ' + \
	'into #accMrk ' + \
	'from #uniqueMrk s, ACC_Accession a ' + \
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
cmds.append('create index idx_key4 on #seqAttr(accID)')

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
	'from #uniqueSeq s, SEQ_Source_Assoc sa, PRB_Source ss, PRB_Strain ps ' + \
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

# marker info
cmds.append('select ms._Sequence_key, m.markerID, m.symbol, m.markerType ' + \
	'from #seqMarker ms, #markers m ' + \
	'where ms._Marker_key = m._Marker_key ')

# sorted sequence info
cmds.append('select * from #seqAttr order by accID')

print 'results executing'
print mgi_utils.date()

results = db.sql(cmds, 'auto')

print 'results done'
print mgi_utils.date()

seqType = {}
for r in results[-6]:
	key = r['_Sequence_key']
	value = r['term']
	seqType[key] = value
	
seqProvider = {}
for r in results[-5]:
	key = r['_Sequence_key']
	value = r['term']
	seqProvider[key] = value
	
seqStrain = {}
for r in results[-4]:
	key = r['_Sequence_key']
	value = r['strain']
	seqStrain[key] = value
	
cloneSet = {}
for r in results[-3]:
	key = r['_Sequence_key']
	value = r['name']
	if not cloneSet.has_key(key):
		cloneSet[key] = []
	cloneSet[key].append(value)
	
seqMarker = {}
for r in results[-2]:
	key = r['_Sequence_key']
	value = []
	value.append(r['markerID'])
	value.append(r['symbol'])
	value.append(r['markerType'])
	if not seqMarker.has_key(key):
		seqMarker[key] = []
	seqMarker[key].append(value)
	
for r in results[-1]:

    key = r['_Sequence_key']

    markers = seqMarker[r['_Sequence_key']]

    for m in markers:

        fp.write(r['accID'] + reportlib.TAB + \
	    seqProvider[key] + reportlib.TAB + \
	    seqType[key] + reportlib.TAB + \
	    mgi_utils.prvalue(r['length']) + reportlib.TAB + \
	    seqStrain[key] + reportlib.TAB + \
	    mgi_utils.prvalue(r['description']) + reportlib.TAB)

        if cloneSet.has_key(r['_Sequence_key']):
	    fp.write(string.join(cloneSet[r['_Sequence_key']], ','))

	for f in m:
          fp.write(reportlib.TAB + f)
    
        fp.write(reportlib.CRT)

reportlib.finish_nonps(fp)

print 'report done'
print mgi_utils.date()

