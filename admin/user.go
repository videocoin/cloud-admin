package admin

import (
	"github.com/jinzhu/gorm"
	"github.com/qor/admin"
	"github.com/qor/qor"
	"github.com/qor/qor/resource"
	"github.com/qor/validations"
	users_v1 "github.com/videocoin/cloud-api/users/v1"
	"golang.org/x/crypto/bcrypt"
	gormigrate "gopkg.in/gormigrate.v1"
)

// AdminUserMigration is the migration that creates our user model
var AdminUserMigration = &gormigrate.Migration{
	ID: "init_admin",
	Migrate: func(tx *gorm.DB) error {
		var err error

		if err = tx.CreateTable(&users_v1.User{}).Error; err != nil {
			return err
		}
		var pwd []byte
		if pwd, err = bcrypt.GenerateFromPassword([]byte("250c385f50217df5dc558795fc5fd35c"), bcrypt.DefaultCost); err != nil {
			return err
		}
		usr := users_v1.User{
			Email:    "admin@videocoin.net",
			Password: pwd,
		}
		return tx.Save(&usr).Error
	},
	Rollback: func(tx *gorm.DB) error {
		return tx.DropTable("users").Error
	},
}

func addUser(adm *admin.Admin) {
	usr := adm.AddResource(&users_v1.User{}, &admin.Config{Menu: []string{"User Management"}})
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
					u := resource.(*users_v1.User)
					u.Password = pwd
				}
			}
		},
	})
}
