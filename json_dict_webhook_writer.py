import json

data = {}
data["ON"] = "NICE"
data["OFF"] = "TRY"
with open('webhooks_urls.secret', 'w') as f:
    f.write(json.dumps(data))
    f.close()