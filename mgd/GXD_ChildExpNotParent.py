#!/usr/local/bin/python

'''
#
# TR 8618
#
# Report:
#
# List anatomical structures used in assays that have been annotated as having
# no expression, but the children used in the same assay have been annotated
# as having expression.
#
# Columns to display:
#    1) J-Number of the assay
#    2) MGI ID of the assay
#    3) Stage of the structures in question
#    4) Parent structure (with absent annotation)
#    5) Child structure(s) (separated by a '|' if more than one)
# 
# Order by MGI ID, stage and parent structure.
# 
# Originally requested as a custom SQL (TR 8073).
#
# Usage:
#       GXD_ChildExpNotParent.py
#
# Notes:
#
# History:
#
# lec	01/21/2016
#	- TR12223/gxd anatomy II
#
# lec   03/11/2014
#       - TR11597/sort by mgiID desc
#
# lec	05/01/2008
#	- TR 8775; on select GXD assay types
#
# dbm	11/28/2007
#	- new
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

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'Assays in which a parent structure is annotated as having no expression while its children have expression.', outputdir = os.environ['QCOUTPUTDIR'])

fp.write('Excluded J-Numbers: J:80501,J:80502,J:91257,J:93300,J:101679,J:122989,J:153498,J:162220,J:171409')
fp.write(2*CRT)
fp.write(string.ljust('J-Number', 12))
fp.write(SPACE)
fp.write(string.ljust('MGI ID', 12))
fp.write(SPACE)
fp.write(string.ljust('Stage', 5))
fp.write(SPACE)
fp.write(string.ljust('Parent Structure', 50))
fp.write(SPACE)
fp.write(string.ljust('Child Structure', 50))
fp.write(CRT)
fp.write(12*'-')
fp.write(SPACE)
fp.write(12*'-')
fp.write(SPACE)
fp.write(5*'-')
fp.write(SPACE)
fp.write(50*'-')
fp.write(SPACE)
fp.write(50*'-')
fp.write(CRT)

#
# Identify all cases where the parent structure has no expression, 
# but has a child that does have expression (strength > 1).
#

db.sql('''
	SELECT DISTINCT
	       a._Assay_key,
	       r._Specimen_key, 
               s._EMAPA_Term_key as parentKey, 
	       s._Stage_key,
               s2._EMAPA_Term_key as childKey
        INTO TEMPORARY TABLE work 
        FROM GXD_InSituResult r, GXD_InSituResult r2, 
             GXD_ISResultStructure s, GXD_ISResultStructure s2, 
	     GXD_Specimen sp, GXD_Specimen sp2,
             GXD_Assay a,
             DAG_Closure c, VOC_Term_EMAPS emaps_p, VOC_Term_EMAPS emaps_c
        WHERE r._Strength_key = 1 
              and r._Result_key = s._Result_key 
              and r._Specimen_key = sp._Specimen_key 
	      and sp._Assay_key = a._Assay_key 
	      and a._AssayType_key in (1,2,3,4,5,6,8,9) 
              and r2._Strength_key > 1 
              and r2._Result_key = s2._Result_key 
              and r2._Specimen_key = sp2._Specimen_key 
              and sp._Assay_key = sp2._Assay_key 
              and sp._Genotype_key = sp2._Genotype_key 
              and sp.age = sp2.age 
	      and s._Stage_key = s2._Stage_key
              and s._EMAPA_Term_key = emaps_p._EMAPA_Term_key
	      and emaps_p._Term_key = c._AncestorObject_key
	      and c._MGIType_key = 13
	      and c._DescendentObject_key = emaps_c._Term_key
	      and emaps_c._EMAPA_Term_key = s2._EMAPA_Term_key
	      and a._Refs_key not in (81462,81463,92242,94290,102744,124081,154591,154591,163316,172505)
	''', None)

db.sql('create index idx1 on work(_Specimen_key)', None)
db.sql('create index idx2 on work(parentKey)', None)
db.sql('create index idx3 on work(childKey)', None)

results = db.sql('''
	SELECT DISTINCT a.accID as mgiID, j.accID as jnumID, t.stage, 
		substring(d.term,1,50) as pterm, substring(d2.term,1,50) as cterm
        FROM work w, GXD_Expression e, 
             ACC_Accession a, ACC_Accession j, 
             VOC_Term d, VOC_Term d2, GXD_TheilerStage t
        WHERE e._Assay_key = w._Assay_key
	      and e._Specimen_key = w._Specimen_key 
	      and e.isForGXD = 1 
              and e.expressed = 1 
              and e._Assay_key = a._Object_key 
              and a._MGIType_key = 8 
              and e._Refs_key = j._Object_key 
              and j._MGIType_key = 1 
              and j.prefixPart = 'J:' 
              and w.parentKey = d._Term_key 
              and w.childKey = d2._Term_key
	      and e._Stage_key = w._Stage_key
	      and e._Stage_key = t._Stage_key
	      order by mgiID desc, t.stage, pterm
	''', 'auto')
fp.write('\n(%d rows affected)\n\n' % (len(results)))

for r in results:
	fp.write(string.ljust(r['jnumID'], 12))
	fp.write(SPACE)
	fp.write(string.ljust(r['mgiID'], 12))
	fp.write(SPACE)
	fp.write(string.ljust(str(r['stage']), 5))
	fp.write(SPACE)
	fp.write(string.ljust(r['pterm'], 50))
	fp.write(SPACE)
	fp.write(string.ljust(r['cterm'], 50))
	fp.write(CRT)

reportlib.finish_nonps(fp)

