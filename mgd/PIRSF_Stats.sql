
print ""
print "Number of unique PIRSF Terms"
print "

select count(*) from VOC_Term where _Vocab_key = 46
go

print ""
print "Number of Mouse Markers with PIRSF Terms"
print ""

select count(distinct _Object_key) from VOC_Annot where _AnnotType_key = 1007
go

