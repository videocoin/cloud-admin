package main

import (
	"os"

	admin "github.com/VideoCoin/adminpanel/admin"
	"github.com/gin-gonic/gin"
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/mysql" // import driver for gorm
	"github.com/sirupsen/logrus"
)

func main() {
	db, err := gorm.Open("mysql", os.Getenv("SQL_URI"))
	if err != nil {
		logrus.Fatal(err)
	}

	// test connection before use
	if err := db.DB().Ping(); err != nil {
		logrus.Fatal(err)
	}

	admin.AdminUserMigration.Migrate(db)

	r := gin.New()
	a := admin.New(db, "", "secret")
	a.Bind(r)
	r.Run("127.0.0.1:8080")
}
