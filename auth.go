package adminpanel

import (
	"github.com/go-bootstrap/go-bootstrap/project-templates/mysql/models"
	"github.com/qor/admin"
	"github.com/qor/auth"
	"github.com/qor/auth_themes/clean"
	"github.com/qor/qor"
)

var Auth = clean.New(&auth.Config{
	DB: DB,
	// User model needs to implement qor.CurrentUser interface (https://godoc.org/github.com/qor/qor#CurrentUser) to use it in QOR Admin
	UserModel: models.User{},
})

type AdminAuth struct{}

func (AdminAuth) LoginURL(c *admin.Context) string {
	return "/auth/login"
}

func (AdminAuth) LogoutURL(c *admin.Context) string {
	return "/auth/logout"
}

func (AdminAuth) GetCurrentUser(c *admin.Context) qor.CurrentUser {
	currentUser := Auth.GetCurrentUser(c.Request)
	if currentUser != nil {
		qorCurrentUser, ok := 
	}
}

func (AdminAuth) GetCurrentUser(c *admin.Context) qor.CurrentUser {
    currentUser := Auth.GetCurrentUser(c.Request)
    if currentUser != nil {
      qorCurrentUser, ok := currentUser.(qor.CurrentUser)
      if !ok {
        fmt.Printf("User %#v haven't implement qor.CurrentUser interface\n", currentUser)
      }
      return qorCurrentUser
    }
    return nil
}
