print ""
print "MGI Organisms"
print ""

select substring(commonName, 1, 30) "Common Name", 
substring(latinName, 1, 35) "Scientific Name",
_Organism_key
from MGI_Organism
order by commonName
go
