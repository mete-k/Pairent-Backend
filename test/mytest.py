import requests

url = "http://127.0.0.1:5000/questions"

# Construct new question
payload = {
    "title": "test_title",
    "body": "Deneme 1 2 3"
}
headers = {
    "Content-Type": "application/json"
}

# Post question
response = requests.post(url, json=payload, headers=headers)
data = response.json()
print(f"Status Code: {response.status_code}")
print(f"Response Body: {data}")

qid = data["qid"]
print(f"qid: {qid}")

url_qid = url + f"/{qid}"

# Get q
response = requests.get(url_qid)
data = response.json()
print(f"Status Code: {response.status_code}")
print(f"Response Body: {data}")

# Put q
new_title = "new_test_title"
response = requests.put(url_qid, json = {"title": new_title}, headers=headers)
data = response.json()
print(f"Status Code: {response.status_code}")
print(f"Response Body: {data}")

new_body = "Yeni deneme 1 2 3"
response = requests.put(url_qid, json = {"body": new_body}, headers=headers)
data = response.json()
print(f"Status Code: {response.status_code}")
print(f"Response Body: {data}")

new_title = "newer_test_title"
new_body = "baya Yeni deneme 1 2 3"
response = requests.put(url_qid, json = {"title": new_title, "body": new_body}, headers=headers)
data = response.json()
print(f"Status Code: {response.status_code}")
print(f"Response Body: {data}")