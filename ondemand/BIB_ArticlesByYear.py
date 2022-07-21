#
# WTS2_673.py
#
# Author Joel Richardson
#
# Implements ad hoc report requested in WTS2-673, i.e., a year X journal 
# matrix of counts. Each count is the number of J#s created for that year 
# and that journal.
#
# Usage:
# optional arguments:
#  -h, --help         show this help message and exit
#  -y MINYEAR         Starting year for query (default=0).
#  -o {year,journal}  Matrix orientation. year=year x journal, journal=journal
#                     x year (default=journal).

import db
import argparse

def getArgs () :
    parser = argparse.ArgumentParser("Generates a year X journal matrix of counts. Each count is the number of J#s created for that year and that journal.")

    parser.add_argument(
        '-y',
        dest = 'minYear',
        default = 0,
        type=int,
        help = 'Starting year for query (default=%(default)d).' )

    parser.add_argument(
        '-o',
        dest = 'orientation',
        default = 'journal',
        choices = ['year', 'journal'],
        help = 'Matrix orientation.\nyear=year x journal,\tjournal=journal x year\t(default=%(default)s).')

    args = parser.parse_args()
    return args

def main () :
    opts = getArgs()

    q = '''
        select r.year, r.journal, count(r.*)
        from BIB_refs r, acc_accession a
        where r._refs_key = a._object_key
        and a._mgitype_key = 1
        and a._logicaldb_key = 1
        and a.prefixPart = 'J:'
        and r.year >= %d
        group by r.year, r.journal
        order by r.year desc, r.journal
        ''' % opts.minYear

    mx = {}
    ys = set()
    js = set()
    for r in db.sql(q):
        y = r['year']
        j = r['journal']
        c = r['count']
        ys.add(y)
        js.add(str(j))
        mx.setdefault(y, {})[j] = c

    ys = list(ys)
    ys.sort(key=lambda y:-y)

    js = list(js)
    js.sort()

    if opts.orientation == 'year':
        # cols=journals, rows=years
        hdrs = [''] + js
        print( '\t'.join(hdrs) )
        for y in ys:
            row = [y] + [mx.get(y,{}).get(j,0) for j in js]
            row = map(str, row)
            print( '\t'.join(row) )
    else:
        # cols=years, rows=journals
        hdrs = [''] + [str(y) for y in ys]
        print( '\t'.join(hdrs) )
        for j in js:
            row = [j] + [mx.get(y,{}).get(j,0) for y in ys]
            row = map(str, row)
            print( '\t'.join(row) )

#
main()
