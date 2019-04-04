package adminpanel

// import (
// 	"fmt"

// 	pb "github.com/VideoCoin/common/proto"
// 	"github.com/jinzhu/gorm"
// 	"github.com/qor/admin"
// 	"github.com/qor/auth"
// 	"github.com/qor/auth/authority"
// 	"github.com/qor/auth_themes/clean"
// 	"github.com/qor/qor"
// )

// var (
// 	// Auth initialize Auth for Authentication
// 	Auth = clean.New(&auth.Config{
// 		DB:        db,
// 		UserModel: pb.User{},
// 	})

// 	// Authority initialize Authority for Authorization
// 	Authority = authority.New(&authority.Config{
// 		Auth: Auth,
// 	})

// 	_ = Authority
// )

// type AdminAuth struct{}

// func (AdminAuth) LoginURL(c *admin.Context) string {
// 	return "/auth/login"
// }

// func (AdminAuth) LogoutURL(c *admin.Context) string {
// 	return "/auth/logout"
// }

// func (AdminAuth) GetCurrentUser(c *admin.Context) qor.CurrentUser {
// 	currentUser := Auth.GetCurrentUser(c.Request)
// 	if currentUser != nil {
// 		qorCurrentUser, ok := currentUser.(qor.CurrentUser)
// 		if !ok {
// 			fmt.Printf("User %#v haven't implement qor.CurrentUser interface\n", currentUser)
// 		}
// 		return qorCurrentUser
// 	}
// 	return nil
// }

// func initAuth(db *gorm.DB) {

// 	Admin := admin.New(&admin.AdminConfig{
// 		Auth: AdminAuth{},
// 	})

// }
