import requests


url = "http://localhost:8000/predict"

files = [
        {'file': open('./early_blight_1.jpg', 'rb')}, 
        {'file': open('./late_blight_1.jpg', 'rb')}, 
        {'file': open('./healthy.JPG', 'rb')}
    ]


resp = []

for file in files:
    res = requests.post(url, files=file)
    print(res.text + "\n")
    resp.append(res.text)




