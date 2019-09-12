package admin

import (
	"net/http"

	"github.com/gin-contrib/sessions"
	"github.com/gin-contrib/sessions/cookie"
	"github.com/gin-gonic/gin"
	"github.com/jinzhu/gorm"
	"github.com/qor/admin"
	"github.com/qor/qor"
	"github.com/sirupsen/logrus"
	users_v1 "github.com/videocoin/cloud-api/users/v1"
)

type auth struct {
	db      *gorm.DB
	session sessionConfig
	paths   pathConfig
}

type sessionConfig struct {
	name  string
	key   string
	store cookie.Store
}

type pathConfig struct {
	login  string
	logout string
	admin  string
}

// GetLogin simply returns the login page
func (a *auth) GetLogin(c *gin.Context) {
	if sessions.Default(c).Get(a.session.key) != nil {
		c.Redirect(http.StatusSeeOther, a.paths.admin)
		return
	}
	c.HTML(http.StatusOK, "login.html", gin.H{})
}

func (a *auth) GetUserRole(email string) (users_v1.UserRole, error) {
	u := users_v1.User{}
	if err := a.db.Table("users").Where("email = ?", email).First(&u).Error; err != nil {
		return users_v1.UserRoleRegular, err
	}
	return u.Role, nil
}

// PostLogin is the handler to check if the user can connect
func (a *auth) PostLogin(c *gin.Context) {
	session := sessions.Default(c)
	email := c.PostForm("email")
	password := c.PostForm("password")
	if email == "" || password == "" {
		c.Redirect(http.StatusSeeOther, a.paths.login)
		return
	}
	var u users_v1.User
	if a.db.Table("users").Where(&users_v1.User{Email: email}).First(&u).RecordNotFound() {
		logrus.Warn("Record Not Found")
		c.Redirect(http.StatusSeeOther, a.paths.login)
		return
	}
	if !u.CheckPassword(password) {
		logrus.Warn("Password does not match")
		c.Redirect(http.StatusSeeOther, a.paths.login)
		return
	}

	role, err := a.GetUserRole(email)
	if role != users_v1.UserRoleSuper {
		logrus.Warn("User has no role")
		c.Redirect(http.StatusSeeOther, a.paths.login)
		return
	}
	if err != nil {
		logrus.WithError(err).Warn("failed to get role")
		c.Redirect(http.StatusSeeOther, a.paths.login)
		return
	}

	a.db.Save(&u)

	session.Set(a.session.key, u.Id)
	err = session.Save()
	if err != nil {
		logrus.WithError(err).Warn("Couldn't save session")
		c.Redirect(http.StatusSeeOther, a.paths.login)
		return
	}
	logrus.Info("redirecting")
	c.Redirect(http.StatusSeeOther, a.paths.admin)
}

// GetLogout allows the user to disconnect
func (a *auth) GetLogout(c *gin.Context) {
	session := sessions.Default(c)
	session.Delete(a.session.key)
	if err := session.Save(); err != nil {
		logrus.WithError(err).Warn("Couldn't save session")
	}
	c.Redirect(http.StatusSeeOther, a.paths.login)
}

// GetCurrentUser satisfies the Auth interface and returns the current user
func (a auth) GetCurrentUser(c *admin.Context) qor.CurrentUser {
	var userid string

	s, err := a.session.store.Get(c.Request, a.session.name)
	if err != nil {
		return nil
	}
	if v, ok := s.Values[a.session.key]; ok {
		userid = v.(string)
	} else {
		return nil
	}

	var user users_v1.User
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
