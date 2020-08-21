
'''
#
# TR11942
#
# Report:
#	
#       Alleles that have Molecular Notes and 'Inserted expressed sequence' attribute
#	1)  status approved
#	2)  Exclude allele type 'QTL' and 'Not Applicable'
#	3)  Exclude 'Wild Type'
#	4)  Exclude alleles with expressed sequence relationships
#
#	Columns:
#       Allele approval date
#	Allele MGI ID
#	Allele Type
#	Allele symbol
#
#	Sort: Approval Date descending
#
# Usage:
#       ALL_ExpressedSeq.py
#
# Notes:
#
# History:
#
#	TR11942 sc - created
#
'''
 
import sys 
import os 
import string
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Alleles that have Molecular Notes and "Inserted expressed sequence" attribute', os.environ['QCOUTPUTDIR'])
fp.write('\t\texcludes allele types: QTL, Not Applicable\n')
fp.write('\t\tincludes only allele status: Aapproved\n')
fp.write('\t\texcludes Wild Type\n')
fp.write('\t\texcludes Alleles with expressed sequence relationships\n\n')

fp.write(str.ljust('Approval', 15) + \
        str.ljust('Acc ID', 15) + \
        str.ljust('Allele Type', 35) + \
        str.ljust('Symbol', 45) + CRT)

db.sql('''
        select distinct al._Allele_key, al.symbol, t.term as alleleType, 
            a.accID as alleleID,  al.approval_date
        into temporary table approved
        from ALL_Allele al, VOC_Term t, ACC_Accession a, MGI_Note n
        where al._Allele_Type_key = t._Term_key
        and al._Allele_Status_key = 847114
        and al._Allele_Type_key not in (847130, 847131)
        and al.isWildType = 0
        and al._Allele_key = a._Object_key
        and a._MGIType_key = 11
        and a._LogicalDB_key = 1
        and a.preferred = 1
        and a.prefixPart = 'MGI:'
        and al._Allele_key = n._Object_key
        and n._NoteType_key = 1021''', None)

db.sql('create index idx1 on approved(_Allele_key)', None)

db.sql('''select distinct a.*
        into temporary table subtype
        from approved a, VOC_Annot va
        where a._Allele_key = va._Object_key
        and va._AnnotType_key = 1014
        and va._Term_key = 11025597''', None)

db.sql('create index idx2 on subtype(_Allele_key)', None)

results = db.sql('''select s.symbol, s.alleleType,
            s.alleleID, to_char( s.approval_date, 'MM/dd/yyyy') as cDate
        from subtype s
        where not exists (select 1
        from MGI_Relationship r
        where r._Category_key = 1004
        and s._Allele_key = r._object_key_1)
        order by s.approval_date desc''', 'auto')

for r in results:
    fp.write(str.ljust(r['cDate'], 15) + \
         str.ljust(r['alleleID'], 15) + \
         str.ljust(r['alleleType'], 35) + \
         str.ljust(r['symbol'], 45) + CRT)
fp.write(CRT + 'Number of Alleles: ' + str(len(results)) + CRT)

reportlib.finish_nonps(fp)
