import urllib.request
import time

# 触发一个不会改变代码的请求来检查服务器是否在运行
try:
    response = urllib.request.urlopen('http://localhost:8000/api/articles/stats', timeout=5)
    print("服务器在运行")
    print(response.read().decode())
except Exception as e:
    print(f"服务器不在运行或无法连接: {e}")
