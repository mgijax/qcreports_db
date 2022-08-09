
'''
#
# TR 8747
#
# GXD Monthly Statistics
#
# Usage:
#       GXD_StatsMonthly.py
#
# Used by:
#
# Assumptions:  
#
# History:
#
# lec   10/22/2014
#       - TR11750/postres complient
#	note : counts are not correct in postgres
#
# 04/30/2008	lec
#	- TR 8747; taken from GXD_Stats
#
'''
 
import sys
import os
import string
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT

def monthlyCounts():

    #
    # Gene and Result counts by monthly period from startYear to endYear
    #

    # Gene stats by year/month

    db.sql('''select date_part('year', a.creation_date) as year, 
        date_part('month', a.creation_date) as month, 
        count (distinct a._Marker_key) as genes,
        count (distinct a._Refs_key) as refs
        into temporary table assayGenes 
        from GXD_Assay a 
        where a._AssayType_key in (1,2,3,4,5,6,8,9) 
        group by date_part('year', a.creation_date), date_part('month', a.creation_date)
        ''', None)

    db.sql('create index assayGenes_idx1 on assayGenes(year)', None)
    db.sql('create index assayGenes_idx2 on assayGenes(month)', None)

    #
    # Assay stats by year/month/assay type
    #

    db.sql('''select date_part('year', a.creation_date) as year, date_part('month', a.creation_date) as month, 
        a._AssayType_key, 
        count(*) as assays
        into temporary table assays 
        from GXD_Assay a 
        where a._AssayType_key in (1,2,3,4,5,6,8,9) 
        group by date_part('year', a.creation_date), date_part('month', a.creation_date), a._AssayType_key
        ''', None)

    db.sql('create index assays_idx1 on assays(year)', None)
    db.sql('create index assays_idx2 on assays(month)', None)
    db.sql('create index assays_idx3 on assays(_AssayType_key)', None)

    #
    # Gel stats by year/month/assay type
    #

    db.sql('''select date_part('year', a.creation_date) as year, 
        date_part('month', a.creation_date) as month, 
        a._AssayType_key, 
        count(*) as results
        into temporary table gelresults 
        from GXD_Assay a, GXD_GelLane l, GXD_GelLaneStructure gls , VOC_Term t
        where a._AssayType_key in (1,2,3,4,5,6,8,9) 
        and a._Assay_key = l._Assay_key 
        and l._GelControl_key = t._Term_key and t.term = 'No'
        and l._GelLane_key = gls._GelLane_key 
        group by date_part('year', a.creation_date), date_part('month', a.creation_date), a._AssayType_key
        ''', None)

    db.sql('create index gelresults_idx1 on gelresults(year)', None)
    db.sql('create index gelresults_idx2 on gelresults(month)', None)
    db.sql('create index gelresults_idx3 on gelresults(_AssayType_key)', None)

    #
    # InSitu stats by year/month/assay type
    #

    db.sql('''select date_part('year', a.creation_date) as year, 
        date_part('month', a.creation_date) as month, 
        a._AssayType_key, 
        count(*) as results
        into temporary table insituresults 
        from GXD_Assay a, GXD_Specimen s, GXD_InSituResult r, GXD_ISResultStructure rs 
        where a._AssayType_key in (1,2,3,4,5,6,8,9) 
        and a._Assay_key = s._Assay_key 
        and s._Specimen_key = r._Specimen_key 
        and r._Result_key = rs._Result_key 
        group by date_part('year', a.creation_date), date_part('month', a.creation_date), a._AssayType_key
        ''', None)

    db.sql('create index insituresults_idx1 on insituresults(year)', None)
    db.sql('create index insituresults_idx2 on insituresults(month)', None)
    db.sql('create index insituresults_idx3 on insituresults(_AssayType_key)', None)

    #
    # generate a list of all unique year/month values by the creation date of Assay records
    #

    db.sql('''select distinct date_part('year', creation_date) as year, 
        date_part('month', creation_date) as month
        into temporary table periods from GXD_Assay
        ''', None)

    # initialize a table of periodCounts with all assay types for each year/month
    # and set "0 as assays", "0 as results"
    # subsequent updates will increment the assays and results counts

    db.sql('''select p.year, p.month, t._AssayType_key, substring(t.assayType,1,25) as assayType, 
        0 as assays, 0 as results 
        into temporary table periodCounts 
        from periods p, GXD_AssayType t where t._AssayType_key in (1,2,3,4,5,6,8,9)
        ''', None)

    # update the Assay count

    db.sql('''update periodCounts
        set assays = a.assays
        from assays a 
        where a.year = periodCounts.year 
        and a.month = periodCounts.month 
        and a._AssayType_key = periodCounts._AssayType_key 
        ''', None)

    # update Gel Results count

    db.sql('''update periodCounts
        set results = periodCounts.results + a.results 
        from gelresults a 
        where a.year = periodCounts.year 
        and a.month = periodCounts.month 
        and a._AssayType_key = periodCounts._AssayType_key 
        ''', None)

    # update InSitu count

    db.sql('''update periodCounts
        set results = periodCounts.results + a.results 
        from insituresults a 
        where a.year = periodCounts.year 
        and a.month = periodCounts.month 
        and a._AssayType_key = periodCounts._AssayType_key 
        ''', None)

    db.sql('create index period_idx1 on periodCounts(year)', None)
    db.sql('create index period_idx2 on periodCounts(month)', None)
    db.sql('create index period_idx3 on periodCounts(results)', None)

    #
    # Gene and Result counts by monthly period
    #

    fp.write(2*CRT + 'Gene and Result counts by monthly period:' + 2*CRT)
    fp.write(str.ljust('Year', 10))
    fp.write(str.ljust('Month', 10))
    fp.write(str.ljust('Genes', 10))
    fp.write(str.ljust('Results', 10))
    fp.write(str.ljust('References', 15) + CRT)
    fp.write(str.ljust('----', 10))
    fp.write(str.ljust('-----', 10))
    fp.write(str.ljust('------', 10))
    fp.write(str.ljust('-------', 10))
    fp.write(str.ljust('----------', 15) + CRT)

    #
    # assayGenes is 1-to-many with periodCounts
    # use avg(gene) & avg(refs) to get a single value from assayGenes
    #

    results = db.sql('''select g.year, g.month, 
        avg(g.genes) as genes, 
        sum(r.results) as sumresults,
        avg(g.refs) as ref
        from assayGenes g, periodCounts r 
        where g.year = r.year 
        and g.month = r.month 
        group by g.year, g.month
        order by g.year, g.month
        ''', 'auto')

    for r in results:
        fp.write(str.ljust(str(int(r['year'])), 10))
        fp.write(str.ljust(str(int(r['month'])), 10))
        fp.write(str.ljust(str(int(r['genes'])), 10))
        fp.write(str.ljust(str(int(r['sumresults'])), 10))
        fp.write(str.ljust(str(int(r['ref'])), 15) + CRT)

    #
    # Total Results
    #

    results = db.sql('select sum(results) as totalresults from periodCounts', 'auto')
    for r in results:
        fp.write(CRT + 'Total Results: ' + str(int(r['totalresults'])) + CRT)

    #
    # Assays and results by Assay Type and month/year
    #

    fp.write(2*CRT + 'Assays and Results by Assay Type and Monthly Period:' + CRT)

    #
    # Cache sums by assay type
    #

    asummary = {}
    rsummary = {}
    results = db.sql('''select assayType, sum(assays) as asum, sum(results) as rsum
        from periodCounts group by assayType
        ''', 'auto')
    for r in results:
        asummary[r['assayType']] = r['asum']
        rsummary[r['assayType']] = r['rsum']

    results = db.sql('''select assayType, year, month, assays, results 
        from periodCounts 
        order by assayType, year, month
        ''', 'auto')

    fp.write(2*CRT + str.ljust('Assay Type', 30))
    fp.write(str.ljust('Year', 10))
    fp.write(str.ljust('Month', 10))
    fp.write(str.ljust('Assays', 10))
    fp.write(str.ljust('Results', 10) + CRT)
    fp.write(str.ljust('----------', 30))
    fp.write(str.ljust('----', 10))
    fp.write(str.ljust('-----', 10))
    fp.write(str.ljust('------', 10))
    fp.write(str.ljust('-------', 10) + CRT)

    prevAssay = ''
    for r in results:

        if len(prevAssay) > 0 and prevAssay != r['assayType']:
            fp.write(CRT + 'Total Assays: ' + str(asummary[prevAssay]) + CRT)
            fp.write('Total Results: ' + str(rsummary[prevAssay]) + CRT)
            prevAssay = r['assayType']
            fp.write(2*CRT + str.ljust('Assay Type', 30))
            fp.write(str.ljust('Year', 10))
            fp.write(str.ljust('Month', 10))
            fp.write(str.ljust('Assays', 10))
            fp.write(str.ljust('Results', 10) + CRT)
            fp.write(str.ljust('----------', 30))
            fp.write(str.ljust('----', 10))
            fp.write(str.ljust('-----', 10))
            fp.write(str.ljust('------', 10))
            fp.write(str.ljust('-------', 10) + CRT)

        fp.write(str.ljust(r['assayType'], 30))
        fp.write(str.ljust(str(int(r['year'])), 10))
        fp.write(str.ljust(str(int(r['month'])), 10))
        fp.write(str.ljust(str(int(r['assays'])), 10))
        fp.write(str.ljust(str(int(r['results'])), 10) + CRT)
        prevAssay = r['assayType']

    fp.write(CRT + 'Total Assays: ' + str(asummary[prevAssay]) + CRT)
    fp.write('Total Results: ' + str(rsummary[prevAssay]) + CRT)


########
#      #
# Main #
#      #
########

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], sqlLogging = 1)
monthlyCounts()
reportlib.finish_nonps(fp)
