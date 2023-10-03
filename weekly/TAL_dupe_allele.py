##########################################################################
#
# TAL_dupe_allele.py 
#
# Usage: ${PYTHON} TAL_dupe_allele.py
#  
# Report:
#       Weekly report of duplicate targeted alleles
# 
# History:
#  
# 10/03/2023    sc
#       -  moved from the targetedalleleload
#
###########################################################################

import os
import sys
import reportlib
import db

db.setTrace()
db.useOneConnection(1)

TAB= reportlib.TAB
CRT = reportlib.CRT

fp = reportlib.init(sys.argv[0], 'Weekly Report for Duplicated GenTar Targeted Alleles', os.environ['QCOUTPUTDIR'])

fp.write(TAB.join(['cellline','allele_status', 'allele_key','symbol','creation_date']))
fp.write(CRT)

#
# Main
#

# get all duplicated tal load created alleles
db.sql('''
    select to_char(a.creation_date, 'MM/dd/yyyy') as cdate, a._allele_key, 
        a.symbol, t.term as status
    into temporary table dups
    from all_allele a, VOC_Term t
    where a._CreatedBy_key = 1466
        and a._Allele_Status_key = t._Term_key
    and exists (select 1 from all_allele a2
    where a2._allele_key != a._allele_key
    and a.symbol = a2.symbol)
    order by a.symbol ''', None)

db.sql('create index idx1 on dups(_Allele_key)', None)
results = db.sql('''select d.*, c.cellLine
        from dups d
        left outer join ALL_Allele_CellLine aac on (
            d._Allele_key = aac._Allele_key)
        left outer join ALL_CellLine c on (
            aac._MutantCellLine_key = c._CellLine_key)''', 'auto')

for r in results:
    symbol = r['symbol']
    key = r['_Allele_key']
    status = r['status']
    date = r['cdate']
    cellLine = r['cellLine']
    if cellLine == None:
        cellLine = ''
    fp.write('%s%s%s%s%s%s%s%s%s%s' % (cellLine, TAB, status, TAB, key, TAB, symbol, TAB, date, CRT ))

#
# Post Process
#

reportlib.finish_nonps(fp)      # non-postscript file

db.useOneConnection(0)
