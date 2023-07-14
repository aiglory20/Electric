import json
with open("/home/jiu/Downloads/Electric/openmv/bin/Electric/read.json", 'r', encoding='utf-8') as fp:
    date = json.load(fp)

for i in date:
    print(date[i])

with open('1.json', 'w') as f:
    json.dump(date, f)
