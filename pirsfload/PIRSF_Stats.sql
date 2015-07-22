
\echo ""
select count(*) "# of unique PIRSF Terms" from VOC_Term where _Vocab_key = 46
go

\echo ""
select count(distinct _Object_key) "# of Markers w/ PIRSF Terms" from VOC_Annot where _AnnotType_key = 1007
go

