print ""
print "Marker Species"
print ""

select substring(name, 1, 30) "Common Name", 
substring(species, 1, 35) "Scientific Name",
_Organism_key
from MRK_Species 
order by name
go
