package adminpanel

import (
	"github.com/qor/admin"
	"github.com/qor/qor"
)

func (a auth) GetCurrentUser(c *admin.Context) qor.CurrentUser {
	var userid uint

	s, err := a.session.store.Get(c.Request, a.session.name)
	if err != nil {
		return nil
	}
	if v, ok := s.Values[a.session.key]; ok {
		userid = v.(uint)
	} else {
		return nil
	}

	var user AdminUser
	if !a.db.First(&user, "id = ?", userid).RecordNotFound() {
		return &user
	}

	return nil
}

// LoginURL statisfies the Auth interface and returns the route used to log
// users in
func (a auth) LoginURL(c *admin.Context) string { // nolint: unparam
	return a.paths.login
}

// LogoutURL statisfies the Auth interface and returns the route used to logout
// a user
func (a auth) LogoutURL(c *admin.Context) string { // nolint: unparam
	return a.paths.logout
}
