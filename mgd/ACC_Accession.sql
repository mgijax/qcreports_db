print ""
print "Markers w/out MGI Accession Numbers"
print ""

select m._Marker_key, m.symbol, m.chromosome
from MRK_Marker m
where m._Species_key = 1
and m._Marker_Status_key = 1
and not exists (select a.* from MRK_Acc_View a
where a.prefixPart = "MGI:"
and a._LogicalDB_key = 1
and a._Object_key = m._Marker_key)
go

print ""
print "Markers w/duplicate preferred MGI Accession Numbers"
print ""

select _Object_key, accID
from ACC_Accession
where _MGIType_key = 2 and _LogicalDB_Key = 1 and preferred = 1
group by accID having count(*) > 1
go

print ""
print "References w/out MGI Accession Numbers"
print ""

select m._Refs_key, m._primary, m.journal
from BIB_Refs m
where 
not exists (select a.* from BIB_Acc_View a
where a.prefixPart = "MGI:"
and a._LogicalDB_key = 1
and a._Object_key = m._Refs_key)
go

print ""
print "References w/out J Numbers"
print ""

select m._Refs_key, m._primary, m.journal
from BIB_Refs m
where 
not exists (select a.* from BIB_Acc_View a
where a.prefixPart = "J:"
and a._LogicalDB_key = 1
and a._Object_key = m._Refs_key)
go

print ""
print "References w/duplicate preferred MGI Accession Numbers"
print ""

select _Object_key, accID
from ACC_Accession
where _MGIType_key = 1 and _LogicalDB_Key = 1 and preferred = 1
group by accID having count(*) > 1
go

print ""
print "Experiments w/out MGI Accession Numbers"
print ""

select m._Expt_key, exptType = substring(m.exptType, 1, 50)
from MLD_Expts m
where 
not exists (select a.* from MLD_Acc_View a
where a.prefixPart = "MGI:"
and a._LogicalDB_key = 1
and a._Object_key = m._Expt_key)
go

print ""
print "Experiments w/duplicate preferred MGI Accession Numbers"
print ""

select _Object_key, accID
from ACC_Accession
where _MGIType_key = 4 and _LogicalDB_Key = 1 and preferred = 1
group by accID having count(*) > 1
go

print ""
print "Probes w/out MGI Accession Numbers"
print ""

select m._Probe_key, m.name
from PRB_Probe m
where 
not exists (select a.* from PRB_Acc_View a
where a.prefixPart = "MGI:"
and a._LogicalDB_key = 1
and a._Object_key = m._Probe_key)
go

print ""
print "Probes w/duplicate preferred MGI Accession Numbers"
print ""

select _Object_key, accID
from ACC_Accession
where _MGIType_key = 3 and _LogicalDB_Key = 1 and preferred = 1
group by accID having count(*) > 1

print ""
print "Antigens w/out MGI Accession Numbers"
print ""

select m._Antigen_key, m.antigenName
from GXD_Antigen m
where 
not exists (select a.* from GXD_Antigen_Acc_View a
where a.prefixPart = "MGI:"
and a._LogicalDB_key = 1
and a._Object_key = m._Antigen_key)
go

print ""
print "Antigens w/duplicate preferred MGI Accession Numbers"
print ""

select _Object_key, accID
from ACC_Accession
where _MGIType_key = 7 and _LogicalDB_Key = 1 and preferred = 1
group by accID having count(*) > 1
go

print ""
print "Antibodys w/out MGI Accession Numbers"
print ""

select m._Antibody_key, m.antibodyName
from GXD_Antibody m
where 
not exists (select a.* from GXD_Antibody_Acc_View a
where a.prefixPart = "MGI:"
and a._LogicalDB_key = 1
and a._Object_key = m._Antibody_key)
go

print ""
print "Antibodys w/duplicate preferred MGI Accession Numbers"
print ""

select _Object_key, accID
from ACC_Accession
where _MGIType_key = 6 and _LogicalDB_Key = 1 and preferred = 1
group by accID having count(*) > 1
go

print ""
print "Assays w/out MGI Accession Numbers"
print ""

select m._Assay_key
from GXD_Assay m
where 
not exists (select a.* from GXD_Assay_Acc_View a
where a.prefixPart = "MGI:"
and a._LogicalDB_key = 1
and a._Object_key = m._Assay_key)
go

print ""
print "Assays w/duplicate preferred MGI Accession Numbers"
print ""

select _Object_key, accID
from ACC_Accession
where _MGIType_key = 8 and _LogicalDB_Key = 1 and preferred = 1
group by accID having count(*) > 1
go

print ""
print "Images w/out MGI Accession Numbers"
print ""

select m._Image_key
from IMG_Image m
where 
not exists (select a.* from IMG_Image_Acc_View a
where a.prefixPart = "MGI:"
and a._LogicalDB_key = 1
and a._Object_key = m._Image_key)
go

print ""
print "Images w/duplicate preferred MGI Accession Numbers"
print ""

select _Object_key, accID
from ACC_Accession
where _MGIType_key = 9 and _LogicalDB_Key = 1 and preferred = 1
group by accID having count(*) > 1
go
