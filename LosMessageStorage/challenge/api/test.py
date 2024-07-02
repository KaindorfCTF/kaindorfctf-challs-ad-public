import requests

url = "http://localhost:3000"

# Register a user
data = {
    "username": "admin",
    "password": "admin"
}
response = requests.post(url + "/register", json=data)
if response.text == "1":
    print("User already exists")
    assert False
else:
    print("User registered")


# try to register again
response = requests.post(url + "/register", json=data)
if response.text == "1":
    print("User already exists")
else:
    print("User registered")
    assert False


# Login as wrong user
data = {
    "username": "admin",
    "password": "wrong"
}
response = requests.post(url + "/login", json=data)
if response.text == "1":
    print("Wrong password")
else:
    print("Logged in")
    assert False


# Login as correct user
data = {
    "username": "admin",
    "password": "admin"
}
response = requests.post(url + "/login", json=data)
if response.text == "1":
    print("Wrong password")
    assert False
else:
    print("Logged in")


# setmessage for non existent user
data = {
    "username": "nonexistent",
    "message": "test"
}
response = requests.post(url + "/setmessage", json=data)
if response.text == "1":
    print("User does not exist")
else:
    print("Message set")
    assert False


# # too long message or empty
# data = {
#     "username": "admin",
#     "message": "A" * 0x201
# }
# response = requests.post(url + "/setmessage", json=data)
# if response.text == "1":
#     print("Message too long")
# else:
#     print("Message set")
#     assert False


# data = {
#     "username": "admin",
#     "message": ""
# }
# response = requests.post(url + "/setmessage", json=data)
# if response.text == "1":
#     print("Message empty")
# else:
#     print("Message set")
#     assert False


data = {
    "username": "admin",
    "message": "test"
}
response = requests.post(url + "/setmessage", json=data)
if response.text == "1":
    print("User does not exist")
    assert False
else:
    print("Message set")

# get messages of non existent user
data = {
    "username": "nonexistent",
    "isadmin": "False"
}
response = requests.post(url + "/getmessages", json=data)
if response.text == "":
    print("User does not exist")
else:
    print("Messages retrieved")
    assert False


# get messages of admin
data = {
    "username": "admin",
    "isadmin": "True"
}
response = requests.post(url + "/getmessages", json=data)
if response.text == "":
    print("User does not exist")
    assert False
else:
    print("Messages retrieved")
    print(response.text)


# register some random user and set a message
data = {
    "username": "random",
    "password": "random"
}
response = requests.post(url + "/register", json=data)

data = {
    "username": "random",
    "message": "test2"
}
response = requests.post(url + "/setmessage", json=data)

# get all messages via isadmin
data = {
    "username": "admin",
    "isadmin": "True"
}

response = requests.post(url + "/getmessages", json=data)
print(response.text)
assert(len(response.text) > 10)
print("All tests passed!")