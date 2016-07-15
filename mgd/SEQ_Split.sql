
select s._Sequence_key
INTO TEMPORARY TABLE split1
from SEQ_Sequence s
where s._SequenceStatus_key = 316344
;

select a.accID
INTO TEMPORARY TABLE split2
from split1 s, ACC_Accession a
where s._Sequence_key = a._Object_key
and a._MGIType_key = 19
and a.preferred = 1
;

\echo ''
\echo 'Split Sequences'
\echo ''
\echo 'A row in this report represents a Sequence that is designated as Split'
\echo 'by the Sequence Provider.'
\echo ''

select s.accID as seqID
from split2 s
order by seqID
;

