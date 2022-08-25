#!/bin/csh -f

#
# Template
#


if ( ${?MGICONFIG} == 0 ) then
        setenv MGICONFIG /usr/local/mgi/live/mgiconfig
endif

source ${MGICONFIG}/master.config.csh

cd `dirname $0`

setenv LOG $0.log
rm -rf $LOG
touch $LOG
 
date | tee -a $LOG
 
cat - <<EOSQL | ${PG_DBUTILS}/bin/doisql.csh $0 | tee -a $LOG

select g._GelLane_key, t.gellanecontent as term
INTO TEMPORARY TABLE gmissingbands
from GXD_GelLane g, GXD_GelControl t
where g._GelControl_key = t._GelControl_key
and not exists
(select 1 from GXD_GelBand b where g._GelLane_key = b._GelLane_key)
;

--select g._GelLane_key, t.term
--INTO TEMPORARY TABLE gmissingbands
--from GXD_GelLane g, VOC_Term t
--where g._GelControl_key = t._Term_key
--and not exists
--(select 1 from GXD_GelBand b where g._GelLane_key = b._GelLane_key)
--;

select a.mgiID, a.jnumID, s.sequenceNum, r.term, substring(s.laneLabel, 1, 50) as laneLabel, modifiedBy, s.modification_date
from gmissingbands r, GXD_GelLane s, GXD_Assay_View a
where r._GelLane_key = s._GelLane_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
order by s.modification_date, jnumID, mgiID, s.sequenceNum, laneLabel
;

EOSQL

date |tee -a $LOG

