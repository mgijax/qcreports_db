#!/usr/local/bin/python

'''
#
# Report:
#       TR10296/Allele/MP EI notes
#
# determine if certain Allele Notes contain HTML errors
#
# History:
#
# lec   10/22/2014
#       - TR11750/postres complient
#
# lec	09/30/2010-10/05/2010
#	- created
#
'''
 
import sys 
import os
import string
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

noteType = {1020: 'General',
	    1021: 'Molecular Notes'
	   }
	  
def alleleNotes():

    #
    # General notes
    # Molecular Notes
    #

    fp.write('\n\n#Note type\n')
    fp.write('#Allele symbol\n')
    fp.write('#Allele accession ID\n')
    fp.write('#Allele status\n')
    fp.write('#Created by\n')
    fp.write('#Created by date\n')
    fp.write('#Modified by\n')
    fp.write('#Modified by date\n')

    for n in noteType:

        fp.write('\n')

        #
        # select all alleles that contain note data with:
        #
        # c.note like '%<sup>%'
        # c.note like '%<sub>%'
        #

        sql = '''
	        select a._Allele_key, a.symbol, aa.accID, t.term, 
		       to_char(a.creation_date, 'MM/dd/yyyy') as cdate,
		       to_char(a.modification_date, 'MM/dd/yyyy') as mdate,
		       u1.login as clogin, u2.login as mlogin
	        into temporary table alleles
	        from ALL_Allele a, ACC_Accession aa, VOC_Term t, MGI_User u1, MGI_User u2
	        where a._Allele_key = aa._Object_key
	        and aa._MGIType_key = 11
	        and aa._LogicalDB_key = 1
	        and aa.preferred = 1
	        and a._Allele_Status_key = t._Term_key
	        and a._CreatedBy_key = u1._User_key
	        and a._ModifiedBy_key = u2._User_key
	        and exists (select * from MGI_Note n, MGI_NoteChunk c
	        where a._Allele_key = n._Object_key
	        and n._NoteType_key = %s
	        ''' % (n)

        db.sql(sql + '''
	        and n._Note_key = c._Note_key
	        and (lower(c.note) like '%<sup>%' or lower(c.note) like '%<sub>%'
	        ))
	        ''', None)

        db.sql('create index alleles_idx1 on alleles(_Allele_key)', None)

        #
        # concatenate notes
        #
        results = db.sql('''
	        select a._Allele_key, c.note
	        from alleles a, MGI_Note n, MGI_NoteChunk c
	        where a._Allele_key = n._Object_key
	        and n._NoteType_key = %s
	        and n._Note_key = c._Note_key
                order by n._Note_key, c.sequenceNum
	          ''' % (n), 'auto')

        notes = {}
        for r in results:
            key = r['_Allele_key']
            value = string.lower(r['note'])
    
            if notes.has_key(key):
	        notes[key] = notes[key] + value
            else:
	        notes[key] = value

        #
        # for each allele w/ notes:
        #	if note exists or has an error:
        #	   print the allele, note snippet
        #

        results = db.sql('select * from alleles order by symbol', 'auto')

        for r in results:
    
            snippets = []
            note = notes[r['_Allele_key']]

	    # if number of <sup> != number of </sup>, then add to snippet
            findA = string.count(note, '<sup>')
            findB = string.count(note, '</sup>')
            if findA != findB:
                findA = string.find(note, '<sup>')
                findB = string.find(note, '</sup>')
                snippets.append(note)

	    # if number of <sub> != number of </sub>, then add to snippet
            findA = string.count(note, '<sub>')
            findB = string.count(note, '</sub>')
            if findA != findB:
                snippets.append(note)

	    # if any snippets exist, then print
            if len(snippets) > 0:
                fp.write(noteType[n] + TAB)
                fp.write(r['symbol'] + TAB)
                fp.write(r['accID'] + TAB)
                fp.write(r['term'] + TAB)
                fp.write(r['clogin'] + TAB)
                fp.write(r['cdate'] + TAB)
                fp.write(r['mlogin'] + TAB)
                fp.write(r['mdate'] + CRT)
    
        db.sql('drop table alleles', None)

def mpNotes():

    #
    # MP notes (1008)
    #

    fp.write('\n\n#Note type\n')
    fp.write('#Genotype accession ID\n')
    fp.write('#Created by\n')
    fp.write('#Created by date\n')
    fp.write('#Modified by\n')
    fp.write('#Modified by date\n\n')

    #
    # select all genotypes that contain note data with:
    #
    # c.note like '%<sup>%'
    # c.note like '%<sub>%'
    #

    db.sql('''
	   select a._Genotype_key, aa.accID,
		       to_char(a.creation_date, 'MM/dd/yyyy') as cdate,
		       to_char(a.modification_date, 'MM/dd/yyyy') as mdate,
		       u1.login as clogin, u2.login as mlogin
	   into temporary table genotypes
	   from GXD_Genotype a, ACC_Accession aa, MGI_User u1, MGI_User u2
	   where a._Genotype_key = aa._Object_key
	   and aa._MGIType_key = 12
	   and aa._LogicalDB_key = 1
	   and aa.preferred = 1
	   and a._CreatedBy_key = u1._User_key
	   and a._ModifiedBy_key = u2._User_key
	   and exists (select * from VOC_Annot v, VOC_Evidence e, MGI_Note_VocEvidence_View n
	   where a._Genotype_key = v._Object_key
	   and v._AnnotType_key = 1002
	   and v._Annot_key = e._Annot_key
	   and e._AnnotEvidence_key = n._Object_key
	   and n._NoteType_key = 1008
	   and (lower(n.note) like '%<sup>%' or lower(n.note) like '%<sub>%'
	   ))
	   ''', None)

    db.sql('create index genotype_idx1 on genotypes(_Genotype_key)', None)

    #
    # concatenate notes
    #
    results = db.sql('''
	        select a._Genotype_key, n.note
	        from genotypes a, VOC_Annot v, VOC_Evidence e, MGI_Note_VocEvidence_View n
	        where a._Genotype_key = v._Object_key
	        and v._AnnotType_key = 1002
	        and v._Annot_key = e._Annot_key
	        and e._AnnotEvidence_key = n._Object_key
	        and n._NoteType_key = 1008
                order by n._Note_key, n.sequenceNum
	          ''', 'auto')

    notes = {}
    for r in results:
        key = r['_Genotype_key']
        value = string.lower(r['note'])
    
        if notes.has_key(key):
	    notes[key] = notes[key] + value
        else:
	    notes[key] = value

    #
    # for each allele w/ notes:
    #	if note exists or has an error:
    #	   print the allele, note snippet
    #

    results = db.sql('select * from genotypes order by accID', 'auto')

    for r in results:
    
        snippets = []
        note = notes[r['_Genotype_key']]

	# if number of <sup> != number of </sup>, then add to snippet
        findA = string.count(note, '<sup>')
        findB = string.count(note, '</sup>')
        if findA != findB:
            findA = string.find(note, '<sup>')
            findB = string.find(note, '</sup>')
            snippets.append(note)

	# if number of <sub> != number of </sub>, then add to snippet
        findA = string.count(note, '<sub>')
        findB = string.count(note, '</sub>')
        if findA != findB:
            snippets.append(note)

	# if any snippets exist, then print
        if len(snippets) > 0:
            fp.write('MP notes' + TAB)
            fp.write(r['accID'] + TAB)
            fp.write(r['clogin'] + TAB)
            fp.write(r['cdate'] + TAB)
            fp.write(r['mlogin'] + TAB)
            fp.write(r['mdate'] + CRT)
    
def markerNotes():

    #
    # Marker Notes
    #

    fp.write('\n\n#Note type\n')
    fp.write('#Marker symbol\n')
    fp.write('#Marker accession ID\n')
    fp.write('#Created by date\n')
    fp.write('#Modified by date\n\n')

    db.sql('''
          select a._Marker_key, a.symbol, aa.accID,
		 to_char(a.creation_date, 'MM/dd/yyyy') as cdate,
		 to_char(a.modification_date, 'MM/dd/yyyy') as mdate
          into markers
          from MRK_Marker a, ACC_Accession aa
          where a._Marker_key = aa._Object_key
          and aa._MGIType_key = 2
	  and aa._LogicalDB_key = 1
	  and aa.preferred = 1
          and exists (select * from MRK_Notes n
          where a._Marker_key = n._Marker_key
          and (lower(n.note) like '%<sup>%' or lower(n.note) like '%<sub>%'))
          ''', None)

    results = db.sql('''
	        select a._Marker_key, n.note
	        from markers a, MRK_Notes n
	        where a._Marker_key = n._Marker_key
                order by a._Marker_key, n.sequenceNum
	          ''', 'auto')

    notes = {}
    for r in results:
        key = r['_Marker_key']
        value = string.lower(r['note'])
    
        if notes.has_key(key):
            notes[key] = notes[key] + value
        else:
            notes[key] = value

    #
    # for each marker w/ notes:
    #	if note exists or has an error:
    #	   print the allele, note snippet
    #

    results = db.sql('select * from markers order by symbol', 'auto')

    for r in results:

        snippets = []
        note = notes[r['_Marker_key']]

        # if number of <sup> != number of </sup>, then add to snippet
        findA = string.count(note, '<sup>')
        findB = string.count(note, '</sup>')
        if findA != findB:
            findA = string.find(note, '<sup>')
            findB = string.find(note, '</sup>')
            snippets.append(note)

        # if number of <sub> != number of </sub>, then add to snippet
        findA = string.count(note, '<sub>')
        findB = string.count(note, '</sub>')
        if findA != findB:
            snippets.append(note)

        # if any snippets exist, then print
        if len(snippets) > 0:
            fp.write('Marker Detail Clip' + TAB)
            fp.write(r['symbol'] + TAB)
            fp.write(r['accID'] + TAB)
            fp.write(r['cdate'] + TAB)
            fp.write(r['mdate'] + CRT)

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Allele Notes with HTML errors', os.environ['QCOUTPUTDIR'], printHeading = None)
markerNotes()
mpNotes()
alleleNotes()
reportlib.finish_nonps(fp)	# non-postscript file

