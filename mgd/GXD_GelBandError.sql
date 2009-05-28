
/* 
 * TR 9665
 * Gel Bands that are attached to the correct Gel Row/Gel Lane
 * but have a different Gel Lane/Assay key
*/

print ""
print "Gel Bands that are attached to the correct Gel Row/Gel Lane"
print "but have a different Gel Lane/Assay key"
print ""

select substring(a1.accID,1,15) "acc #1", 
substring(u1.login,1,10) "user #1", 
substring(a2.accID,1,15) "acc #2", 
substring(u2.login,1,10) "user #2", 
r._Assay_key "assay #1", l._Assay_key "assay #2"
from GXD_GelBand b, GXD_GelRow r, GXD_GelLane l, ACC_Accession a1, ACC_Accession a2,
MGI_User u1, MGI_User u2
where b._GelLane_key = l._GelLane_key 
and r._GelRow_key = b._GelRow_key 
and r._Assay_key != l._Assay_key
and r._Assay_key = a1._Object_key
and a1._MGIType_key = 8
and l._Assay_key = a2._Object_key
and a2._MGIType_key = 8
and a1._CreatedBy_key = u1._User_key
and a2._CreatedBy_key = u2._User_key
go

