
'''
#
# Another report of variants that me need review.
#
# Report variants where: 
#       the allele has a nomenclature note any of the following:
#               mut=,  mut =, mutation=, mutation =,
#               mut:,  mut :, mutation:, mutation :
#       has no curated variant data 
#
# Columns: 
#       Allele Symbol
#       Allele ID 
#       Note
#
'''
 
import sys
import os
import db
import reportlib
import re

CRT = reportlib.CRT
TAB = reportlib.TAB

REGEX = re.compile(r'', re.I)

def go (form) :
    # This just gets the allele MGI IDs and symbols 
    results = db.sql('''
    select a.symbol, aa.accid, n.note
    from all_allele  a, mgi_note n, acc_accession aa
    where n._notetype_key = 1022
    and n.note similar to '%[Mm][Uu][Tt]([Aa][Tt][Ii][Oo][Nn])? ?[:=]%'
    and n._object_key = a._allele_key
    and a._allele_key not in (select distinct _allele_key from all_variant where isreviewed = 1)
    and a._allele_key = aa._object_key
    and aa._mgitype_key = 11
    and aa._logicaldb_key = 1
    and aa.preferred = 1
    order by a.symbol
    ''', 'auto')

    sys.stdout.write('symbol' + TAB)
    sys.stdout.write('accid' + TAB)
    sys.stdout.write('note' + CRT)

    for r in results:
            sys.stdout.write(r['symbol'] + TAB)
            sys.stdout.write(r['accid'] + TAB)
            # Have to be careful about odd characters in the notes.
            # For this report, just ignore them.
            # Also, since we're generating tab-delimited output, replace all TABs with spaces.
            note = r['note'].encode('ascii', 'ignore').decode().replace(TAB, " ").replace(CRT, " ")
            sys.stdout.write(note)
            sys.stdout.write(CRT)

    sys.stdout.flush()

