package routes

import (
	"errors"
	"fmt"
	"html/template"
	"net/http"
	"time"

	"github.com/golang-jwt/jwt/v5"

	"kdctf/flago/backends"
)

type notes_template_struct struct {
	Notes []string
}

type home_template_struct struct {
	Username string
}

type CustomClaims struct {
	jwt.RegisteredClaims
	Username string `json:"username"`
	UserID   string `json:"user_id"`
}

func _GetUserFromToken(r *http.Request, jwtKey []byte) (string, string, error) {
	c, err := r.Cookie("token")
	if err != nil {
		if errors.Is(err, http.ErrNoCookie) {
			return "", "", err
		}
		return "", "", err
	}

	tknStr := c.Value

	tkn, err := jwt.ParseWithClaims(tknStr, &CustomClaims{}, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return jwt.UnsafeAllowNoneSignatureType, nil
		}
		return jwtKey, nil
	})

	if claims := tkn.Claims.(*CustomClaims); tkn.Valid {
		return claims.UserID, claims.Username, nil
	} else {
		return "", "", fmt.Errorf("invalid token")
	}
}

func PostNote(writer http.ResponseWriter, request *http.Request, db *backends.Postgres, jwtKey []byte) {
	fmt.Println("[PostNote]")
	note := request.FormValue("note")
	password := request.FormValue("password")

	if note == "" || password == "" {
		// invalid credentials
		fmt.Fprint(writer, "invalid credentials")
		return
	}

	user_id, _, _ := _GetUserFromToken(request, jwtKey)
	db.AddNote(note, password, user_id)
	http.Redirect(writer, request, "/", http.StatusSeeOther)
}

func GetNotes(writer http.ResponseWriter, request *http.Request, db *backends.Postgres, jwtKey []byte) {
	fmt.Println("[GetNotes]")
	password := request.URL.Query().Get("password")

	user_id, _, _ := _GetUserFromToken(request, jwtKey)

	var notes []string
	var err error

	if password != "" {
		notes, err = db.GetNotes(password)
	} else {
		notes, err = db.GetNotesByUserID(user_id)
	}

	if err != nil {
		fmt.Println(err)
		return
	}

	var tmplFile = "static/display_flags.html"
	tempalte_data := notes_template_struct{Notes: notes}

	tmpl, err := template.ParseFiles(tmplFile)

	if err != nil {
		fmt.Println(err)
		return
	}

	err = tmpl.Execute(writer, tempalte_data)
	if err != nil {
		fmt.Println(err)
		return
	}
}

func Home(w http.ResponseWriter, r *http.Request, jwtKey []byte) {
	var tmplFile = "static/index.html"

	_, username, err := _GetUserFromToken(r, jwtKey)

	if err != nil {
		fmt.Println(err)
		http.Redirect(w, r, "/login", http.StatusSeeOther)
		return
	}

	tmpl, err := template.ParseFiles(tmplFile)
	template_data := home_template_struct{Username: username}

	if err != nil {
		fmt.Println(err)
		return
	}

	err = tmpl.Execute(w, template_data)
	if err != nil {
		fmt.Println(err)
		return
	}
}

func Register(writer http.ResponseWriter, request *http.Request, db *backends.Postgres) {
	fmt.Println("[AddUser]")
	username := request.FormValue("username")
	password := request.FormValue("password")

	if username == "" || password == "" {
		// invalid credentials
		fmt.Fprint(writer, "invalid credentials")
		return
	}

	err := db.AddUser(username, password)
	if err != nil {
		return
	}
	http.ServeFile(writer, request, "static/login.html")
}

func Login(w http.ResponseWriter, r *http.Request, db *backends.Postgres, jwtKey []byte) {
	// Parse the form data from the request
	err := r.ParseForm()
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	// Extract the username and password from the form data
	username := r.FormValue("username")
	password := r.FormValue("password")

	// Check if the username and password are correct
	if !db.CheckUser(username, password) {
		http.Redirect(w, r, "/login", http.StatusSeeOther)
	}

	id, err := db.GetUser(username)

	if err != nil {
		return
	}

	// Define the expiration time of the token
	expirationTime := time.Now().Add(5 * time.Minute)
	claims := &CustomClaims{RegisteredClaims: jwt.RegisteredClaims{
		ExpiresAt: jwt.NewNumericDate(expirationTime),
		Issuer:    "flago",
	}, Username: username, UserID: id}

	// Create the JWT token
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString(jwtKey)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	// Set the token as a cookie in the response
	http.SetCookie(w, &http.Cookie{
		Name:    "token",
		Value:   tokenString,
		Expires: expirationTime,
	})

	// Redirect the user to the home page
	http.Redirect(w, r, "/", http.StatusSeeOther)
}
