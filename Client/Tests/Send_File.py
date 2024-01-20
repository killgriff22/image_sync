import requests
url = "http://192.168.1.237:4385/upload"
files = {'upload_file': open('sample.zip', 'rb')}
values = {'DB': 'photcat', 'OUT': 'csv', 'SHORT': 'short'}

r = requests.post(url, files=files, data=values)
