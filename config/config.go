package config

import (
	"sync"

	"github.com/spf13/viper"
)

// Cfg holds all needed config variables
type Cfg struct {
	SQLURI string
	Secret string
	Port   int
}

var once sync.Once

// FromEnv binds and loads config variables from enviroinment
func FromEnv() *Cfg {
	cfg := new(Cfg)
	viper.SetEnvPrefix("ap")

	once.Do(func() {
		{
			viper.BindEnv("sql_uri")
			viper.BindEnv("secret")
			viper.BindEnv("port")
		}

		{
			cfg.SQLURI = viper.GetString("sql_uri")
			cfg.Secret = viper.GetString("secret")
			cfg.Port = viper.GetInt("port")
		}
	})

	return cfg

}
