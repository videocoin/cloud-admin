package resources

import (
	profiles_v1 "github.com/videocoin/cloud-api/profiles/v1"
	transcoder_v1 "github.com/videocoin/cloud-api/transcoder/v1"
	workorder_v1 "github.com/videocoin/cloud-api/workorder/v1"
	"github.com/qor/admin"
)

// AddTranscoders adds the transcoder model to the admin interface
func AddTranscoders(adm *admin.Admin) {
	transcoders := adm.AddResource(transcoder_v1.Transcoder{})
	transcoders.IndexAttrs("-XXX_NoUnkeyedLiteral", "-XXX_sizecache", "-XXX_unrecognized")
	transcoders.Meta(&admin.Meta{Name: "XXX_NoUnkeyedLiteral", Type: "hidden"})
	transcoders.Meta(&admin.Meta{Name: "XXX_sizecache", Type: "hidden"})
	transcoders.Meta(&admin.Meta{Name: "XXX_unrecognized", Type: "hidden"})
	transcoders.Meta(&admin.Meta{Name: "Worker", Type: "hidden"})
}

// AddWorkOrders add workOrder resource and ignore proto fields
func AddWorkOrders(adm *admin.Admin) {
	workOrders := adm.AddResource(workorder_v1.WorkOrder{})
	workOrders.IndexAttrs("-XXX_NoUnkeyedLiteral", "-XXX_sizecache", "-XXX_unrecognized")
	workOrders.Meta(&admin.Meta{Name: "XXX_NoUnkeyedLiteral", Type: "hidden"})
	workOrders.Meta(&admin.Meta{Name: "XXX_sizecache", Type: "hidden"})
	workOrders.Meta(&admin.Meta{Name: "XXX_unrecognized", Type: "hidden"})
	workOrders.Meta(&admin.Meta{Name: "Chunks", Type: "hidden"})
	workOrders.Meta(&admin.Meta{Name: "Worker", Type: "hidden"})
}

// AddProfiles adds profiles resource and ignores the proto fields
func AddProfiles(adm *admin.Admin) {
	profiles := adm.AddResource(profiles_v1.Profile{})
	profiles.IndexAttrs("-XXX_NoUnkeyedLiteral", "-XXX_sizecache", "-XXX_unrecognized")
	profiles.Meta(&admin.Meta{Name: "XXX_NoUnkeyedLiteral", Type: "hidden"})
	profiles.Meta(&admin.Meta{Name: "XXX_sizecache", Type: "hidden"})
	profiles.Meta(&admin.Meta{Name: "XXX_unrecognized", Type: "hidden"})
}
