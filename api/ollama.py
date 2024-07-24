import requests
import json
class ollama:
    def __init__(self) -> None:
        self.messages = []
        self.model = None
    def loadmodel(self):
        url = "http://localhost:11434/api/generate"
        data = {
            "model": self.model
        }

        response = requests.post(url, data=json.dumps(data))

        print(response.text)

    def generate_response(self,config_file="api/ollama.json"):
        # Load JSON config
        with open(config_file, 'r', encoding='utf-8') as json_file:
            config = json.load(json_file)
        
        api_url = config["api_url"]
        model = config["model"]
        prompt = config["prompt"]
        options = config["options"]
        
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,  # Assuming stream is always False based on your example
            "options": options
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(api_url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            print(response.text)
            return response.json()
        else:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

    def chat_with_model(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })  
        # 定义API的URL
        url = 'http://localhost:11434/api/chat'
        
        # 构建请求的headers，假设响应和请求都使用application/json
        headers = {
            'Content-Type': 'application/json',
        }
        
        # 构建请求的payload，包含模型名称和消息历史
        payload = {
            "model": self.model,
            "messages": self.messages,
            "stream": False  # 设置为False以禁用流式响应
        }
        
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # 检查请求是否成功
        if response.status_code == 200:
            # 解析响应内容
            response_data = response.json()
            # 获取助理角色的content
            content = response_data['message']['content']
            # 将新的消息添加到聊天记录中
            self.messages.append({
                "role": "assistant",
                "content": content
            })
            print(content)
            return content
        else:
            # 如果响应状态码不是200，打印错误信息
            print(f"Error: {response.status_code}")
            return None
    def newtalk(self):
        self.messages = []

# # 示例用法
# model_name = "qwen:1.8b"


# oll = ollama()
# oll.model = "qwen:1.8b"
# while True:
#     mes = input("请输入:")
#     if mes == "退出":
#        break
#     elif mes == "新建对话":
#        oll.newtalk() 
#     elif mes == "model":
#         oll.loadmodel() 
#     elif mes == "star":
#         oll.generate_response()      
#     else:
#         assistant_response = oll.chat_with_model(mes)
#         print(assistant_response)
#         print(oll.messages)


