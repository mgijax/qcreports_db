#!/usr/local/bin/python

'''
#
# MRK_McvAnnot.py
#
# Report:
#	TR10429/marker MCV annotations (curated)
#
#    I would like to request a report with all current (official and interim) 
#    markers and their Feature Types.
#
#    It is best to have the following columns that is similar to the load file f
#    or Feature type update.
#
#    I would like to use report to compare with my prediction and generate new 
#    file for an update load. I would like to have it as a regular weekly report
#
#      1. MCV ID
#      2. Marker MGI ID
#      3. J: (J:#####)
#      4. Evidence Code Abbreviation (max length 5)
#      5. Inferred From 
#      6. Qualifier - may be blank
#      7. Editor user login
#      8. Date (MM/DD/YYYY) - may be blank, if so date of load is used.
#      9. Blank
#      10. Notes - may be blank (max length 255)
#      11. MCV term (For example, protein coding gene)
#
#	sc note - columns 1-10 are the mcvload annotation format, columns 11+ 
#	          are for curation purposes and ignored by the load. Be mindful
#	          of this when editing this report.
# Usage:
#       "MRK_McvAnnot.py
#
# Notes:
#
# History:
#
# sc	10/26/2010  TR10429
#
'''

import sys 
import os
import re
import db
import reportlib

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'],printHeading = None)

fp.write('MCV ID%sMarker MGI ID%sJ:%sEvidence Code Abbreviation%sInferred From%sQualifier%sEditor User Login%sAnnotation Date%sNotes%sAlways Blank%sMCV Term%s' % (TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, CRT) )

#
# Load the note lookup for easy access to notes
# _NoteType_key = 1008 -  General VOC_Evidence note
# _MGIType_key = 25 # - annotation evidence
noteLookup = {}
results = db.sql('''select n._Object_key as annotKey, nc.note as chunk
        from MGI_Note n, MGI_NoteChunk nc
        where n._NoteType_key = 1008
        and n._MGIType_key = 25
        and n._Note_key = nc._Note_key
	order by n._Object_key''', 'auto')

for r in results:
    annotKey = r['annotKey']
    chunk = r['chunk']
    if not noteLookup.has_key(annotKey):
	noteLookup[annotKey] = []
    noteLookup[annotKey].append(chunk)

db.sql('''select va.*, t1.term as mcvTerm, t2.term as qualifier, a1.accid as mcvID, a2.accid as mgiID
    into #mcvAnnot
    from VOC_Annot va, VOC_Term t1, VOC_Term t2, ACC_Accession a1, ACC_Accession a2
    where va._AnnotType_key = 1011
    and va._Term_key = t1._Term_key
    and va._Qualifier_key = t2._term_key
    and va._Term_key = a1._Object_key
    and a1._MGIType_key = 13
    and a1.prefixPart = "MCV:"
    and va._Object_key = a2._Object_key
    and a2._MGIType_key = 2
    and a2._LogicalDB_key = 1
    and a2.prefixPart = 'MGI:'
    and a2.preferred = 1''', None)

db.sql('''create index idx1 on #mcvAnnot(_Annot_key)''', None)

results = db.sql('''select  ma.qualifier, convert(char(10), 
	a.creation_date, 101) as creation_date, e._AnnotEvidence_key as evidKey,
	ma.mcvTerm, ma.mcvID, ma.mgiID, a.accid as jnum, e.inferredFrom, u.login, 
	t.term as evidCode
    from #mcvAnnot ma, VOC_Evidence e, ACC_Accession a, MGI_User u, VOC_Term t
    where ma._Annot_key = e._Annot_key
    and e._CreatedBy_key = u._User_key
    and e._Refs_key = a._Object_key
    and a._MGIType_key = 1
    and a._LogicalDB_key = 1
    and a.prefixPart = "J:"
    and a.preferred = 1
    and e._EvidenceTerm_key = t._Term_key''', 'auto')

for r in results:
    evidKey = r['evidKey']
    mcvID = r['mcvID']
    mgiID = r['mgiID']
    jnum = r['jnum']
    evidCode =  r['evidCode']
    inferredFrom =  r['inferredFrom']
    if inferredFrom == None:
	inferredFrom = ''
    qualifier = r['qualifier']
    if qualifier == None:
	qualifier = ''
    login = r['login']
    date = r['creation_date']
    mcvTerm = r['mcvTerm']
    note = ''
    col10 = '' # always empty as supposed to follow mcvload format
    if noteLookup.has_key(evidKey):
	chunkList = noteLookup[evidKey]
	note = ''.join(chunkList).strip()
	note = re.sub('\n', ' ', note)
    fp.write('%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (mcvID, TAB, mgiID, TAB, jnum, TAB, evidCode, TAB, inferredFrom, TAB, qualifier, TAB, login, TAB, date, TAB, note, TAB, col10, TAB, mcvTerm, CRT))

reportlib.finish_nonps(fp)

