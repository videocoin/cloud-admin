package adminpanel

import (
	"net/http"
	"time"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

// GetLogin simply returns the login page
func (a *auth) GetLogin(c *gin.Context) {
	if sessions.Default(c).Get(a.session.key) != nil {
		c.Redirect(http.StatusSeeOther, a.paths.admin)
		return
	}
	c.HTML(http.StatusOK, "login.html", gin.H{})
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
	var u AdminUser
	if a.db.Where(&AdminUser{Email: email}).First(&u).RecordNotFound() {
		c.Redirect(http.StatusSeeOther, a.paths.login)
		return
	}
	if !u.CheckPassword(password) {
		c.Redirect(http.StatusSeeOther, a.paths.login)
		return
	}

	now := time.Now()
	u.LastLogin = &now
	a.db.Save(&u)

	session.Set(a.session.key, u.ID)
	err := session.Save()
	if err != nil {
		logrus.WithError(err).Warn("Couldn't save session")
		c.Redirect(http.StatusSeeOther, a.paths.login)
		return
	}
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
