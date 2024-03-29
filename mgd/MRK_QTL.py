
'''
#
# Purpose:
#
# TR11373 : QTL Reports
#
# 1: QTL markers that have no mapping and no allele associated (no/no)
#
# 2: QTL markers that have mapping but no allele associated (yes/no)
#
# 3: QTL markers that have no mapping but have allele associated (no/yes)
#
# 4: QTL markers that have assigned reference of J:23000 or J:85000
#
# 5: QTL markers that are in Reserved
#
# History
#
# lec	05/11/2018
#	TR12858/MRK_QTL.py/add J: and counts to MRK_QTL_2.rpt (query2)
#
'''
 
import sys 
import os
import mgi_utils
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

query1 = '''select a1.accID as mgiID, a2.accID as refID, m.symbol, m.name
          from MRK_Marker m, ACC_Accession a1, ACC_Accession a2, refs r
          where m._Marker_Type_key = 6
          and m._Marker_Status_key = 1
          and m._Organism_key = 1
          and m._Marker_key = a1._Object_key
          and a1._MGIType_key = 2
          and a1._Logicaldb_key = 1
          and a1.prefixpart = 'MGI:'
          and a1.preferred = 1
          and m._Marker_key = r._Marker_key
          and r._refs_key = a2._Object_key
          and a2._MGIType_key = 1
          and a2._Logicaldb_key = 1
          and a2.prefixpart = 'J:'
          and a2.preferred = 1
          '''

query2 = '''select distinct a2.accID as refID, a2.numericPart
          from MRK_Marker m, ACC_Accession a2, refs r
          where m._Marker_Type_key = 6
          and m._Marker_Status_key = 1
          and m._Organism_key = 1
          and m._Marker_key = r._Marker_key
          and r._refs_key = a2._Object_key
          and a2._MGIType_key = 1
          and a2._Logicaldb_key = 1
          and a2.prefixpart = 'J:'
          and a2.preferred = 1
          '''

def getRefs():
        #
        # get assigned reference; that is, the first "history" reference
        #

        db.sql('''
        select m._Marker_key, h._Refs_key
        into temporary table refs
        from MRK_Marker m, MRK_History h
        where m._Marker_Type_key = 6
                and m._Marker_Status_key = 1
                and m._Organism_key = 1
        and m._Marker_key = h._Marker_key
        and h.sequenceNum = 1
        ''', None)

        db.sql('create index refs_idx1 on refs(_Marker_key)', None)
        db.sql('create index refs_idx2 on refs(_Refs_key)', None)

def qtl1():

        fp1.write('QTL markers that have no mapping and no allele associated (no/no)\n')
        fp1.write('mapping = no/alleles = no\n')

        results = db.sql('''%s
          and not exists (select 1 from MRK_Notes n where m._Marker_key = n._Marker_key)
          and not exists (select 1 from MLD_Expt_Marker mld where m._Marker_key = mld._Marker_key)
          and not exists (select 1 from ALL_Allele al where m._Marker_key = al._Marker_key and al.isWildType = 0)
          order by symbol
        ''' % (query1), 'auto')

        for r in results:
                fp1.write(r['mgiID'] + TAB)
                fp1.write(r['refID'] + TAB)
                fp1.write(r['symbol'] + TAB)
                fp1.write(r['name'] + TAB)
                fp1.write(CRT)

        fp1.write(CRT + '(%d rows affected)' % (len(results)) + CRT)

def qtl2():

        fp2.write('QTL markers that have mapping but no allele associated (yes/no)\n')
        fp2.write('mapping = yes/alleles = no\n')

        results = db.sql('''%s
          and not exists (select 1 from MRK_Notes n where m._Marker_key = n._Marker_key)
          and exists (select 1 from MLD_Expt_Marker mld where m._Marker_key = mld._Marker_key)
          and not exists (select 1 from ALL_Allele al where m._Marker_key = al._Marker_key and al.isWildType = 0)
          order by symbol
        ''' % (query1), 'auto')

        for r in results:
                fp2.write(r['mgiID'] + TAB)
                fp2.write(mgi_utils.prvalue(r['refID']) + TAB)
                fp2.write(r['symbol'] + TAB)
                fp2.write(r['name'] + TAB)
                fp2.write(CRT)

        fp2.write(CRT + '(%d rows affected)' % (len(results)) + CRT)

        fp2.write('\n\nQTL References with map records that have QTL associated w/o Alleles:\n\n')

        results = db.sql('''%s
          and not exists (select 1 from MRK_Notes n where m._Marker_key = n._Marker_key)
          and exists (select 1 from MLD_Expt_Marker mld where m._Marker_key = mld._Marker_key)
          and not exists (select 1 from ALL_Allele al where m._Marker_key = al._Marker_key and al.isWildType = 0)
          order by numericPart
        ''' % (query2), 'auto')

        for r in results:
                fp2.write(mgi_utils.prvalue(r['refID']) + CRT)
        fp2.write(CRT + '(%d rows affected)' % (len(results)) + CRT)

def qtl3():

        fp3.write('QTL markers that have no mapping but have allele associated (no/yes)\n')
        fp3.write('mapping = no/alleles = yes\n')

        results = db.sql('''%s
          and not exists (select 1 from MRK_Notes n where m._Marker_key = n._Marker_key)
          and not exists (select 1 from MLD_Expt_Marker mld where m._Marker_key = mld._Marker_key)
          and exists (select 1 from ALL_Allele al where m._Marker_key = al._Marker_key and al.isWildType = 0)
          order by symbol
        ''' % (query1), 'auto')

        for r in results:
                fp3.write(r['mgiID'] + TAB)
                fp3.write(mgi_utils.prvalue(r['refID']) + TAB)
                fp3.write(r['symbol'] + TAB)
                fp3.write(r['name'] + TAB)
                fp3.write(CRT)

        fp3.write(CRT + '(%d rows affected)' % (len(results)) + CRT)

def qtl4():

        fp4.write('QTL markers that have assigned reference of J:23000 or J:85000\n')

        results = db.sql('''
          select a1.accID as mgiID, a2.accID as refID, m.symbol, m.name
          from MRK_Marker m, ACC_Accession a1, ACC_Accession a2, refs r
          where m._Marker_Type_key = 6
          and m._Marker_Status_key = 1
          and m._Organism_key = 1
          and m._Marker_key = a1._Object_key
          and a1._MGIType_key = 2
          and a1._Logicaldb_key = 1
          and a1.prefixpart = 'MGI:'
          and a1.preferred = 1
          and m._Marker_key = r._Marker_key
          and r._Refs_key in (22864, 85477)
          and r._Refs_key = a2._Object_key
          and a2._MGIType_key = 1
          and a2._Logicaldb_key = 1
          and a2.prefixpart = 'J:'
          and a2.preferred = 1
          and not exists (select 1 from MRK_Notes n where m._Marker_key = n._Marker_key)
          order by symbol
        ''', 'auto')

        for r in results:
                fp4.write(r['mgiID'] + TAB)
                fp4.write(mgi_utils.prvalue(r['refID']) + TAB)
                fp4.write(r['symbol'] + TAB)
                fp4.write(r['name'] + TAB)
                fp4.write(CRT)

        fp4.write(CRT + '(%d rows affected)' % (len(results)) + CRT)

def qtl5():

        fp5.write('QTL markers that are Reserved\n')

        results = db.sql('''
          select m._Marker_key, 
                to_char(m.creation_date, 'MM/dd/yyyy') as creation_date,
                t.status,
                a1.accID as mgiID, 
                r.jnumID as refID, 
                m.symbol, 
                m.name
          from ACC_Accession a1, 
                MRK_Status t,
                MRK_Marker m,
                MRK_History h,
                BIB_Citation_Cache r
          where m._Marker_Type_key = 6
          and m._Marker_Status_key = 3
          and m._Marker_key = a1._Object_key
          and a1._MGIType_key = 2
          and a1._Logicaldb_key = 1
          and a1.prefixpart = 'MGI:'
          and a1.preferred = 1
          and m._Marker_Status_key = t._Marker_Status_key
          and m._Marker_key = h._Marker_key
          and h.sequenceNum = 1
          and h._Refs_key = r._Refs_key
          order by m.creation_date
        ''', 'auto')

        for r in results:
                fp5.write(r['creation_date'] + TAB)
                fp5.write(r['status'] + TAB)
                fp5.write(r['mgiID'] + TAB)
                fp5.write(mgi_utils.prvalue(r['refID']) + TAB)
                fp5.write(r['symbol'] + TAB)
                fp5.write(r['name'] + TAB)
                fp5.write(CRT)

        fp5.write(CRT + '(%d rows affected)' % (len(results)) + CRT)

#
# main
#

# generate once
getRefs()

fp1 = reportlib.init('MRK_QTL_1', outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)
fp2 = reportlib.init('MRK_QTL_2', outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)
fp3 = reportlib.init('MRK_QTL_3', outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)
fp4 = reportlib.init('MRK_QTL_4', outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)
fp5 = reportlib.init('MRK_QTL_5', outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

qtl1()
qtl2()
qtl3()
qtl4()
qtl5()

reportlib.finish_nonps(fp1)	# non-postscript file
reportlib.finish_nonps(fp2)	# non-postscript file
reportlib.finish_nonps(fp3)	# non-postscript file
reportlib.finish_nonps(fp4)	# non-postscript file
reportlib.finish_nonps(fp5)	# non-postscript file

