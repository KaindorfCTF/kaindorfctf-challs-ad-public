# TestCenter

## Vulnerabilities

### No Password Check

Password is not checked during login, username is sufficient to log in as admin.

### Direct Object Reference on Profile + guessable UserID

Profile can be accessed by `/profile/<id>` without authentication. User IDs are just incremented, so it's guessable!

### Signup Certificate Signiture Check missing

After uploading the Cert only the data is extracted. No check for the signature is done so you could forge a cert that
gives you an admin user.

### Add a Trusted Key

The endpoint `/api/trustedkeys/<action>/` reachable unauthenticated. Which makes it possible to add your own key pair
to the list of trusted certificates and enables you to generate valid signup certificates.

### Information Disclosure

`/api/users` is a bit to talkative.

### Username=Password?

Developer be dumb so copy/paste and forgot to change `username` to `password` in the parameter field.

### Get Trusted Keys too talkitive
`/api/trustedkeys/get` similar to `/api/users`, it just prints you the private key.