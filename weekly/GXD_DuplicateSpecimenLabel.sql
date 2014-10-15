
set nocount on
go

print ''
print ' GXD duplicate specimen label report '
print ''
select distinct substring(bc.jnumid, 1, 12) as jnumID, substring(m.symbol, 1, 25) as symbol, substring(gaav.accid, 1, 12) assayID, substring(s.specimenlabel, 1, 25) as specimenLabel
	from bib_citation_cache bc, gxd_assay a,gxd_assay_acc_view gaav,
	gxd_specimen s,
	mrk_marker m,
	gxd_insituresult gir,
	gxd_insituresultimage giri,
	img_imagepane ip,
	img_image i
	where exists(select 1 from gxd_specimen s2 
		where s.specimenlabel=s2.specimenlabel
		and s._specimen_key!=s2._specimen_key
		and s._assay_key=s2._assay_key)
	and s.specimenlabel is not null
	and s._assay_key=a._assay_key
	and a._assaytype_key!=10
	and a._assaytype_key!=11
	and gir._specimen_key=s._specimen_key
	and giri._result_key=gir._result_key
	and giri._imagepane_key=ip._imagepane_key
	and ip._image_key=i._image_key
	and i.xdim is not null
	and a._refs_key=bc._refs_key
	and a._assay_key=gaav._object_key
	and a._marker_key=m._marker_key
	order by jnumID,symbol,specimenlabel
go

