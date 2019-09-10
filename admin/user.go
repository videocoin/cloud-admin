package admin

import (
	"fmt"
	"time"

	"github.com/jinzhu/gorm"
	"github.com/qor/admin"
	"github.com/qor/qor"
	"github.com/qor/qor/resource"
	"github.com/qor/validations"
	users_v1 "github.com/videocoin/cloud-api/users/v1"
	"golang.org/x/crypto/bcrypt"
	gormigrate "gopkg.in/gormigrate.v1"
)

// User defines how an admin user is represented in database
type User struct {
	gorm.Model
	Email     string `gorm:"not null;unique"`
	FirstName string
	LastName  string
	Password  []byte
	LastLogin *time.Time
}

// TableName allows to override the name of the table
func (u User) TableName() string {
	return "users"
}

// DisplayName satisfies the interface for Qor Admin
func (u User) DisplayName() string {
	if u.FirstName != "" && u.LastName != "" {
		return fmt.Sprintf("%s %s", u.FirstName, u.LastName)
	}
	return u.Email
}

// HashPassword is a simple utility function to hash the password sent via API
// before inserting it in database
func (u *User) HashPassword() (err error) {
	pwd, err := bcrypt.GenerateFromPassword(u.Password, bcrypt.DefaultCost)
	if err != nil {
		return
	}
	u.Password = pwd
	return
}

// CheckPassword is a simple utility function to check the password given as raw
// against the user's hashed password
func (u User) CheckPassword(raw string) bool {
	return bcrypt.CompareHashAndPassword(u.Password, []byte(raw)) == nil
}

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
					u := resource.(*User)
					u.Password = pwd
				}
			}
		},
	})
}
