package adminpanel

import (
	pb "github.com/VideoCoin/common/proto"
	"github.com/qor/admin"
)

func init() {
	// Set Auth interface when initialize QOR Admin
	Admin := admin.New(&admin.AdminConfig{
		Auth: &AdminAuth{},
	})
}

func (s *service) initAdmin() {
	transcoders := s.adm.AddResource(pb.Transcoder{})
	profiles := s.adm.AddResource(pb.Profile{})
	workOrders := s.adm.AddResource(pb.WorkOrder{})

	profiles.IndexAttrs("-XXX_unrecognized", "-XXX_sizecache", "-XXX_NoUnkeyedLiteral")

	profiles.Meta(&admin.Meta{Name: "XXX_NoUnkeyedLiteral", Type: "hidden"})
	profiles.Meta(&admin.Meta{Name: "XXX_sizecache", Type: "hidden"})
	profiles.Meta(&admin.Meta{Name: "XXX_unrecognized", Type: "hidden"})

	transcoders.Meta(&admin.Meta{Name: "XXX_NoUnkeyedLiteral", Type: "hidden"})
	transcoders.Meta(&admin.Meta{Name: "XXX_sizecache", Type: "hidden"})
	transcoders.Meta(&admin.Meta{Name: "XXX_unrecognized", Type: "hidden"})
	transcoders.Meta(&admin.Meta{Name: "Worker", Type: "hidden"})

	workOrders.Meta(&admin.Meta{Name: "XXX_NoUnkeyedLiteral", Type: "hidden"})
	workOrders.Meta(&admin.Meta{Name: "XXX_sizecache", Type: "hidden"})
	workOrders.Meta(&admin.Meta{Name: "XXX_unrecognized", Type: "hidden"})
	workOrders.Meta(&admin.Meta{Name: "Chunks", Type: "hidden"})
	workOrders.Meta(&admin.Meta{Name: "Worker", Type: "hidden"})
}
