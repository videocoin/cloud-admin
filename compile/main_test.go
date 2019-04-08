package main

import "testing"

func Test_main(t *testing.T) {
	tests := []struct {
		name string
	}{
		{name: "empty"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			main()
		})
	}
}

func Test_detectViewsDir(t *testing.T) {
	type args struct {
		path string
	}
	tests := []struct {
		name  string
		args  args
		want  string
		want1 bool
	}{
		{args: args{"/vendor/"}},
		{want1: false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, got1 := detectViewsDir(tt.args.path)
			if got != tt.want {
				t.Errorf("detectViewsDir() got = %v, want %v", got, tt.want)
			}
			if got1 != tt.want1 {
				t.Errorf("detectViewsDir() got1 = %v, want %v", got1, tt.want1)
			}
		})
	}
}

func Test_detectQORdir(t *testing.T) {
	tests := []struct {
		name  string
		want  string
		want1 bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, got1 := detectQORdir()
			if got != tt.want {
				t.Errorf("detectQORdir() got = %v, want %v", got, tt.want)
			}
			if got1 != tt.want1 {
				t.Errorf("detectQORdir() got1 = %v, want %v", got1, tt.want1)
			}
		})
	}
}
