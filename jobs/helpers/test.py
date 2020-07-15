import json
file = open("location.json", "r")
x = file.read()
x = json.loads(x)
print(x["wong tai sin"]['latitude'])
file.close()