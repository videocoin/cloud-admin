package adminpanel

import (
	"time"

	"github.com/gin-contrib/sessions/cookie"
	"github.com/jinzhu/gorm"
	"github.com/qor/admin"
)

// AdminUser generic user type for accessing adminpanel
type AdminUser struct {
	gorm.Model
	Email     string `gorm:"not null;unique"`
	FirstName string
	LastName  string
	Password  []byte
	LastLogin *time.Time
}

type server struct {
	adm *admin.Admin
	db  *gorm.DB
}

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
