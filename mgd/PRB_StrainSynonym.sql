print ""
print "Strain Synonyms"
print ""

select substring(s.strain,1,125) "strain", substring(y.synonym,1,125) "synonym"
from PRB_Strain s, PRB_Strain_Synonym y
where s._Strain_key = y._Strain_key
order by s.strain
go

