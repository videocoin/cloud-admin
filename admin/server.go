package admin

import (
	"fmt"

	"github.com/gin-gonic/gin"
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/mysql" // import driver for gorm
	"github.com/sirupsen/logrus"
	"github.com/videocoin/adminpanel/config"
	"github.com/videocoin/cloud-admin/admin"
	profiles_v1 "github.com/videocoin/cloud-api/profiles/v1"
	transcoder_v1 "github.com/videocoin/cloud-api/transcoder/v1"
	workorder_v1 "github.com/videocoin/cloud-api/workorder/v1"
	users_v1 "github.com/videocoin/cloud-api/users/v1"
)

// Start starts admin server
func Start() {

	cfg := config.FromEnv()

	db, err := gorm.Open("mysql", cfg.SQLURI)
	if err != nil {
		logrus.Fatal(err)
	}

	db.AutoMigrate(&workorder_v1.WorkOrder{})
	db.AutoMigrate(&transcoder_v1.Transcoder{})
	db.AutoMigrate(&profiles_v1.Profile{})
	db.AutoMigrate(&users_v1.User{})

	// test connection before use
	if err := db.DB().Ping(); err != nil {
		logrus.Fatal(err)
	}

	admin.AdminUserMigration.Migrate(db)

	{
		r := gin.New()
		a := NewAdmin(db, "", cfg.Secret)
		a.Bind(r)
		if err := r.Run(fmt.Sprintf(":%d", cfg.Port)); err != nil {
			a.log.Fatalf("failed to run server: %s", err.Error())
		}
	}
}
