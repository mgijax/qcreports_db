
'''
#
# Strain Check by Strain Repository
#
# Lookup IMSR Strain Info by Repository IDs 
#
# Enter a space delimited set of Repository IDs 
#
# Examples: MMRRC:037343 RBRC00257 000486
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
    arg = form['arg'].value
    # expects "MMRRC:037343 RBRC00257 000486"
    value = list(arg.split(' '))

    # example: 'MMRRC:037343','RBRC00257','000486'
    value1 = "'" + "','".join(value) + "'"

    db.sql('''
    select a1.accid as inputID, 
    a1._Object_key as _strain_key, 
    a1._logicaldb_key, 
    a2.accid as mgiID, 
    s.strain, 
    CASE WHEN s.private = 0 THEN 'No' ELSE 'Yes' END AS private 
    into temporary table strains 
    from ACC_Accession a1, ACC_Accession a2, PRB_Strain s 
    where a1.accid in (%s) 
    and a1._MGIType_key = 10 
    and a1._Object_key = a2._Object_key 
    and a2._MGIType_key = 10 
    and a2._LogicalDB_key = 1 
    and a2.prefixPart = 'MGI:' 
    and a2.preferred = 1 
    and a1._Object_key = s._Strain_key
    ''' % (value1), None)
    db.sql('create index idx1 on strains(_strain_key)', None)

    db.sql('''
    select s.*, a.accid as otherID 
    into temporary table strainsOtherIDs 
    from strains s left outer join acc_accession a on (
            s._strain_key = a._object_key 
            and a._mgitype_key = 10 
            and a._logicaldb_key not in (1) 
            and a.preferred = 1 
            and s.inputID != a.accid)
    ''', None)
    db.sql('create index idx2 on strainsOtherIDs(_strain_key)', None)

    results = db.sql('''
    select s.inputID, 
    s.mgiID, 
    s.strain, 
    s.private, 
    string_agg(distinct s.otherID, 
    ', ') as otherIDS, 
    string_agg(distinct a.symbol, ', ') as alleleSymbols 
    from strainsOtherIDs s left outer join all_allele a on (s._strain_key = a._strain_key and a._allele_status_key in (847114, 3983021)) 
    group by 1,2,3,4 
    order by s.inputID
    ''', 'auto')

    sys.stdout.write('inputID' + TAB)
    sys.stdout.write('mgiID' + TAB)
    sys.stdout.write('strain' + TAB)
    sys.stdout.write('private' + TAB)
    sys.stdout.write('otherIDS' + TAB)
    sys.stdout.write('alleleSymbols' + CRT)

    for r in results:
            sys.stdout.write(r['inputID'] + TAB)
            sys.stdout.write(r['mgiID'] + TAB)
            sys.stdout.write(r['strain'] + TAB)
            sys.stdout.write(r['private'] + TAB)

            if r['otherIDS'] == None:
                    sys.stdout.write(TAB)
            else:
                    sys.stdout.write(r['otherIDS'] + TAB)

            if r['alleleSymbols'] == None:
                    sys.stdout.write(CRT)
            else:
                    sys.stdout.write(r['alleleSymbols'] + CRT)

    sys.stdout.flush()

