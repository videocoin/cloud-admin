package resources

import (
	pb "github.com/VideoCoin/common/proto"
	"github.com/qor/admin"
)

// AddTranscoders adds the product model to the admin interface
func AddTranscoders(adm *admin.Admin) {
	transcoders := adm.AddResource(pb.Transcoder{})
	transcoders.IndexAttrs("-XXX_NoUnkeyedLiteral", "-XXX_sizecache", "-XXX_unrecognized")
	transcoders.Meta(&admin.Meta{Name: "XXX_NoUnkeyedLiteral", Type: "hidden"})
	transcoders.Meta(&admin.Meta{Name: "XXX_sizecache", Type: "hidden"})
	transcoders.Meta(&admin.Meta{Name: "XXX_unrecognized", Type: "hidden"})
	transcoders.Meta(&admin.Meta{Name: "Worker", Type: "hidden"})
}

// AddWorkOrders add workOrder resource and ignore proto fields
func AddWorkOrders(adm *admin.Admin) {
	workOrders := adm.AddResource(pb.WorkOrder{})
	workOrders.IndexAttrs("-XXX_NoUnkeyedLiteral", "-XXX_sizecache", "-XXX_unrecognized")
	workOrders.Meta(&admin.Meta{Name: "XXX_NoUnkeyedLiteral", Type: "hidden"})
	workOrders.Meta(&admin.Meta{Name: "XXX_sizecache", Type: "hidden"})
	workOrders.Meta(&admin.Meta{Name: "XXX_unrecognized", Type: "hidden"})
	workOrders.Meta(&admin.Meta{Name: "Chunks", Type: "hidden"})
	workOrders.Meta(&admin.Meta{Name: "Worker", Type: "hidden"})
}

// AddProfiles adds profiles resource and ignores the proto fields
func AddProfiles(adm *admin.Admin) {
	profiles := adm.AddResource(pb.Profile{})
	profiles.IndexAttrs("-XXX_NoUnkeyedLiteral", "-XXX_sizecache", "-XXX_unrecognized")
	profiles.Meta(&admin.Meta{Name: "XXX_NoUnkeyedLiteral", Type: "hidden"})
	profiles.Meta(&admin.Meta{Name: "XXX_sizecache", Type: "hidden"})
	profiles.Meta(&admin.Meta{Name: "XXX_unrecognized", Type: "hidden"})
}
