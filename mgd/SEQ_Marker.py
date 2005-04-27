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

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = 0)

# select all distinct sequences/markers, excluding certain providers
# exclude RefSeq, Dots, TIGR Mouse Gene Index, NIA Mouse Gene Index

db.sql('select s._Sequence_key, s._Marker_key ' + \
	'into #seqMarker1 ' + \
	'from SEQ_Marker_Cache s, SEQ_Sequence ss ' + \
	'where s._Sequence_key = ss._Sequence_key ' + \
	'and ss._SequenceProvider_key not in (316372, 316382, 316381, 316383)', None)

db.sql('create index idx_key1 on #seqMarker1(_Sequence_key)', None)
db.sql('create index idx_key2 on #seqMarker1(_Marker_key)', None)

db.sql('select distinct _Sequence_key, _Marker_key into #seqMarker from #seqMarker1', None)
db.sql('create index idx_key1 on #seqMarker(_Sequence_key)', None)
db.sql('create index idx_key2 on #seqMarker(_Marker_key)', None)

# select unique sequences
db.sql('select distinct _Sequence_key into #uniqueSeq from #seqMarker', None)
db.sql('create index idx_key on #uniqueSeq(_Sequence_key)', None)

# select unique markers
db.sql('select distinct _Marker_key into #uniqueMrk from #seqMarker', None)
db.sql('create index idx_key on #uniqueMrk(_Marker_key)', None)

# select Seq IDs
db.sql('select a.accID, a._Object_key ' + \
	'into #accSeq ' + \
	'from #uniqueSeq s, ACC_Accession a ' + \
	'where s._Sequence_key = a._Object_key ' + \
	'and a._MGIType_key = 19 ' + \
	'and a.preferred = 1', None)
db.sql('create index idx_key on #accSeq(_Object_key)', None)

# select marker MGI IDs
db.sql('select a.accID, a._Object_key ' + \
	'into #accMrk ' + \
	'from #uniqueMrk s, ACC_Accession a ' + \
	'where s._Marker_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1', None)
db.sql('create index idx_key on #accMrk(_Object_key)', None)

# select other marker attributes

db.sql('select markerID = a.accID, m._Marker_key, m.symbol, markerType = t.name ' + \
	'into #markers ' + \
	'from #accMrk a, MRK_Marker m, MRK_Types t ' + \
	'where a._Object_key = m._Marker_key ' + \
	'and m._Marker_Type_key = t._Marker_Type_key', None)
db.sql('create index idx_key on #markers(_Marker_key)', None)

# select Sequence attributes

db.sql('select a.accID, _Sequence_key = a._Object_key, sq.length, sq.description, ' + \
	'sq._SequenceType_key, sq._SequenceProvider_key ' + \
	'into #seqAttr ' + \
	'from #accSeq a, SEQ_Sequence sq ' + \
	'where a._Object_key = sq._Sequence_key ', None)
db.sql('create index idx_key1 on #seqAttr(_Sequence_key)', None)
db.sql('create index idx_key2 on #seqAttr(_SequenceType_key)', None)
db.sql('create index idx_key3 on #seqAttr(_SequenceProvider_key)', None)
db.sql('create index idx_key4 on #seqAttr(accID)', None)

db.sql('select s._Sequence_key, t.term ' + \
	'into #seqType ' + \
	'from #seqAttr s, VOC_Term t ' + \
	'where s._SequenceType_key = t._Term_key ', None)

db.sql('create index idx_key on #seqType(_Sequence_key)', None)

db.sql('select s._Sequence_key, t.term ' + \
	'into #seqProvider ' + \
	'from #seqAttr s, VOC_Term t ' + \
	'where s._SequenceProvider_key = t._Term_key ', None)

db.sql('create index idx_key on #seqProvider(_Sequence_key)', None)

db.sql('select s._Sequence_key, ps.strain ' + \
	'into #seqStrain ' + \
	'from #uniqueSeq s, SEQ_Source_Assoc sa, PRB_Source ss, PRB_Strain ps ' + \
	'where s._Sequence_key = sa._Sequence_key ' + \
	'and sa._Source_key = ss._Source_key ' + \
	'and ss._Strain_key = ps._Strain_key', None)

db.sql('create index idx_key on #seqStrain(_Sequence_key)', None)

db.sql('select s._Sequence_key, cl.name ' + \
	'into #seqCloneSet ' + \
	'from #uniqueSeq s, SEQ_Source_Assoc sa, MGI_SetMember sm, MGI_Set_CloneLibrary_View cl ' + \
	'where s._Sequence_key = sa._Sequence_key ' + \
	'and sa._Source_key = sm._Object_key ' + \
	'and sm._Set_key = cl._Set_key ', None)

#
# This is what we'll process...
#

# sequence type info
results = db.sql('select _Sequence_key, term from #seqType', 'auto')
seqType = {}
for r in results:
	key = r['_Sequence_key']
	value = r['term']
	seqType[key] = value
	
# sequence provider info
results = db.sql('select _Sequence_key, term from #seqProvider', 'auto')
seqProvider = {}
for r in results:
	key = r['_Sequence_key']
	value = r['term']
	seqProvider[key] = value

# sequence strain info
results = db.sql('select _Sequence_key, strain from #seqStrain', 'auto')
seqStrain = {}
for r in results:
	key = r['_Sequence_key']
	value = r['strain']
	seqStrain[key] = value

# clone set info
results = db.sql('select _Sequence_key, name from #seqCloneSet', 'auto')
cloneSet = {}
for r in results:
	key = r['_Sequence_key']
	value = r['name']
	if not cloneSet.has_key(key):
		cloneSet[key] = []
	cloneSet[key].append(value)

# marker info
results = db.sql('select ms._Sequence_key, m.markerID, m.symbol, m.markerType ' + \
	'from #seqMarker ms, #markers m ' + \
	'where ms._Marker_key = m._Marker_key ', 'auto')
seqMarker = {}
for r in results:
	key = r['_Sequence_key']
	value = []
	value.append(r['markerID'])
	value.append(r['symbol'])
	value.append(r['markerType'])
	if not seqMarker.has_key(key):
		seqMarker[key] = []
	seqMarker[key].append(value)
	
# sorted sequence info
results = db.sql('select * from #seqAttr order by accID', 'auto')
for r in results:

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

#print 'report done'
#print mgi_utils.date()

