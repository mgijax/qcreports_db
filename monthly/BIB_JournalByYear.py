#
# Report: BIB_JournalByYear.py
#
# Lit triage: journals x year of publication
#
# This purpose of this report is to generate journal counts by year where:
#       . journal must have a J:
#       . year is within the last 5 years of today's year
#
# x axis = year
# y axis = journal
#

import sys
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

def init():
        global fp
        global displayByYear

        fp = reportlib.init(sys.argv[0], 'Columns report the number of J#s created using articles from each journal during the publication year', os.environ['QCOUTPUTDIR'])

        # 
        # set of unique years, descending
        #
        displayByYear = {}
        results = db.sql('''
                select distinct r.year
                from BIB_Refs r
                where r.year between date_part('year', CURRENT_DATE) - 5 and date_part('year', CURRENT_DATE) 
                and r.journal is not null
                order by year desc
                ''', 'auto')
        for r in results:
                displayByYear[r['year']] = 0


def process():

        #
        # count grouped by year, journal
        #       . journal must have a J:
        #       . year is within the last 5 years of today's year
        #

        countByJournal = {}
        results = db.sql('''
                select r.journal, r.year, count(*) as counter
                from BIB_Refs r
                where r.year between date_part('year', CURRENT_DATE) - 5 and date_part('year', CURRENT_DATE) 
                and r.journal is not null
                and exists (select 1 from BIB_Citation_Cache c where r._refs_key = c._refs_key and c.jnumid is not null)
                group by r.journal, year
                order by r.year desc, r.journal
                ''', 'auto')
        for r in results:
                if r['journal'] not in countByJournal:
                        countByJournal[r['journal']] = displayByYear.copy()
                countByJournal[r['journal']][r['year']] = r['counter']

        #
        # write the year
        #
        fp.write(TAB)
        for r in displayByYear:
                fp.write(str(r) + TAB)
        fp.write(CRT)

        #
        # write the journals & counts
        #
        for r in countByJournal:
                fp.write(r + TAB)
                for y in displayByYear:
                        fp.write(str(countByJournal[r][y]) + TAB)
                fp.write(CRT)

#
# main
#
init()
process()
reportlib.finish_nonps(fp)

