package v1

import "golang.org/x/crypto/bcrypt"

// DisplayName satisfies the interface for Qor Admin
func (u User) DisplayName() string {
	if u.Name != "" {
		return u.Name
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

// TableName allows to override the name of the table
func (u User) TableName() string {
	return "users"
}
