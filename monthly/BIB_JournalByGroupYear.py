#
# Report: BIB_JournalByGroupYear.py
#
# Lit triage: journals x curatorial group
#
# The purpose of this report is to generate journal counts by group:
#       AP, GXD, GO, and Tumor.
# 
# * one report per group
#       Lit triage: journals x AP
#       Lit triage: journals x GXD
#       Lit triage: journals x GO
#       Lit triage: journals x Tumor
#
# 1. Routed records (each year for group)
# 2. Chosen records (each year for group)
# 3. Indexed records (each year for group)
# 4. Full-coded records (each year for group)
# 5. Rejected records (each year for group)
# 6. Not routed records (each year for group)
# 

import sys
import os
import copy
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

def init():
        global displayByStatus
        global displayByYear
        global fp1, fp2, fp3, fp4

        # 
        # set of unique status & years
        # year -> each status
        #

        displayByStatus = {}
        results = db.sql(''' select term from voc_term where _vocab_key = 128 ''', 'auto')
        for r in results:
                displayByStatus[r['term']] = 0

        displayByYear = {}
        results = db.sql('''
                select distinct r.year
                from BIB_Refs r
                where r.year between date_part('year', CURRENT_DATE) - 5 and date_part('year', CURRENT_DATE) 
                and r.journal is not null
                order by year
                ''', 'auto')
        for r in results:
                deepCopy = copy.deepcopy(displayByStatus)
                displayByYear[r['year']] = deepCopy
        #print(displayByYear)

        #
        # create fp reports
        # print year headers
        #

        header = ' - Group reference usage by journal reported by publication year'
        fp1 = reportlib.init('BIB_JournalByGroupYear_AP', 'AP' + header, os.environ['QCOUTPUTDIR'])
        fp2 = reportlib.init('BIB_JournalByGroupYear_GXD', 'GXD' + header, os.environ['QCOUTPUTDIR'])
        fp3 = reportlib.init('BIB_JournalByGroupYear_GO', 'GO' + header, os.environ['QCOUTPUTDIR'])
        fp4 = reportlib.init('BIB_JournalByGroupYear_Tumor', 'Tumor' + header, os.environ['QCOUTPUTDIR'])

        for fp in (fp1, fp2, fp3, fp4):
                fp.write(TAB)
                for r in displayByYear:
                        fp.write('Routed' + ' ' + str(r) + TAB)
                        fp.write('Chosen' + ' ' + str(r) + TAB)
                        fp.write('Indexed' + ' ' + str(r) + TAB)
                        fp.write('Full-coded' + ' ' + str(r) + TAB)
                        fp.write('Rejected' + ' ' + str(r) + TAB)
                        fp.write('Not Routed' + ' ' + str(r) + TAB)
                fp.write(CRT)

def process(fp, group):
        #
        # journal -> group -> year -> status
        #
        # 1. Routed records (each year for group)
        # 2. Chosen records (each year for group)
        # 3. Indexed records (each year for group)
        # 4. Full-coded records (each year for group)
        # 5. Rejected records (each year for group)
        # 6. Not routed records (each year for group)
        #

        displayByGroup = {}

        results = db.sql('''
                select r.journal, t1.abbreviation as group, r.year, t2.term as status, count(*) as counter
                from BIB_Refs r, BIB_Workflow_Status s, VOC_Term t1, VOC_Term t2
                where r.year between date_part('year', CURRENT_DATE) - 5 and date_part('year', CURRENT_DATE) 
                and r.journal is not null
                and r._Refs_key = s._Refs_key
                and s.isCurrent = 1
                and s._Group_key = t1._Term_key
                and t1.abbreviation = '%s'
                and s._Status_key = t2._Term_key
                group by r.journal, t1.abbreviation, r.year, t2.term
                order by r.journal, t1.abbreviation, r.year, t2.term
        ''' % (group), 'auto')

        for r in results:
                journal = r['journal']
                group = r['group']
                year = r['year']
                status = r['status']
                if journal not in displayByGroup:
                        deepCopy = copy.deepcopy(displayByYear)
                        displayByGroup[journal] = deepCopy
                displayByGroup[journal][year][status] = r['counter']

        for r in displayByGroup:
                fp.write(r + TAB)
                for y in displayByGroup[r]:
                        fp.write(str(displayByGroup[r][y]['Routed']) + TAB)
                        fp.write(str(displayByGroup[r][y]['Chosen']) + TAB)
                        fp.write(str(displayByGroup[r][y]['Indexed']) + TAB)
                        fp.write(str(displayByGroup[r][y]['Full-coded']) + TAB)
                        fp.write(str(displayByGroup[r][y]['Rejected']) + TAB)
                        fp.write(str(displayByGroup[r][y]['Not Routed']) + TAB)
                fp.write(CRT)
                
#
# main
#
init()
process(fp1, 'AP')
process(fp2, 'GXD')
process(fp3, 'GO')
process(fp4, 'Tumor')
reportlib.finish_nonps(fp1)
reportlib.finish_nonps(fp2)
reportlib.finish_nonps(fp3)
reportlib.finish_nonps(fp4)

