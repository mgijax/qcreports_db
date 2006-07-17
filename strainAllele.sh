#!/bin/csh -f

# $Header$
# $Name$

#
# Program: strainAllele.sh
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To update PRB_Strain_Marker._Allele_key
#	with the appropriate value for
#	mutant strains with at most one Marker and no Allele
#
# Requirements Satisfied by This Program:
#
#	TR 4702
#
# Usage:
#	strainAllele.sh
#
# Envvars:
#
# Inputs: None
#
# Outputs: strainAllele.log
#
# Exit Codes:
#
# Assumes:
#
# Bugs:
#
# Implementation:
#
#    Modules:
#
# Modification History:
#
# 04/24/2003 lec
#	- TR 4702; created
#
#

cd `dirname $0` && source ./Configuration

setenv LOG ${QCOUTPUTDIR}/`basename $0 sh`log
rm -rf $LOG
touch $LOG
 
date >> $LOG
 
cat - <<EOSQL | doisql.csh ${MGD_DBSERVER} ${MGD_DBNAME} $0 >> $LOG

use ${MGD_DBNAME}
go

select distinct s._Strain_key, strain = substring(s.strain,1,85), 
alleleSymbol = substring(strain, charindex("-", strain) + 1, char_length(strain)),
sm.symbol, sm._Marker_key, sm._Allele_key
into #strains
from PRB_Strain s, PRB_Strain_Type st, VOC_Term t, PRB_Strain_Marker_View sm
where s.strain like '%>'
and s.strain not like 'STOCK%'
and s._Strain_key = st._Strain_key
and st._StrainType_key = t._Term_key
and t.term in ('mutant stock', 'mutant strain', 'targeted mutation')
and s._Strain_key = sm._Strain_key
go

select *
into #singles
from #strains
group by _Strain_key having count(*) = 1
go

print ""
print "Strains ending with '>' "
print "with Strain Type of mutant stock, mutant strain or targeted mutation "
print "with at most one Marker and Marker has no Allele"
print "and Allele symbol is in MGD"
print ""

select s.strain, s.symbol, s.alleleSymbol
from #singles s, ALL_Allele a
where s._Allele_key is null
and s._Marker_key = a._Marker_key
and s.alleleSymbol = a.symbol
order by s.strain
go

print ""
print "Strains ending with '>' "
print "with Strain Type of mutant stock, mutant strain or targeted mutation "
print "with at most one Marker and Marker has no Allele"
print "and Allele symbol is *not* in MGD"
print ""

select s.strain, s.symbol, s.alleleSymbol
from #singles s
where s._Allele_key is null
and not exists (select 1 from ALL_Allele a
where s._Marker_key = a._Marker_key
and s.alleleSymbol = a.symbol)
order by s.strain
go

checkpoint
go

/* do the update */

update PRB_Strain_Marker 
set _Allele_key = a._Allele_key,
    modification_date = getdate()
from #singles s, PRB_Strain_Marker pm, ALL_Allele a
where s._Allele_key is null
and s._Strain_key = pm._Strain_key
and s._Marker_key = pm._Marker_key
and s._Marker_key = a._Marker_key
and s.alleleSymbol = a.symbol
go

quit

EOSQL

date >> $LOG

