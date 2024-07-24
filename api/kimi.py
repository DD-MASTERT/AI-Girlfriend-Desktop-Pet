import requests
import json

class kimiapi:
    def __init__(self):
        self.refresh_token = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ1c2VyLWNlbnRlciIsImV4cCI6MTcyOTI1OTczMSwiaWF0IjoxNzIxNDgzNzMxLCJqdGkiOiJjcWRzM2tyM2Flc2gxbDhsbmJiMCIsInR5cCI6InJlZnJlc2giLCJzdWIiOiJjbzdnZWRzdWR1NmYxcW03Yzk2ZyIsInNwYWNlX2lkIjoiY283Z2Vkc3VkdTZmMXFtN2M5NjAiLCJhYnN0cmFjdF91c2VyX2lkIjoiY283Z2Vkc3VkdTZmMXFtN2M5NWcifQ.NcDdc_DkRN5-Rv8RYHOukKLBNwx39Z3yBK4sXHd-uUpoUIOKcivk7WCF9XfrKBQSkihNB_xE2SCiQz9dR45DIA"
        self.token = None
        self.id = None
    def talknext(self,text):
        url = f"https://kimi.moonshot.cn/api/chat/{self.id}/completion/stream"
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "authorization": f"Bearer {self.token}",
            "content-type": "application/json",
            "cookie": "",
            "origin": "https://kimi.moonshot.cn",
            "priority": "u=1, i",
            "r-timezone": "Asia/Shanghai",
            "referer": f"https://kimi.moonshot.cn/chat/{self.id}"

        }

        data = {
            "messages": [{"role": "user", "content": text}],
            "refs": [],
            "use_search": True,
            "kimiplus_id": "kimi",
            "is_pro_search": False
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()  # 确保请求成功
            response_content = response.content.decode('utf-8')
            data_lines = response_content.strip().split('\n')
            texts = []

            for line in data_lines[1:-1]:  # 跳过首尾行
                try:
                    # 跳过"data:"前缀并解析JSON
                    data_json = json.loads(line[5:])
                    if 'text' in data_json and data_json.get('event') == 'cmpl':
                        texts.append(data_json['text'])
                except (IndexError, json.JSONDecodeError):
                    # 忽略格式不正确的行或解析JSON失败的情况
                    continue

            merged_text = ''.join(texts)
            print(merged_text)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
        return merged_text
        

    def gettoken(self):
        url = "https://kimi.moonshot.cn/api/auth/token/refresh"
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9",
            "authorization": f"Bearer {self.refresh_token}",
            "cookie": "",
            "priority": "u=1, i",
            "referer": "https://kimi.moonshot.cn/"

        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 将捕获非200响应
            self.refresh_token = response.json().get('refresh_token')
            self.token = response.json().get('access_token')
            print("Token retrieval successful.")
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            print(f"OOps: Something Else: {err}")
        except KeyError:
            print("Error: 'refresh_token' or 'access_token' not in response JSON.")
        return self.refresh_token, self.token      

    def getnewtalk(self):
        url = "https://kimi.moonshot.cn/api/chat"

        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "authorization": f"Bearer {self.token}",
            "content-type": "application/json",
            "cookie": "",
            "origin": "https://kimi.moonshot.cn",
            "priority": "u=1, i",
            "r-timezone": "Asia/Shanghai",
            "referer": "https://kimi.moonshot.cn/"
        }

        data = {
            "name": "未命名会话",
            "is_example": False,
            "born_from": "",
            "kimiplus_id": "kimi"
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # 检查响应状态码，确保请求成功
            json_response = response.json()
            if 'id' in json_response:
                self.id = json_response['id']
                print(f"ID: {self.id}")
            else:
                print("Error: 'id' not in response JSON.")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

# def loop_function():
#     kim = kimiapi()
#     kim.gettoken()
#     i = 1    
#     while True:
#         user_input = input()  # 获取用户输入
#         if user_input == "退出":  # 如果用户输入"退出"，则终止循环
#             print("用户选择退出循环。")
#             break
#         if i==1:
#             kim.getnewtalk()
#             kim.talknext(user_input)
#         else:
#             kim.talknext(user_input)
#         i += 1             
# loop_function()
# kim = kimiapi()
# kim.gettoken()