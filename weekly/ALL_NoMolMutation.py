
'''
#
# TR 6703
#
# Report:
#       Produce a report of alleles that have Molecular Notes
#       but no Molecular Mutation.
#
#       MGI ID of Allele
#	Allele Symbol
#	Allele Type
#	Molecular Note
#
# Usage:
#       ALL_NoMolMutation.py
#
# Notes:
#
# History:
#
# lec   10/22/2014
#       - TR11750/postres complient
#
# 08/14/2008	lec
#	- TR9187
#	   only list alleles with status = "approved"
#	   list last modification date in descending order
#
# 04/01/2005	lec
#       - created
#
'''
 
import sys 
import os 
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Alleles that have Molecular Notes but no Molecular Mutation', os.environ['QCOUTPUTDIR'])
fp.write('only list alleles with status = "approved"\n')
fp.write('list last modication date in descending order\n')
fp.write('\n')

db.sql('''
        select a._Allele_key into temporary table alleles 
        from ALL_Allele a, VOC_Term t 
        where a._Allele_Status_key = 847114 
                and a._Allele_Type_key = t._Term_key 
                and t.term != 'QTL' 
                and exists (select 1 from MGI_Note n, MGI_NoteType nt 
                where a._Allele_key = n._Object_key 
                and n._MGIType_key = 11 
                and n._NoteType_key = nt._NoteType_key 
                and nt.noteType = 'Molecular') 
        and not exists (select 1 from ALL_Allele_Mutation m where a._Allele_key = m._Allele_key)
        ''', None)

db.sql('create index idex1 on alleles(_Allele_key)', None)

results = db.sql('''
        select a._Allele_key, n.note 
        from alleles a, MGI_Note n, MGI_NoteType nt
        where a._Allele_key = n._Object_key 
        and n._MGIType_key = 11 
        and n._NoteType_key = nt._NoteType_key 
        and nt.noteType = 'Molecular' 
        order by a._Allele_key
        ''', 'auto')
notes = {}
for r in results:
    key = r['_Allele_key']
    value = r['note']
    if key not in notes:
        notes[key] = []
    notes[key].append(value)

results = db.sql('''
        select a._Allele_key, ac.accID, aa.symbol, t.term as alleleType, 
        to_char( aa.modification_date, 'MM/dd/yyyy') as modDate
        from alleles a, ACC_Accession ac, ALL_Allele aa, VOC_Term t 
        where a._Allele_key = ac._Object_key 
        and ac._MGIType_key = 11 
        and ac._LogicalDB_key = 1 
        and ac.prefixPart = 'MGI:' 
        and ac.preferred = 1 
        and a._Allele_key = aa._Allele_key 
        and aa._Allele_Type_key = t._Term_key 
        order by aa.modification_date desc, ac.numericPart
        ''', 'auto')

for r in results:
        fp.write(r['accID'] + TAB + \
                 r['symbol'] + TAB + \
                 r['alleleType'] + TAB + \
                 r['modDate'] + TAB + \
                 ''.join(notes[r['_Allele_key']]) + CRT)

fp.write(CRT + 'Number of Alleles: ' + str(len(results)) + CRT)

reportlib.finish_nonps(fp)
