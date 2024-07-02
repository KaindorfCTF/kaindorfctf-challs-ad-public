# FlaGO
## Vulnerabilities

### SQLi
There is an SQL Injection in `GetUser` and `GetNotes`.

### Hardcoded JWT Key
The JWT Key is the same for every app, could be used to forge JWT Tokens.

### JWT Alg None
JWT lets you set Alg to None and can be forged this way.