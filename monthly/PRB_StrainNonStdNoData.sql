print ""
print "Non-Standard Strains with no JR# and no data attached"
print ""

select strain = substring(s.strain,1,100)
from PRB_Strain s
where s.standard = 0
and not exists (select 1 from PRB_Strain_Acc_View a
where s._Strain_key = a._Object_key
and a._MGIType_key = 10
and a._LogicalDB_key = 22)
and not exists (select 1 from ALL_Allele a
where s._Strain_key = a._Strain_key)
and not exists (select 1 from ALL_CellLine a
where s._Strain_key = a._Strain_key)
and not exists (select 1 from CRS_Cross a
where s._Strain_key = a._femaleStrain_key
or s._Strain_key = a._maleStrain_key
or s._Strain_key = a._StrainHO_Key
or s._Strain_key = a._StrainHT_Key)
and not exists (select 1 from GXD_Genotype a
where s._Strain_key = a._Strain_key)
and not exists (select 1 from MLD_FISH a
where s._Strain_key = a._Strain_key)
and not exists (select 1 from MLD_InSitu a
where s._Strain_key = a._Strain_key)
and not exists (select 1 from PRB_Allele_Strain a
where s._Strain_key = a._Strain_key)
and not exists (select 1 from PRB_Source a
where s._Strain_key = a._Strain_key)
and not exists (select 1 from RI_RISet a
where s._Strain_key = a._Strain_key_1
or s._Strain_key = a._Strain_key_2)
order by s.strain
go
