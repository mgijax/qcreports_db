
'''
#
# All Alleles
#
'''
 
import sys
import os
import db
import reportlib

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

def go (form) :

    sys.stdout.write('allele symbol' + TAB)
    sys.stdout.write('allele id' + TAB)
    sys.stdout.write('nomen note' + TAB)
    sys.stdout.write('status' + CRT)

    results = db.sql('''
    WITH alleles AS (
    select a._Allele_key, a.symbol, aa.accid, t.term
    from ALL_Allele a, ACC_Accession aa, VOC_Term t
    where a._Allele_key = aa._Object_key
    and aa._LogicalDB_key = 1
    and aa._MGIType_key = 11
    and a._Allele_Status_key = t._term_key
    and a.iswildtype = 0
    )
    select a.*, n.note
    from alleles a, MGI_Note n
    where a._Allele_key = n._Object_key
    and n._MGIType_key = 11
    and n._NoteType_key = 1022
    union
    select a.*, null
    from alleles a
    and not exists (select 1 from  MGI_Note n
        where a._Allele_key = n._Object_key
        and n._MGIType_key = 11
        and n._NoteType_key = 1022
    )
    order by symbol
    ''', 'auto')

    for r in results:
            sys.stdout.write(r['symbol'] + TAB)
            sys.stdout.write(r[accid'] + TAB)

            if r['note'] != None:
                    note = r['note'].replace('\n', ' ').replace('\t', ' ')
                    sys.stdout.write(note)
            sys.stdout.write(TAB)

            sys.stdout.write(r['term'] + CRT)

    sys.stdout.flush()

