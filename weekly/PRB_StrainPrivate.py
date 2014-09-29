#!/usr/local/bin/python

'''
#
# PRB_StrainPrivate.py
#
# Report:
#
#	Determine private Strains that contain associations to public data
#
# Usage:
#       PRB_StrainPrivate.py
#
# Notes:
#
# History:
#
# lec	06/14/2012
#	- TR11093/part of the "delete private data" issue
#
#
'''
 
import sys
import os
import reportlib

try:
    if os.environ['DB_TYPE'] == 'postgres':
        import pg_db
        db = pg_db
        db.setTrace()
        db.setAutoTranslateBE()
    else:
        import db
except:
    import db


TAB = reportlib.TAB
CRT = reportlib.CRT

db.useOneConnection(1)
fp = reportlib.init(sys.argv[0], 'Private Strains that contain associations to public data', outputdir = os.environ['QCOUTPUTDIR'])

db.sql('''
	select _Strain_key, substring(strain,1,50) as strain
	into #strains
	from PRB_Strain
	where private = 1
	''', None)

db.sql('create index idx1 on #strains(_Strain_key)', None)

#
# PRB_Source
#

fp.write('\n**PRB_Source\n\n')
results = db.sql('''
	select s.strain, pp.name
	from #strains s, PRB_Source p, PRB_Probe pp
	where s._Strain_key = p._Strain_key
	and p._Source_key = pp._Source_key
	''', 'auto')
for r in results:
	fp.write(r['strain'] + TAB)
	fp.write(r['name'] + CRT)

results = db.sql('''
	select s.strain, pp.antigenName
	from #strains s, PRB_Source p, GXD_Antigen pp
	where s._Strain_key = p._Strain_key
	and p._Source_key = pp._Source_key
	''', 'auto')
for r in results:
	fp.write(r['strain'] + TAB)
	fp.write(r['antigenName'] + CRT)

db.sql('''
	select s.strain, s._Strain_key, p._Source_key
	into #psource
	from #strains s, PRB_Source p
	where s._Strain_key = p._Strain_key
	''', 'auto')
db.sql('create index idx2 on #psource(_Source_key)', None)
db.sql('create index idx3 on #psource(_Strain_key)', None)
results = db.sql('''
	select s.strain, a.accID
	from #strains s, #psource p, SEQ_Source_Assoc pp, ACC_Accession a
	where s._Strain_key = p._Strain_key
	and p._Source_key = pp._Source_key
	and pp._Sequence_key = a._Object_key
	and a._MGIType_key = 19
	''', 'auto')
for r in results:
	fp.write(r['strain'] + TAB)
	fp.write(r['accID'] + CRT)

#
# CRS_Cross
#

fp.write('\n**CRS_Cross\n\n')
results = db.sql('''
	select a.accid, s.strain, r.jnumID, e.exptType, e.chromosome
	from #strains s, CRS_Cross p, MLD_Matrix m, MLD_Expts e, BIB_Citation_Cache r, ACC_Accession a
	where (s._Strain_key = p._femaleStrain_key
	or s._Strain_key = p._maleStrain_key
	or s._Strain_key = p._StrainHO_key
	or s._Strain_key = p._StrainHT_key
	)
	and p._Cross_key = m._Cross_key
	and m._Expt_key = e._Expt_key
	and e._Refs_key = r._Refs_key
	and e._Expt_key = a._Object_key
	and a._MGIType_key = 4
	and a._LogicalDB_key = 1
	and a.preferred = 1
	''', 'auto')
for r in results:
	fp.write(r['accid'] + TAB)
	fp.write(r['strain'] + TAB)
	fp.write(r['jnumID'] + TAB)
	fp.write(r['exptType'] + TAB)
	fp.write(r['chromosome'] + CRT)

#
# MLD_FISH
#

fp.write('\n**MLD_FISH\n\n')
results = db.sql('''
	select a.accid, s.strain, r.jnumID, e.exptType, e.chromosome
	from #strains s, MLD_FISH p, MLD_Expts e, BIB_Citation_Cache r, ACC_Accession a
	where s._Strain_key = p._Strain_key
	and p._Expt_key = e._Expt_key
	and e._Refs_key = r._Refs_key
	and e._Expt_key = a._Object_key
	and a._MGIType_key = 4
	and a._LogicalDB_key = 1
	and a.preferred = 1
	''', 'auto')
for r in results:
	fp.write(r['accid'] + TAB)
	fp.write(r['strain'] + TAB)
	fp.write(r['jnumID'] + TAB)
	fp.write(r['exptType'] + TAB)
	fp.write(r['chromosome'] + CRT)

#
# MLD_InSitu
#

fp.write('\n**MLD_InSitu\n\n')
results = db.sql('''
        select a.accid, s.strain, r.jnumID, e.exptType, e.chromosome
        from #strains s, MLD_InSitu p, MLD_Expts e, BIB_Citation_Cache r, ACC_Accession a
        where s._Strain_key = p._Strain_key
        and p._Expt_key = e._Expt_key
        and e._Refs_key = r._Refs_key
        and e._Expt_key = a._Object_key
        and a._MGIType_key = 4
        and a._LogicalDB_key = 1
        and a.preferred = 1
        ''', 'auto')
for r in results:
        fp.write(r['accid'] + TAB)
        fp.write(r['strain'] + TAB)
        fp.write(r['jnumID'] + TAB)
        fp.write(r['exptType'] + TAB)
        fp.write(r['chromosome'] + CRT)


#
# ALL_Allele
#
fp.write('\n**ALL_Allele\n\n')
results = db.sql('''
	select a.accid, s.strain, p.symbol
	from #strains s, ALL_Allele p, ACC_Accession a
	where s._Strain_key = p._Strain_key
	and p._Allele_key = a._Object_key
	and a._MGIType_key = 11
	and a._LogicalDB_key = 1
	and a.preferred = 1
	''', 'auto')
for r in results:
	fp.write(r['accid'] + TAB)
	fp.write(r['strain'] + TAB)
	fp.write(r['symbol'] + CRT)

#
# ALL_CellLine
#
fp.write('\n**ALL_CellLine\n\n')
results = db.sql('''
	select s.strain, p.cellline
	from #strains s, ALL_CellLine p
	where s._Strain_key = p._Strain_key
	''', 'auto')
for r in results:
	fp.write(r['strain'] + TAB)
	fp.write(r['cellline'] + CRT)

#
# GXD_Genotype
#
fp.write('\n**GXD_Genotype\n\n')
results = db.sql('''
	select a.accid, s.strain
	from #strains s, GXD_Genotype p, ACC_Accession a
	where s._Strain_key = p._Strain_key
	and p._Genotype_key = a._Object_key
	and a._MGIType_key = 12
	and a._LogicalDB_key = 1
	and a.preferred = 1
	''', 'auto')
for r in results:
	fp.write(r['strain'] + CRT)

#
# RI_RISet
#
fp.write('\n**RI_RISet\n\n')
results = db.sql('''
	select s.strain, p.designation
	from #strains s, RI_RISet p
	where s._Strain_key = p._Strain_key_1
	or s._Strain_key = p._Strain_key_2
	''', 'auto')
for r in results:
	fp.write(r['strain'] + TAB)
	fp.write(r['designation'] + CRT)

#
# MGI_Set
#
fp.write('\n**MGI_Set\n\n')
results = db.sql('''
	select s.strain, t.name
	from #strains s, MGI_SetMember sm, MGI_Set t
	where s._Strain_key = sm._Object_key
	and sm._Set_key = t._Set_key
	and t._MGIType_key = 10
	''', 'auto')
for r in results:
	fp.write(r['strain'] + TAB)
	fp.write(r['name'] + CRT)

#
# MGI_Translation
#
fp.write('\n**MGI_Translation\n\n')
results = db.sql('''
	select s.strain, t.badName
	from #strains s, MGI_Translation t, MGI_TranslationType tt
	where s._Strain_key = t._Object_key
	and t._TranslationType_key = tt._TranslationType_key
	and tt._MGIType_key = 10
	''', 'auto')
for r in results:
	fp.write(r['strain'] + TAB)
	fp.write(r['badName'] + CRT)

reportlib.finish_nonps(fp)
db.useOneConnection(0)

