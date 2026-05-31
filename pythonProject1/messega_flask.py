import requests

def aaa():
    params = {"api_key_user": "123456789", "email": "pavel@mail.ru", "update": "False"}
    get = requests.get("http://127.0.0.1:5000/api/hello", params=params)
    print(get.text)

def bbb():
    params = {"api_key_user": "123456789", "group": "1", "update": "True", "group_access": "1,2,3"}
    get = requests.get("http://127.0.0.1:5000/api/hello", params=params)
    print(get.text)


# aaa()
bbb()