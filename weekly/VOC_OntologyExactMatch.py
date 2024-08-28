'''
#
# VOC_OntologyExactMatch.py
#
# Report: Terms with more than 1 exact match in the other ontology
#
# MP term to HP term
# MP term to HP term synonym
# HP term to MP term synonym
# MP term synonym to HP term synonym
#
# Columns in 2 reports
# A: MP ID
# B: MP term
# C: MP synonym
# D: HP ID
# E: HP term
# F: HP synonym
# G: Match type
# 
# 1 MP more than 1 HP
# 1 HP more than 1 MP
# 
# History:
#
# 08/27/2024
#       - wts2-1377/fl2-960/QC reports for MP-HP match tool
#
'''

import sys
import os
import reportlib
import db

db.setTrace()

TAB = reportlib.TAB
CRT = reportlib.CRT

fp = reportlib.init(sys.argv[0], 'Phenotype Terms with more than 1 exact match', outputdir = os.environ['QCOUTPUTDIR'])
fp.write('MP ID' + TAB)
fp.write('MP term' + TAB)
fp.write('MP synonym' + TAB)
fp.write('HP ID' + TAB)
fp.write('HP term' + TAB)
fp.write('HP synonym' + TAB)
fp.write('Match type' + CRT)

#
# one SQL per case statement:
# MP term to HP term
# MP term to HP term synonym
# HP term to MP term synonym
# MP term synonym to HP term synonym
#
db.sql('''
(
select distinct mp._term_key as mptermkey, mp.term as mpterm, hp._term_key as hptermkey, hp.term as hpterm, 
    null as mpsynonym, null as hpsynonym, 'MP term to HP term' as matchType
into temp exactMatches
from voc_term mp, voc_term hp
where mp._vocab_key = 5
and lower(mp.term) = lower(hp.term)
and hp._vocab_key = 106

union
select distinct mp._term_key as mptermkey, mp.term as mpterm, hp._term_key as hptermkey, hp.term as hpterm, 
    null as mpsynonym, hs.synonym as hpsynonym, 'MP term to HP synonym' as matchType
from voc_term mp, voc_term hp, mgi_synonym hs
where mp._vocab_key = 5
and lower(mp.term) = lower(hs.synonym)
and hs._synonymtype_key = 1017
and hs._mgitype_key = 13
and hs._object_key = hp._term_key
and hp._vocab_key = 106

union
select distinct mp._term_key as mptermkey, mp.term as mpterm, hp._term_key as hptermkey, hp.term as hpterm, 
    ms.synonym as mpsynonym, null as hpsynonym, 'HP term to MP synonym' as matchType
from voc_term mp, voc_term hp, mgi_synonym ms
where mp._vocab_key = 5
and mp._term_key = ms._object_key
and ms._mgitype_key = 13
and lower(ms.synonym) = lower(hp.term)
and ms._synonymtype_key = 1017
and ms._mgitype_key = 13
and hp._vocab_key = 106

union
select distinct mp._term_key as mptermkey, mp.term as mpterm, hp._term_key as hptermkey, hp.term as hpterm, 
    ms.synonym as mpsynonym, hs.synonym as hpsynonym, 'MP synonym to HP synonym' as matchType
from voc_term mp, voc_term hp, mgi_synonym ms, mgi_synonym hs
where mp._vocab_key = 5
and mp._term_key = ms._object_key
and ms._mgitype_key = 13
and lower(ms.synonym) = lower(hs.synonym)
and ms._synonymtype_key = 1017
and hs._synonymtype_key = 1017
and hs._mgitype_key = 13
and hs._object_key = hp._term_key
and hp._vocab_key = 106
)
order by mptermkey
''', None)

db.sql('''create index idx3a on exactMatches(mptermkey)''', None)
db.sql('''create index idx3b on exactMatches(hptermkey)''', None)

#
# MP -> 1 HP
#
results = db.sql('''
WITH resultCount AS (
select mptermkey, count(distinct hptermkey) from exactMatches group by 1 having count(distinct hptermkey) > 1
)
select em.*, mpacc.accid as mpaccid, hpacc.accid as hpaccid
from resultCount c, exactMatches em, acc_accession mpacc, acc_accession hpacc
where c.mptermkey = em.mptermkey
and em.mptermkey = mpacc._object_key
and mpacc._mgitype_key = 13
and mpacc._logicaldb_key = 34
and mpacc.prefixpart = 'MP:'
and mpacc.preferred = 1
and em.hptermkey = hpacc._object_key
and hpacc._mgitype_key = 13
and hpacc._logicaldb_key = 180
and hpacc.prefixpart = 'HP:'
and hpacc.preferred = 1
order by mpaccid, hpaccid
''', 'auto')

fp.write('\nMP -> 1 HP\n')
for r in results:
    fp.write(r['mpaccid'] + TAB)
    fp.write(r['mpterm'] + TAB)

    if r['mpsynonym'] != None:
        fp.write(r['mpsynonym'])
    fp.write(TAB)

    fp.write(r['hpaccid'] + TAB)
    fp.write(r['hpterm'] + TAB)

    if r['hpsynonym'] != None:
        fp.write(r['hpsynonym'])
    fp.write(TAB)

    fp.write(r['matchType'] + CRT)
    
fp.write('\n(%d rows affected)\n\n' % (len(results)))

#
# HP -> 1 MP
#
results = db.sql('''
WITH resultCount AS (
select hptermkey, count(distinct mptermkey) from exactMatches group by 1 having count(distinct mptermkey) > 1
)
select em.*, mpacc.accid as mpaccid, hpacc.accid as hpaccid
from resultCount c, exactMatches em, acc_accession mpacc, acc_accession hpacc
where c.hptermkey = em.hptermkey
and em.mptermkey = mpacc._object_key
and mpacc._mgitype_key = 13
and mpacc._logicaldb_key = 34
and mpacc.prefixpart = 'MP:'
and mpacc.preferred = 1
and em.hptermkey = hpacc._object_key
and hpacc._mgitype_key = 13
and hpacc._logicaldb_key = 180
and hpacc.prefixpart = 'HP:'
and hpacc.preferred = 1
order by hpaccid, mpaccid
''', 'auto')

fp.write('\nHP -> 1 MP\n')
for r in results:
    fp.write(r['mpaccid'] + TAB)
    fp.write(r['mpterm'] + TAB)

    if r['mpsynonym'] != None:
        fp.write(r['mpsynonym'])
    fp.write(TAB)

    fp.write(r['hpaccid'] + TAB)
    fp.write(r['hpterm'] + TAB)

    if r['hpsynonym'] != None:
        fp.write(r['hpsynonym'])
    fp.write(TAB)

    fp.write(r['matchType'] + CRT)

fp.write('\n(%d rows affected)\n\n' % (len(results)))

reportlib.finish_nonps(fp)

