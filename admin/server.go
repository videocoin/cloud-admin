package admin

import (
	"fmt"

	"github.com/VideoCoin/adminpanel/config"
	"github.com/VideoCoin/articles/code/qor/admin"
	"github.com/gin-gonic/gin"
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/mysql" // import driver for gorm
	"github.com/sirupsen/logrus"
)

// Start starts admin server
func Start() {

	cfg := config.FromEnv()

	db, err := gorm.Open("mysql", cfg.SQLURI)
	if err != nil {
		logrus.Fatal(err)
	}

	// test connection before use
	if err := db.DB().Ping(); err != nil {
		logrus.Fatal(err)
	}

	admin.AdminUserMigration.Migrate(db)

	{
		r := gin.New()
		a := admin.New(db, "", cfg.Secret)
		a.Bind(r)
		r.Run(fmt.Sprintf(":%d", cfg.Port))
	}
}
