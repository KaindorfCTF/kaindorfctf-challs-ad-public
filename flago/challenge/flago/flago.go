package main

import (
	"errors"
	"fmt"
	"kdctf/flago/backends"
	"kdctf/flago/routes"
	"net/http"

	"github.com/golang-jwt/jwt/v5"
	_ "github.com/lib/pq"
)

type CustomClaims struct {
	jwt.RegisteredClaims
	Username string `json:"username"`
	UserID   string `json:"user_id"`
}

var jwtKey = []byte("my_secret_key") // In a real app, keep this key secret!

func IsAuthenticated(endpoint func(http.ResponseWriter, *http.Request)) http.HandlerFunc {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		c, err := r.Cookie("token")
		if err != nil {
			if errors.Is(err, http.ErrNoCookie) {
				http.Redirect(w, r, "/login", http.StatusSeeOther)
				return
			}
			w.WriteHeader(http.StatusBadRequest)
			return
		}

		tknStr := c.Value
		claims := &CustomClaims{}

		tkn, err := jwt.ParseWithClaims(tknStr, claims, func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return jwt.UnsafeAllowNoneSignatureType, nil
			}
			return jwtKey, nil
		})

		if err != nil {
			if errors.Is(err, jwt.ErrSignatureInvalid) {
				http.Redirect(w, r, "/login", http.StatusSeeOther)
				return
			}
			w.WriteHeader(http.StatusBadRequest)
			return
		}

		if !tkn.Valid {
			http.Redirect(w, r, "/login", http.StatusSeeOther)
			return
		}

		endpoint(w, r)
	})
}

func main() {

	server_addr := ":8080"
	pg_db, _ := backends.InitDatabase()

	http.HandleFunc("GET /favicon.ico", func(w http.ResponseWriter, r *http.Request) {
		fmt.Println("[favicon.ico]")
		http.ServeFile(w, r, "static/favicon_green.ico")
	})
	http.HandleFunc("GET /", IsAuthenticated(func(w http.ResponseWriter, r *http.Request) {
		routes.Home(w, r, jwtKey)
	}))

	http.HandleFunc("GET /login", func(w http.ResponseWriter, r *http.Request) {
		fmt.Println("[login.html]")
		http.ServeFile(w, r, "static/login.html")
	})

	http.HandleFunc("POST /login", func(w http.ResponseWriter, r *http.Request) {
		routes.Login(w, r, pg_db, jwtKey)
	})

	http.HandleFunc("GET /register", func(w http.ResponseWriter, r *http.Request) {
		fmt.Println("[register.html]")
		http.ServeFile(w, r, "static/register.html")
	})

	http.HandleFunc("POST /register", func(w http.ResponseWriter, r *http.Request) {
		routes.Register(w, r, pg_db)
	})

	http.HandleFunc("GET /getNotes", IsAuthenticated(func(w http.ResponseWriter, r *http.Request) {
		routes.GetNotes(w, r, pg_db, jwtKey)
	}))
	http.HandleFunc("POST /addNote", IsAuthenticated(func(w http.ResponseWriter, r *http.Request) {
		routes.PostNote(w, r, pg_db, jwtKey)
	}))

	fmt.Println("Started Server on", server_addr)
	err := http.ListenAndServe(server_addr, nil)
	if err != nil {
		return
	}
}
