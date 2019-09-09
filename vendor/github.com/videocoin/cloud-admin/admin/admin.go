package admin

import (
	"html/template"
	"net/http"
	"path/filepath"

	"github.com/gin-contrib/sessions"
	"github.com/gin-contrib/sessions/cookie"
	"github.com/gin-gonic/gin"
	"github.com/jinzhu/gorm"
	"github.com/qor/admin"
	"github.com/sirupsen/logrus"

	"github.com/videocoin/adminpanel/admin/bindatafs"
	"github.com/videocoin/adminpanel/resources"
)

// Admin abstracts the whole QOR Admin + authentication process
type Admin struct {
	db        *gorm.DB
	auth      auth
	adm       *admin.Admin
	adminpath string
	prefix    string
	log       *logrus.Entry
}

// NewAdmin will create a new admin using the provided gorm connection, a prefix
// for the various routes. Prefix can be an empty string. The cookie secret
// will be used to encrypt/decrypt the cookie on the backend side.
func NewAdmin(db *gorm.DB, prefix, cookiesecret string) *Admin {
	adminpath := filepath.Join(prefix, "/admin")
	a := Admin{
		db:        db,
		prefix:    prefix,
		adminpath: adminpath,
		auth: auth{
			db: db,
			paths: pathConfig{
				admin:  adminpath,
				login:  filepath.Join(prefix, "/login"),
				logout: filepath.Join(prefix, "/logout"),
			},
			session: sessionConfig{
				key:   "userid",
				name:  "admsession",
				store: cookie.NewStore([]byte(cookiesecret)),
			},
		},
		log: logrus.WithField("service", "admin"),
	}
	a.adm = admin.New(&admin.AdminConfig{
		SiteName: "Videocoin Admin Panel",
		DB:       db,
		Auth:     a.auth,
		AssetFS:  bindatafs.AssetFS.NameSpace("admin"),
	})

	{
		addUser(a.adm)
		resources.AddTranscoders(a.adm)
		resources.AddProfiles(a.adm)
		resources.AddWorkOrders(a.adm)
		resources.AddUsers(a.adm)
	}

	return &a
}

// Bind login and logout to compiled asssets
func (a Admin) Bind(r *gin.Engine) {
	mux := http.NewServeMux()
	a.adm.MountTo(a.adminpath, mux)

	lfs := bindatafs.AssetFS.NameSpace("login")
	err := lfs.RegisterPath("admin/templates/")
	if err != nil {
		a.log.Fatalf("failed to register path: %s", err.Error())
	}
	logintpl, err := lfs.Asset("login.html")
	if err != nil {
		a.log.Fatalf("failed to set html teplate: %s", err.Error())
	}
	r.SetHTMLTemplate(template.Must(template.New("login.html").Parse(string(logintpl))))

	g := r.Group(a.prefix)
	g.Use(sessions.Sessions(a.auth.session.name, a.auth.session.store))
	{
		g.Any("/admin/*resources", gin.WrapH(mux))
		g.GET("/login", a.auth.GetLogin)
		g.POST("/login", a.auth.PostLogin)
		g.GET("/logout", a.auth.GetLogout)
	}
}
