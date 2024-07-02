package backends

import (
	"database/sql"
	"fmt"
	_ "github.com/lib/pq"
	"golang.org/x/crypto/bcrypt"
	"os"
	"strconv"
)

type Postgres struct {
	db *sql.DB
}

// HashPassword hashes a password using bcrypt.
func HashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), 14)
	return string(bytes), err
}

func InitDatabase() (*Postgres, error) {
	host := os.Getenv("PG_Host")
	port, err := strconv.Atoi(os.Getenv("PG_Port"))
	user := os.Getenv("PG_User")
	password := os.Getenv("PG_Password")
	dbname := os.Getenv("PG_DB")

	if err != nil {
		fmt.Println("Error parsing DB port")
		os.Exit(1)
	}

	psqlInfo := fmt.Sprintf(
		"host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)
	fmt.Println("Connecting using", psqlInfo)
	db, err := sql.Open("postgres", psqlInfo)
	if err != nil {
		fmt.Println(err)
		return nil, err
	}

	err = db.Ping()
	if err != nil {
		fmt.Println(err)
		return nil, err
	}
	var exists bool

	// Check if the "users" table exists and create it if not
	err = db.QueryRow("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users');").Scan(&exists)
	if err != nil {
		fmt.Println(err)
		return nil, err
	}

	if !exists {
		_, err = db.Exec("CREATE TABLE users (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), username VARCHAR(255) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL);")
		if err != nil {
			fmt.Println(err)
			db.Close()
			return nil, err
		}
	}

	// Check if the table exists and create it if not
	err = db.QueryRow("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'notes');").Scan(&exists)
	if err != nil {
		fmt.Println(err)
		return nil, err
	}

	if !exists {
		_, err = db.Exec("CREATE TABLE notes (id uuid PRIMARY KEY DEFAULT gen_random_uuid(),note VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL, user_id uuid, FOREIGN KEY (user_id) REFERENCES users(id));")
		if err != nil {
			fmt.Println(err)
			db.Close()
			return nil, err
		}
	}

	return &Postgres{db: db}, nil
}

func (pg *Postgres) AddNote(note string, password string, user_id string) error {
	tx, err := pg.db.Begin()

	if err != nil {
		return err
	}

	stmt, err := tx.Prepare("INSERT INTO notes (password, note, user_id) VALUES($1, $2, $3);")

	if err != nil {
		tx.Rollback()
		fmt.Println(err)
		return err
	}
	defer stmt.Close()

	if _, err := stmt.Exec(password, note, user_id); err != nil {
		tx.Rollback()
		fmt.Println(err)
		return err
	}

	return tx.Commit()
}

func (pg *Postgres) GetNotes(password string) ([]string, error) {
	var all_notes []string

	rows, err := pg.db.Query("SELECT note FROM notes WHERE password = '" + password + "'")

	if err != nil {
		fmt.Println(err)
		return nil, err
	}

	for rows.Next() {
		var note string
		err := rows.Scan(&note)
		if err != nil {
			fmt.Println(err)
			return nil, err
		}

		all_notes = append(all_notes, note)
	}

	return all_notes, nil
}

func (pg *Postgres) GetNotesByUserID(user_id string) ([]string, error) {
	var all_notes []string

	rows, err := pg.db.Query("SELECT note FROM notes WHERE user_id = $1", user_id)

	if err != nil {
		return nil, err
	}

	for rows.Next() {
		var note string
		err := rows.Scan(&note)
		if err != nil {
			return nil, err
		}

		all_notes = append(all_notes, note)
	}

	return all_notes, nil
}

func (pg *Postgres) AddUser(username string, password string) error {
	tx, err := pg.db.Begin()

	if err != nil {
		return err
	}

	hashedPassword, err := HashPassword(password)
	if err != nil {
		return err
	}

	stmt, err := tx.Prepare("INSERT INTO users (username, password) VALUES($1, $2);")

	if err != nil {
		tx.Rollback()
		fmt.Println(err)
		return err
	}
	defer stmt.Close()

	if _, err := stmt.Exec(username, hashedPassword); err != nil {
		tx.Rollback()
		fmt.Println(err)
		return err
	}

	return tx.Commit()
}

func (pg *Postgres) GetUser(username string) (string, error) {
	var id string
	var password string

	err := pg.db.QueryRow("SELECT id, password FROM users WHERE username = '"+username+"'").Scan(&id, &password)
	if err != nil {
		return "", err
	}

	return id, nil
}

func (pg *Postgres) CheckUser(username string, password string) bool {
	var hashedPassword string

	// Use prepared statement to prevent SQL injection
	err := pg.db.QueryRow("SELECT password FROM users WHERE username = $1", username).Scan(&hashedPassword)

	err = bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(password))
	if err != nil {
		return false
	}

	return true
}
