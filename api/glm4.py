import requests
import json

class glm4api:
    def __init__(self):
        self.chatglm_refresh_token = ""
        self.token = None
        self.id = None
        self.assistant_id = ""
    def talknext(self,text):
        # 请求的 URL
        url = "https://chatglm.cn/chatglm/backend-api/assistant/stream"
        # 请求头
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Authorization": f"Bearer {self.token}",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Cookie": f"chatglm_refresh_token={self.chatglm_refresh_token}",
            "Origin": "https://chatglm.cn",
            "Referer": "https://chatglm.cn/main/alltoolsdetail",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "accept": "application/json",
        }

        # 请求数据
        data = {
            "assistant_id": self.assistant_id,
            "conversation_id": self.id,
            "meta_data": {
                "mention_conversation_id": "1",
                "is_test": False,
                "input_question_type": "xxxx",
                "channel": "",
                "draft_id": ""
            },
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                }
            ]
        }

        # 发送请求
        response = requests.post(url, headers=headers, data=json.dumps(data))
        lines = response.text.strip().split('\n')
        # 直接获取最后一行并处理
        last_line = lines[-1]
        if last_line.startswith("data:"):      
            json_str = last_line.split("data:")[1].strip()
            try:
                json_data = json.loads(json_str)
                for part in json_data.get('parts', []):
                    for content in part.get('content', []):
                        if content.get('type') == 'text':
                            print(content.get('text'))
                            return content.get('text')
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return(f"Error decoding JSON: {e}")

    def talknew(self,text='你好'):
        # 请求的 URL
        url = "https://chatglm.cn/chatglm/backend-api/assistant/stream"

        # 请求头
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Authorization": f"Bearer {self.token}",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Cookie": f"chatglm_refresh_token={self.chatglm_refresh_token}",
            "Origin": "https://chatglm.cn",
            "Referer": "https://chatglm.cn/main/alltoolsdetail",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "accept": "application/json",
        }

        # 请求数据
        data = {
            "assistant_id": self.assistant_id,
            "conversation_id": "",
            "meta_data": {
                "mention_conversation_id": "1",
                "is_test": False,
                "input_question_type": "xxxx",
                "channel": "",
                "draft_id": ""
            },
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                }
            ]
        }
        # 发送请求
        response = requests.post(url, headers=headers, data=json.dumps(data))
        lines = response.text.strip().split('\n')
        last_line = lines[-1]
        if last_line.startswith("data:"):
            json_str = last_line.split("data:")[1].strip()
            try:
                json_data = json.loads(json_str)
                conversation_id = json_data.get('conversation_id', 'N/A')  # 获取 conversation_id
                self.id = conversation_id
                print(f"Conversation ID: {conversation_id}")  # 打印 conversation_id

                for part in json_data.get('parts', []):
                    for content in part.get('content', []):
                        if content.get('type') == 'text':
                            print(content.get('text'))  # 打印文本内容
                            return content.get('text')
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
        # return content.get('text')
    def gettoken(self):
        url = "https://chatglm.cn/chatglm/user-api/user/refresh"

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Authorization": f"Bearer {self.chatglm_refresh_token}",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Cookie": f"chatglm_refresh_token={self.chatglm_refresh_token}",
            "Origin": "https://chatglm.cn",
            "Referer": "https://chatglm.cn/main/alltoolsdetail",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }

        response = requests.post(url, headers=headers, json={})

        if response.status_code == 200:
            result = response.json()
            access_token = result.get("result", {}).get("access_token")
            refresh_token0 = result.get("result", {}).get("refresh_token")
            self.token = access_token
            self.chatglm_refresh_token = refresh_token0
            print("Access Token:", self.token)
            print("Refresh Token:", self.chatglm_refresh_token)
        else:
            print("Failed to retrieve data:", response.status_code)
        return  self.chatglm_refresh_token, self.token
    
# def loop_function():
#     glm = glm4api()
#     glm.gettoken()
#     i = 1
#     while True:
#         user_input = input()  # 获取用户输入
#         if user_input == "退出":  # 如果用户输入"退出"，则终止循环
#             print("用户选择退出循环。")
#             break
#         if i == 1:
#             glm.talknew(user_input)        
#         else:
#             glm.talknext(user_input)
#         i += 1  # 增加循环计数   

# # talknew() 
# # gettoken()
# loop_function()        
