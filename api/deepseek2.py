import requests
import json

class deepseekv2:
    def __init__(self):
        self.usertoken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzc29faWQiOiJjNTQwYjZhYS1hNDg5LTQ2MGMtYjgxNS0zYjk5MTM5MzdiZWMiLCJlbWFpbCI6IiIsIm1vYmlsZV9udW1iZXIiOiIxNTczNzU2NzUzMiIsImFyZWFfY29kZSI6Iis4NiIsIm1vYmlsZSI6IjE1NzM3NTY3NTMyIiwiZXhwIjoxNzIyMTgyOTE4LCJhdWQiOiI2NTI4YWQzOTZmYWExMzY3ZmVlNmQxNmMifQ.VqCvwp2yRdeXE2YNbcPDovgE4lSN7NBGow3LCmtsBrA"
    def talknext(self,text): 
        try:    
            url = "https://chat.deepseek.com/api/v0/chat/completions"

            headers = {
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Cookie": "",
                "Origin": "https://chat.deepseek.com",
                "Referer": "https://chat.deepseek.com/",
                "accept": "*/*",
                "authorization": f"Bearer {self.usertoken}",
                "content-type": "application/json",
            }

            data = {
                "message": text,
                "stream": True,
                "model_preference": None,
                "model_class": "deepseek_chat",
                "temperature": 0
            }


            # 发送 POST 请求，并启用流式处理
            with requests.post(url, headers=headers, json=data, stream=True) as response:
                response.raise_for_status()  # 确保请求成功

                # 逐块读取响应内容
                for chunk in response.iter_content(chunk_size=1024):  # 可以根据需要调整 chunk_size
                    if chunk:  # 确保 chunk 不为空
                        response_data = chunk.decode('utf-8')

                        # 处理结果，把 content 的结果拼接为一句话打印
                        content_parts = []
                        for line in response_data.splitlines():
                            if line.startswith("data: "):
                                try:
                                    json_data = json.loads(line[6:])
                                    if "choices" in json_data and len(json_data["choices"]) > 0:
                                        delta = json_data["choices"][0]["delta"]
                                        if "content" in delta and delta["content"] is not None:
                                            content_parts.append(delta["content"])
                                            yield "".join(content_parts)  # 逐个产生拼接后的文本
                                except json.JSONDecodeError as e:
                                    print(f"JSON 解析错误: {e}")

        except requests.RequestException as e:
            print(f"请求错误: {e}")
        except Exception as e:
            print(f"其他错误: {e}")

    def newtalk(self):
        try:    
            url = "https://chat.deepseek.com/api/v0/chat/clear_context"

            headers = {
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Cookie": "",
                "Origin": "https://chat.deepseek.com",
                "Referer": "https://chat.deepseek.com/",
                "accept": "*/*",
                "authorization": f"Bearer {self.usertoken}",
                "content-type": "application/json",
            }

            data = {
                "model_class": "deepseek_chat",
                "append_welcome_message": False
            }
            # 发送 POST 请求
            response = requests.post(url, headers=headers, json=data)

            # 确保以 UTF-8 编码解码响应内容
            response_data = response.content.decode('utf-8')

            # 打印解码后的内容
            print(response_data)

        except requests.RequestException as e:
            print(f"请求错误: {e}")
        except Exception as e:
            print(f"其他错误: {e}")

# def loop_function():
#     deep = deepseekv2()
#     i = 1    
#     while True:
#         user_input = input()  # 获取用户输入
#         if user_input == "退出":  # 如果用户输入"退出"，则终止循环
#             print("用户选择退出循环。")
#             break
#         if i==1:
#             deep.newtalk()
#             ere = deep.talknext(user_input)
#             print(ere)
#         else:
#             sfaf = deep.talknext(user_input)
#             print(sfaf)
#         i += 1             
# loop_function()
    