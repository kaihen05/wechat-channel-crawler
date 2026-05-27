import urllib.request
import json

response = urllib.request.urlopen('http://localhost:8000/api/articles?limit=1')
data = response.read()
articles = json.loads(data)

article = articles[0]
print("完整文章数据:")
print(json.dumps(article, indent=2, ensure_ascii=False))
