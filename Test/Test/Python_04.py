import requests
from urllib.parse import urlencode

# 设置请求头
headers = {urlencode({
    'Projects-Name': '测试_00'
})}

print(headers)

# 发送 GET 请求
response = requests.get('http://127.0.0.1:5000/Project-Info', headers=headers)

# 输出响应内容
if response.status_code == 200:
    # 成功请求，输出返回的数据
    print(response.json())
else:
    # 请求失败，输出错误信息
    print(f"请求失败，状态码：{response.status_code}")
    print(response.json())
