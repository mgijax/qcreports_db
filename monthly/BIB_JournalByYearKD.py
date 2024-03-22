#
# Report: BIB_JournalByYear.py
#
# WTS2-1449 Lit triage: journals' keep/discard numbers
#
# This purpose of this report is to generate journal counts by year where:
#       . year is within the last 5 years of today's year
#
# x axis = year/total, year/keep, year/discard
# y axis = journal
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
        global fp
        global displayByRelevance
        global displayByYear
        
        fp = reportlib.init(sys.argv[0], 'For each publication year columns report the Total number of papers imported, classified as Keep, or classified as Discard from each journal.', os.environ['QCOUTPUTDIR'])

        # 
        # set of unique years
        #
        displayByRelevance = {}
        results = db.sql(''' select term from voc_term where _vocab_key = 149 and term != 'Not Specified' order by term desc ''', 'auto')
        for r in results:
                displayByRelevance[r['term']] = 0
        
        displayByYear = {}
        results = db.sql('''
                select distinct r.year
                from BIB_Refs r
                where r.year between date_part('year', CURRENT_DATE) - 5 and date_part('year', CURRENT_DATE) 
                and r.journal is not null
                order by year
                ''', 'auto')
        for r in results:
                deepCopy = copy.deepcopy(displayByRelevance)
                displayByYear[r['year']] = deepCopy
        #print(displayByYear)

def process():
        #
        # count grouped by year, journal
        #       . journal must have a J:
        #       . year is within the last 5 years of today's year
        #

        displayByJournal = {}
        results = db.sql('''
                select r.journal, r.year, c.relevanceterm, count(*) as counter
                from BIB_Refs r, BIB_Citation_Cache c
                where r.year between date_part('year', CURRENT_DATE) - 5 and date_part('year', CURRENT_DATE) 
                and r.journal is not null
                and r._refs_key = c._refs_key 
                group by r.journal, year, relevanceterm
                order by r.journal, r.year, c.relevanceterm
                ''', 'auto')
        for r in results:
                journal = r['journal']
                year = r['year']
                relevanceterm = r['relevanceterm']
                if journal not in displayByJournal:
                        deepCopy = copy.deepcopy(displayByYear)
                        displayByJournal[journal] = deepCopy
                displayByJournal[journal][year][relevanceterm] = r['counter']

        #
        # write the year
        #
        fp.write(TAB)
        for r in displayByYear:
                fp.write(str(r) + ' Total' + TAB)
                for t in displayByYear[r]:
                        fp.write(str(r) + ' ' + t + TAB)
                fp.write(CRT)

        #
        # write the journals & counts
        #
        for r in displayByJournal:
                fp.write(r + TAB)
                for y in displayByJournal[r]:
                        totalCount = 0
                        for t in displayByYear[y]:
                                totalCount += displayByJournal[r][y][t]
                        fp.write(str(totalCount) + TAB)
                for y in displayByJournal[r]:
                        for t in displayByYear[y]:
                                fp.write(str(displayByJournal[r][y][t]) + TAB)
                fp.write(CRT)

#
# main
#
init()
process()
reportlib.finish_nonps(fp)

