package adminpanel

import (
	"fmt"

	"github.com/spf13/viper"
)

// Config Prototypes for config
type Config interface {
	SQLURI() string
}

// Cfg reciver for config
type Cfg struct{}

// SQLURI lookup and return sql uri
func (c Cfg) SQLURI() string {
	return viper.GetString("AP_TEST")
}

func initConfig() {
	viper.SetEnvPrefix("AP_")
	viper.AutomaticEnv()

	fmt.Println()

	var c Config
	c = Cfg{}

	fmt.Println(c.SQLURI())

}
