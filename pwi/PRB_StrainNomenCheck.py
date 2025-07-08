
'''
#
# Strain Check by Strain Nomenclature
#
# Lookup IMSR Strain Info by Strain Nomenclature 
#
# Enter a space delimited set of strain names 
#
# Examples: MRL/MpJ 129.B6-GIX<->/Rbrc
#
'''
 
import sys
import os
import db
import reportlib

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

def go (form) :
    # expects "MRL/MpJ 129.B6-GIX<->/Rbrc"
    arg = form['arg'].value
    value = list(arg.split(' '))

    # example: 'MRL/MpJ','129.B6-GIX<->/Rbrc'
    value1 = "'" + "','".join(value) + "'"

    db.sql('''
    select 
    s.strain, 
    s._strain_key, 
    ms.synonym 
    into temporary table strainSynHist 
    from mgi_synonym ms, prb_strain s 
    where ms._synonymtype_key in (1000, 1001) 
    and s.strain in (%s) 
    and s._strain_key = ms._object_key 
    order by s.strain
    ''' % (value1), None)
    db.sql('create index idx1 on strainSynHist(_strain_key)', None)

    db.sql('''
    select 
    s.strain, 
    s._strain_key, 
    t.term as strainType,
    a1.accid as mgiID, 
    CASE WHEN s.private = 0 THEN 'No' ELSE 'Yes' END AS private,
    array_to_string(array_agg(distinct vt.term),',') as strainAttributes
    into temporary table strains 
    from prb_strain s, acc_accession a1, voc_term t, voc_annot va, voc_term vt
    where strain in (%s) 
    and s._straintype_key = t._term_key
    and s._strain_key = a1._object_key 
    and a1._MGIType_key = 10 
    and a1._LogicalDB_key = 1 
    and a1.prefixPart = 'MGI:' 
    and a1.preferred = 1
    and s._strain_key = va._object_key
    and va._annottype_key = 1009
    and va._term_key = vt._term_key
    group by s.strain, s._strain_key, t.term, a1.accid, s.private
    ''' % (value1), None)
    db.sql('create index idx2 on strains(_strain_key)', None)

    db.sql('''
    select s.*, a.accid as repoID 
    into temporary table repoIDs 
    from strains s 
            left outer join acc_accession a on (s._strain_key = a._object_key 
                    and a._mgitype_key = 10 
                    and a._logicaldb_key not in (1) 
                    and a.preferred = 1)
    ''', None)
    db.sql('create index idx3 on repoIDs(_strain_key)', None)

    db.sql('''
    select s._strain_key, string_agg(distinct aa.accid, ', ') as alleleAssocs
    into temporary table alleleAssociations
    from strains s, prb_strain_marker m, all_allele a, acc_accession aa
    where s._strain_key = m._strain_key 
    and m._allele_key = a._allele_key 
    and a._allele_status_key in (847114, 3983021)
    and a._allele_key = aa._object_key
    and aa._mgitype_key = 11
    and aa.preferred = 1
    group by s._strain_key
    ''', None)
    db.sql('create index idx4 on alleleAssociations(_strain_key)', None)

    db.sql('''
    select s.strain, 
    s._strain_key, 
    s.strainType,
    s.mgiID, 
    s.private, 
    s.strainAttributes,
    aa.alleleAssocs,
    string_agg(distinct s.repoID, ', ') as repoIDS, 
    string_agg(distinct a.symbol, ', ') as alleleSymbols
    into temporary table final 
    from repoIDs s 
            left outer join all_allele a on (s._strain_key = a._strain_key and a._allele_status_key in (847114, 3983021))
            left outer join alleleAssociations aa on (s._strain_key = aa._strain_key)
    group by 1, 2, 3, 4, 5, 6, 7
    order by s.strain
    ''', None)
    db.sql('create index idx5 on final(_strain_key)', None)

    results = db.sql('''
    select f.strain, f.strainType, f.strainAttributes,
    CASE WHEN sh.synonym is null THEN 'No' ELSE 'Yes' END AS synonymOrHistory, 
    f.mgiID, 
    f.private, 
    f.repoids, 
    f.alleleSymbols,
    f.alleleAssocs
    from final f left outer join strainSynHist sh on (f._strain_key = sh._strain_key) 
    order by f.strain
    ''', 'auto')

    sys.stdout.write('strain' + TAB)
    sys.stdout.write('strain type' + TAB)
    sys.stdout.write('strain attributes' + TAB)
    sys.stdout.write('synonymOrHistory' + TAB)
    sys.stdout.write('mgiID' + TAB)
    sys.stdout.write('private' + TAB)
    sys.stdout.write('repoids' + TAB)
    sys.stdout.write('alleles (strain of origin)' + TAB)
    sys.stdout.write('alleles (associations)' + CRT)

    for r in results:
            sys.stdout.write(r['strain'] + TAB)
            sys.stdout.write(r['strainType'] + TAB)
            sys.stdout.write(r['strainAttributes'] + TAB)
            sys.stdout.write(r['synonymOrHistory'] + TAB)
            sys.stdout.write(r['mgiID'] + TAB)
            sys.stdout.write(r['private'] + TAB)
            sys.stdout.write(r['repoids'] + TAB)

            if r['alleleSymbols'] == None:
                    sys.stdout.write(TAB)
            else:
                    sys.stdout.write(r['alleleSymbols'] + TAB)

            if r['alleleAssocs'] == None:
                    sys.stdout.write(CRT)
            else:
                    sys.stdout.write(r['alleleAssocs'] + CRT)

    sys.stdout.flush()

