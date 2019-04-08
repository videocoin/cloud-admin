package config

import "testing"

func Test_loadConfig(t *testing.T) {
	tests := []struct {
		name string
	}{
		{name: "empty"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			loadConfig()
		})
	}
}
