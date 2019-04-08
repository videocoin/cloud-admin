package proto

import (
	time "time"

	"github.com/jinzhu/gorm"
)

// BeforeCreate set defaults on create, cannot use directives in proto directly
func (w *WorkOrder) BeforeCreate(scope *gorm.Scope) error {
	err := scope.SetColumn("created_at", time.Now().Unix())
	if err != nil {
		return err
	}
	err = scope.SetColumn("chunks", []byte(`{}`))
	if err != nil {
		return err
	}
	return nil
}

// AfterUpdate update time automatically
func (w *WorkOrder) AfterUpdate(scope *gorm.Scope) error {
	return scope.SetColumn("updated_at", time.Now().Unix())
}

// AfterSave update time automatically
func (w *WorkOrder) AfterSave(scope *gorm.Scope) error {
	return scope.SetColumn("updated_at", time.Now().Unix())
}
