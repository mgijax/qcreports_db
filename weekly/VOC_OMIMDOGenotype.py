#!/usr/local/bin/python

'''
#
# VOC_OMIMDOGenotype.py
#
# Report:
#
#       OMIM-to-Genotype Annotations that do not map to DO
#
# Usage:
# 	VOC_OMIMDOGenotype.py
#
# Notes:
#
# History:
#
# 11/17/2016	lec
#       - TR12427/Disease Ontology (DO)
#
'''

import sys
import os
import string
import reportlib
import db

db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

TAB = reportlib.TAB
CRT = reportlib.CRT

fp = reportlib.init(sys.argv[0], 'omim-to-genotype : do not map to DO ids', outputdir = os.environ['QCOUTPUTDIR'])

db.sql('''
	select distinct a._Object_key, a.accID as omimID, t._Term_key, substring(t.term,1,30) as omimTerm
	INTO TEMP TABLE omimlookup
	from VOC_Annot v, ACC_Accession a, VOC_Term t
	where v._AnnotType_key = 1005
	and v._Term_key = a._Object_key
	and a._MGIType_key = 13
	and a.preferred = 1
	and a._Object_key = t._Term_key
	''', None)

db.sql('create index omimlookup_idx1 on omimlookup(_Object_key)', None)
db.sql('create index omimlookup_idx2 on omimlookup(omimID)', None)

db.sql('''
	select distinct a._Object_key, a.accID as doID, substring(t.term,1,30) as doTerm
	INTO TEMP TABLE dolookup
	from ACC_Accession a, VOC_Term t
	where a._MGIType_key = 13
	and a._LogicalDB_key = 191
	and a.preferred = 1
	and a._Object_key = t._Term_key
	''', None)

db.sql('create index dolookup_idx1 on dolookup(_Object_key)', None)
db.sql('create index dolookup_idx2 on dolookup(doID)', None)

db.sql('''
	select distinct a._Object_key, a.accID as omimdoID, a3.doID, a1.omimTerm, a3.doTerm, a1._Term_key
	INTO TEMP TABLE omimdolookup
	from ACC_Accession a, omimlookup a1, dolookup a3
	where a1.omimID = a.accID
	and a._MGIType_key = 13
	and a._LogicalDB_key = 15
	and a._Object_key = a3._Object_key
	''', None)
db.sql('create index omimdolookup_idx1 on omimdolookup(_Term_key)', None)

db.sql('''
	select distinct a1.*
	INTO TEMP TABLE exclude_omimdolookup
	from omimlookup a1
	where not exists (select 1 from ACC_Accession a, dolookup a3
        	where a1.omimID = a.accID
		and a._MGIType_key = 13
		and a._LogicalDB_key = 15
		and a._Object_key = a3._Object_key
		)
	''', None)
db.sql('create index exclude_omimdolookup_idx1 on exclude_omimdolookup(_Term_key)', None)

db.sql('''
	select distinct a._Object_key, a.accID as genotypeid
	INTO TEMP TABLE genotype
	from VOC_Annot v, ACC_Accession a
	where v._AnnotType_key = 1005
	and v._Object_key = a._Object_key
	and a._MGIType_key = 12
	and a._LogicalDB_key = 1
	and a.preferred = 1
	''', None)
db.sql('create index genotype_idx1 on genotype(_Object_key)', None)

db.sql('''
	select distinct a._Object_key, a.accID as refID
	INTO TEMP TABLE reference 
	from VOC_Annot v, VOC_Evidence e, ACC_Accession a
	where v._AnnotType_key = 1005
	and v._Annot_key = e._Annot_key
	and e._Refs_key = a._Object_key
	and a._MGIType_key = 1
	and a._LogicalDB_key = 1
	and a.prefixPart = 'J:'  
	''', None)
db.sql('create index reference_idx1 on reference(_Object_key)', None)

results = db.sql('''
	select distinct a2.omimID, 
       		a2.omimTerm,
       		a4.genotypeid,
       		a5.refID
	from VOC_Annot v, VOC_Evidence e,
		exclude_omimdolookup a2, genotype a4, reference a5
	where v._AnnotType_key = 1005
	and v._Term_key = a2._Term_key
	and v._Object_key = a4._Object_key
	and v._Annot_key = e._Annot_key
	and e._Refs_key = a5._Object_key
	order by omimID, genotypeid
	''', 'auto')

for r in results:
	fp.write(r['omimID'] + TAB)
	fp.write(r['omimTerm'] + TAB)
	fp.write(r['genotypeid'] + TAB)
	fp.write(r['refID'] + CRT)

reportlib.finish_nonps(fp)

