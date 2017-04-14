#!/usr/local/bin/python

'''
#
# PHENO_Features.py
#
# Report:
#       Report of all expressed component and mutation involves relationships in the database
#
# Usage:
#       PHENO_Features.py
#
# History:
#
# 04/07/2017	sc
#	- TR12551
#
'''

import sys 
import os
import string
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB
NON_MOUSE_ORG = 'Non-mouse_Organism'
NON_MOUSE_GS = 'Non-mouse_Gene_Symbol'
NON_MOUSE_GI = 'Non-mouse_NCBI_Gene_ID'

def doSQL(category):
    db.useOneConnection(1)
    db.sql('''select r._Relationship_key, c.name as category, 
		t1.term as relationship, a1.accid as rvId, 
		t2.abbreviation as qualifier, t3.abbreviation as evidence, 
		u.login, aa.symbol as alleleSymbol, a2.accid as alleleId, 
		m.symbol as markerSymbol, a3.accid as markerId, a4.accid as JNum
	    into temporary table relationships
	    from MGI_Relationship r, MGI_Relationship_Category c, VOC_Term t1, 
		ACC_Accession a1, VOC_Term t2, VOC_Term t3, MGI_User u, 
		ALL_Allele aa, ACC_Accession a2, MRK_Marker m, ACC_Accession a3, 
		ACC_Accession a4
	    where r._Category_key = %s
	    and r._Category_key = c._Category_key
	    and r._RelationshipTerm_key = t1._Term_key
	    and r._RelationshipTerm_key = a1._Object_key
	    and a1._MGIType_key = 13
	    and a1._LogicalDB_key = 171
	    and a1.preferred = 1
	    and r._Qualifier_key = t2._Term_key
	    and r._Evidence_key = t3._Term_key
	    and r._CreatedBy_key = u._User_key
	    and r._Object_key_1 = aa._Allele_key
	    and r._Object_key_1 = a2._Object_key
	    and a2._MGIType_key = 11
	    and a2._LogicalDB_key = 1
	    and a2.preferred = 1
	    and a2.prefixPart = 'MGI:'
	    and r._Object_key_2 = m._Marker_key
	    and r._Object_key_2 = a3._Object_key
	    and a3._MGIType_key = 2
	    and a3._LogicalDB_key = 1
	    and a3.preferred = 1
	    and a3.prefixPart = 'MGI:'
	    and r._Refs_key = a4._Object_key
	    and a4._MGIType_key = 1
	    and a4._LogicalDB_key = 1
	    and a4.preferred = 1
	    and a4.prefixPart = 'J:' ''' % category , None)
	    
    db.sql('create index idx1 on relationships (_Relationship_key)', None)
    
    # get the notes for subsequent left outer join
    db.sql('''select n._Note_key, nc.Note, n._Object_key
	    into temporary table notes
	    from MGI_Note n, MGI_NoteChunk nc
	    where n._Note_key = nc._Note_key
	    and n._NoteType_key = 1042''', None)

    db.sql('create index idx2 on notes(_Object_key)', None)

    db.sql('''select r.*, n.note
	into temporary table relNotes
	    from relationships r
	    left outer join notes n on (
		r._Relationship_key = n._Object_key)''', None)
    results = {}
    if category == 1004: # expresses component, has properties 
	db.sql('create index idx3 on relNotes(_Relationship_key)', None)
     
	results = db.sql('''select distinct r.*, t.term as propName, p.value as propValue
	    from relNotes r
	    left outer join MGI_Relationship_Property p on (r._Relationship_key = p._Relationship_key)
	    left outer join  VOC_Term t on (p._PropertyName_key = t._Term_key)''', 'auto')
    else: #  mutation involves, no properties
	results = db.sql('''select * from relNotes''', 'auto')
    
    db.sql('''drop table relationships''', None)
    db.sql('''drop table notes''', None)
    db.sql('''drop table relNotes''', None)

    db.useOneConnection(0)
    
    resultsDict = {}
    for r in results:
	relKey = r['_Relationship_key']
	if relKey not in resultsDict:
	    resultsDict[relKey] = []
	resultsDict[relKey].append(r)
    return resultsDict

def writeReport(resultsDict, rptName, category):
    fp = reportlib.init(rptName, outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

    if category == 1004: # expressed component, has properties
	fp.write('Action%sCategory%sOrganizer ID%sOrganizer symbol%sRelationship ID%sRelationship Name%sParticipant ID%sParticipant Name%sQualifier%sAbbreviation%sEvidence Code%sjnum_id%sCurator ID%sNotes%sProperty:Non-mouse_Organism%sProperty:Non-mouse_Gene_Symbol%sProperty:Non-mouse_NCBI_Gene_ID%s' % (TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB,TAB, TAB, TAB, TAB, TAB, TAB, CRT))
    else: # 1003 mutation involves, no properties
    	fp.write('Action%sCategory%sOrganizer ID%sOrganizer symbol%sRelationship ID%sRelationship Name%sParticipant ID%sParticipant Name%sQualifier%sAbbreviation%sEvidence Code%sjnum_id%sCurator ID%sNotes%s' % (TAB, TAB, TAB, TAB, TAB, TAB,TAB, TAB, TAB, TAB, TAB, TAB, TAB, CRT))

    nmOrgVal = ''
    nmGSVal = ''
    nmGIVal = ''
    for r in resultsDict:
	# Each record in this list represents the same feature, 
	# but with different properties
	resultsList = resultsDict[r]
	cat = resultsList[0]['category']
	aId = resultsList[0]['alleleId']
	aSym = resultsList[0]['alleleSymbol']
	rvId = resultsList[0]['rvId']
	rel = resultsList[0]['relationship']
	mId = resultsList[0]['markerId']
	mSym = resultsList[0]['markerSymbol']
	qual = resultsList[0]['qualifier']
	evid = resultsList[0]['evidence']
	jnum = resultsList[0]['JNum']
	curator = resultsList[0] ['login']
	notes = resultsList[0]['note']
 	if notes == None:
	    notes = ''
	if category == 1004: # expresses component, get properties
	    nmOrgVal = ''
	    nmGSVal = ''
	    nmGIVal = ''

	    for res in resultsList:
		propName = res['propName']
		propValue = res['propValue']
		if propName == None:
		    continue
		elif propName == NON_MOUSE_ORG:
		    nmOrgVal = propValue
		elif propName == NON_MOUSE_GS:
		    nmGSVal = propValue
		elif propName == NON_MOUSE_GI:
		    nmGIVal = propValue
	    fp.write('%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (cat, TAB, aId, TAB, aSym, TAB, rvId, TAB, rel, TAB, mId, TAB, mSym, TAB, qual, TAB, evid, TAB, jnum, TAB, curator, TAB, notes, TAB, nmOrgVal, TAB, nmGSVal, TAB, nmGIVal, CRT) )
	else: # mutation involves
	    fp.write('%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (cat, TAB, aId, TAB, aSym, TAB, rvId, TAB, rel, TAB, mId, TAB, mSym, TAB, qual, TAB, evid, TAB,  jnum, TAB, curator, TAB, notes, CRT) )

    reportlib.finish_nonps(fp)	# non-postscript file

#
# Main
#

# expresses component has properties
results = doSQL(1004)
writeReport(results, 'PHENO_Features-ExpComp', 1004)

# mutation involves no properties
results = doSQL(1003)
writeReport(results, 'PHENO_Features-MutInv', 1003)
