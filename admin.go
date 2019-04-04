package adminpanel

import (
	"fmt"
	"net/http"
	"time"

	pb "github.com/VideoCoin/common/proto"
	"github.com/sirupsen/logrus"

	"github.com/gin-gonic/gin"
	"github.com/jinzhu/gorm"
	"github.com/qor/admin"
	"github.com/qor/qor"
	"github.com/qor/qor/resource"
	"github.com/qor/validations"
	"golang.org/x/crypto/bcrypt"
	"gopkg.in/gormigrate.v1"
)

// DisplayName satisfies the interface for Qor Admin
func (u AdminUser) DisplayName() string {
	if u.FirstName != "" && u.LastName != "" {
		return fmt.Sprintf("%s %s", u.FirstName, u.LastName)
	}
	return u.Email
}

// HashPassword is a simple utility function to hash the password sent via API
// before inserting it in database
func (u *AdminUser) HashPassword() error {
	pwd, err := bcrypt.GenerateFromPassword(u.Password, bcrypt.DefaultCost)
	if err != nil {
		return err
	}
	u.Password = pwd
	return nil
}

// CheckPassword is a simple utility function to check the password given as raw
// against the user's hashed password
func (u AdminUser) CheckPassword(raw string) bool {
	return bcrypt.CompareHashAndPassword(u.Password, []byte(raw)) == nil
}

var initAdmin = &gormigrate.Migration{
	ID: "init_admin",
	Migrate: func(tx *gorm.DB) error {
		var err error

		type adminUser struct {
			gorm.Model
			Email     string `gorm:"not null;unique"`
			FirstName string
			LastName  string
			Password  []byte
			LastLogin *time.Time
		}

		if err = tx.CreateTable(&adminUser{}).Error; err != nil {
			return err
		}
		var pwd []byte
		if pwd, err = bcrypt.GenerateFromPassword([]byte("changeme"), bcrypt.DefaultCost); err != nil {
			return err
		}
		usr := adminUser{
			Email:    "earl@liveplanet.net",
			Password: pwd,
		}
		return tx.Save(&usr).Error
	},
	Rollback: func(tx *gorm.DB) error {
		return tx.DropTable("admin_users").Error
	},
}

func setupAdmin() {
	db, err := gorm.Open("mysql", "sqluri")
	if err != nil {
		logrus.Fatal(err)
	}

	adm := admin.New(&admin.AdminConfig{SiteName: "Admin", DB: db})

	transcoders := adm.AddResource(pb.Transcoder{})
	profiles := adm.AddResource(pb.Profile{})
	workOrders := adm.AddResource(pb.WorkOrder{})

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

	mux := http.NewServeMux()
	adm.MountTo("/admin", mux)

	r := gin.New()
	r.Any("/admin/*resources", gin.WrapH(mux))
	r.Run("127.0.0.1:8080")

	usr := adm.AddResource(&AdminUser{}, &admin.Config{Menu: []string{"User Management"}})
	usr.IndexAttrs("-Password")
	usr.Meta(&admin.Meta{
		Name: "Password",
		Type: "password",
		Setter: func(resource interface{}, metaValue *resource.MetaValue, context *qor.Context) {
			values := metaValue.Value.([]string)
			if len(values) > 0 {
				if np := values[0]; np != "" {
					pwd, err := bcrypt.GenerateFromPassword([]byte(np), bcrypt.DefaultCost)
					if err != nil {
						context.DB.AddError(validations.NewError(usr, "Password", "Can't encrypt password")) // nolint: gosec,errcheck
						return
					}
					u := resource.(*AdminUser)
					u.Password = pwd
				}
			}
		},
	})
}
