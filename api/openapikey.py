from openai import OpenAI
import json
import os
import qianfan
import requests
import json
class openaiapi:
    def __init__(self) -> None:
        self.type = None
        self.siliconflow_api_key = None
        self.siliconflow_model = None
        self.client = None
        self.zhipu_apikey = None
        self.zhipu_model = None
        self.tongyi_apikey = None
        self.tongyi_model = None
        self.qianfan_accesskey = None
        self.qianfan_secretkey = None
        self.qianfan_model = None
        self.kimi_key = None
        self.kimi_model = None
        self.minimax_key = None
        self.minimax_model = None
        self.doubao_api = None
        self.doubao_id = None
        self.xf_ak  = None
        self.xf_as = None
        self.xf_model = None
        self.yi_key = None
        self.yi_model = None
        self.messages = []        
    def loadmodel(self):
        # 打开 JSON 文件并读取内容
        with open('api/api_key.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        self.siliconflow_api_key = data['siliconflow_api_key']
        self.siliconflow_model = data['siliconflow_model'] 
        self.zhipu_apikey = data['zhipu_apikey'] 
        self.zhipu_model = data['zhipu_model'] 
        self.tongyi_apikey = data['tongyi_apikey']
        self.tongyi_model = data['tongyi_model'] 
        self.qianfan_accesskey = data['qianfan_accesskey'] 
        self.qianfan_secretkey = data['qianfan_secretkey'] 
        self.qianfan_model = data['qianfan_model'] 
        self.kimi_key = data['kimi_key'] 
        self.kimi_model = data['kimi_model'] 
        self.minimax_key = data['minimax_key'] 
        self.minimax_model = data['minimax_model']  
        self.doubao_api = data['doubao_api'] 
        self.doubao_id = data['doubao_id']
        self.xf_ak= data['xf_ak']
        self.xf_as= data['xf_as']
        self.xf_model= data['xf_model']
        self.yi_key= data['yi_key'] 
        self.yi_model= data['yi_model'] 
        self.type= data['type']                                                                                                                        
        if self.type=="siliconflow":
            self.client = OpenAI(api_key=self.siliconflow_api_key, base_url="https://api.siliconflow.cn/v1")
        elif self.type=='zhipu':
            self.client = OpenAI(api_key=self.zhipu_apikey, base_url="https://open.bigmodel.cn/api/paas/v4/")
        elif self.type=='tongyi':
            self.client = OpenAI(api_key=self.tongyi_apikey, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        elif self.type=='qianfan':
            os.environ["QIANFAN_ACCESS_KEY"] = self.qianfan_accesskey
            os.environ["QIANFAN_SECRET_KEY"] = self.qianfan_secretkey
            self.client = qianfan.ChatCompletion()
        elif self.type=='kimi':
            self.client = OpenAI(api_key=self.kimi_key, base_url="https://api.moonshot.cn/v1")
        elif self.type=='minimax':
            self.client = OpenAI(api_key=self.minimax_key, base_url="https://api.minimax.chat/v1") 
        elif self.type=='doubao':
            pass 
        elif self.type=='xf':
            key = f"{self.xf_ak}:{self.xf_as}"
            self.client = OpenAI(api_key=key, base_url="https://spark-api-open.xf-yun.com/v1") 
        elif self.type=="yi":
            self.client = OpenAI(api_key=self.yi_key, base_url="https://api.lingyiwanwu.com/v1") 
        else:
            pass                 
    def siliconflow_talk(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })  
        response = self.client.chat.completions.create(
            model=self.siliconflow_model,
            messages=self.messages,
            stream=True
        )
        aa = ""
        first_newline_found = False  # 标志位，用于跟踪是否已经找到了第一个换行符

        for chunk in response:  # 假设 response 是一个可迭代对象
            if chunk.choices[0].delta.content is not None:
                if '\n' in chunk.choices[0].delta.content and not first_newline_found:
                    # 如果找到了第一个换行符，将其过滤掉
                    aa += chunk.choices[0].delta.content.replace('\n', '', 1)
                    first_newline_found = True
                else:
                    aa += chunk.choices[0].delta.content
        self.messages.append({
            "role": "assistant",
            "content": aa
        })                    
        return aa 
    
    def zhipu_talk(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })  
        response = self.client.chat.completions.create(
            model=self.zhipu_model,
            messages=self.messages,
            stream=True,
	        top_p=0.7,
            temperature=0.9            
        )
        aa = ""
        for chunk in response:  # 假设 response 是一个可迭代对象
            if chunk.choices and chunk.choices[0].delta.content:
                aa +=chunk.choices[0].delta.content
            else:
                pass
        self.messages.append({
            "role": "assistant",
            "content": aa
        })                    
        return aa 
    def tongyi_talk(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })  
        response = self.client.chat.completions.create(
            model=self.tongyi_model,
            messages=self.messages,
            stream=True,
            temperature=0.8,
            top_p=0.8         
        )
        aa = ""
        for chunk in response:  # 假设 response 是一个可迭代对象
            if chunk.choices and chunk.choices[0].delta.content:
                aa +=chunk.choices[0].delta.content
            else:
                pass
        self.messages.append({
            "role": "assistant",
            "content": aa
        })                    
        return aa 
    
    def qianfan_talk(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })  
        response = self.client.do(model=self.qianfan_model, messages=self.messages, stream=True)
        aa = ""
        for r in response:
            aa += r["body"]['result']
        self.messages.append({
            "role": "assistant",
            "content": aa
        })                    
        return aa 
    
    def kimi_talk(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })  
        response = self.client.chat.completions.create(
            model=self.kimi_model,
            messages=self.messages,
            stream=True,
	        temperature=0.3  
        )
        aa = ""
        for chunk in response:  # 假设 response 是一个可迭代对象
            if chunk.choices and chunk.choices[0].delta.content:
                aa +=chunk.choices[0].delta.content
            else:
                pass
        self.messages.append({
            "role": "assistant",
            "content": aa
        })                    
        return aa 
    
    def minimax_talk(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })  
        response = self.client.chat.completions.create(
            model=self.minimax_model,
            messages=self.messages,
            stream=True 
        )
        aa = ""
        for chunk in response:  # 假设 response 是一个可迭代对象
            if chunk.choices and chunk.choices[0].delta.content:
                aa +=chunk.choices[0].delta.content
            else:
                pass
        self.messages.append({
            "role": "assistant",
            "content": aa
        })                    
        return aa 
    
    def doubao_talk(self, message):
        url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        api_key = self.doubao_api # 替换为你的 API 密钥
        endpoint_id = self.doubao_id  # 替换为你的端点 ID
        self.messages.append({
            "role": "user",
            "content": message
        })  
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        data = {
            "model": endpoint_id,
            "messages":self.messages,
            "stream": True
        }

        response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
        aa = ''
        if response.status_code == 200:
            for chunk in response.iter_lines():
                if chunk:
                    decoded_line = chunk.decode('utf-8').strip()
                    if decoded_line.startswith('data: '):
                        json_line = decoded_line[6:]  # 去掉 'data: ' 前缀
                        if json_line == '[DONE]':
                            break
                        try:
                            json_data = json.loads(json_line)
                            if 'choices' in json_data and json_data['choices']:
                                content = json_data['choices'][0].get('delta', {}).get('content')
                                if content:
                                    aa += content
                        except json.JSONDecodeError:
                            print(f"Failed to decode JSON: {json_line}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

        self.messages.append({
            "role": "assistant",
            "content": aa
        })                    
        return aa 

    def xf_talk(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })  
        response = self.client.chat.completions.create(
            model=self.xf_model,
            messages=self.messages,
            stream=True 
        )
        aa = ""
        for chunk in response:  # 假设 response 是一个可迭代对象
            if chunk.choices and chunk.choices[0].delta.content:
                aa +=chunk.choices[0].delta.content
            else:
                pass
        self.messages.append({
            "role": "assistant",
            "content": aa
        })                    
        return aa 
    def yi_talk(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })  
        response = self.client.chat.completions.create(
            model=self.yi_model,
            messages=self.messages,
            stream=True 
        )
        aa = ""
        for chunk in response:  # 假设 response 是一个可迭代对象
            if chunk.choices and chunk.choices[0].delta.content:
                aa +=chunk.choices[0].delta.content
            else:
                pass
        self.messages.append({
            "role": "assistant",
            "content": aa
        })                    
        return aa                 
    def newtalk(self):
        self.messages = []
    def talk(self,text):
        if self.type=="siliconflow":
            return self.siliconflow_talk(text)
        elif self.type=='zhipu':
            return self.zhipu_talk(text)
        elif self.type=='tongyi':
            return self.tongyi_talk(text)
        elif self.type=='qianfan':
            return self.qianfan_talk(text)
        elif self.type=='kimi':
            return self.kimi_talk(text)
        elif self.type=='minimax':
            return self.minimax_talk(text)
        elif self.type=='doubao':
            return self.doubao_talk(text) 
        elif self.type=='xf':
            return self.xf_talk(text)
        elif self.type=="yi":
            return self.yi_talk(text)
        else:
            pass          
# mod = openaiapi()
# mod.loadmodel() 
# while True:
#     shuru = input()
#     if shuru == '退出':
#         break
#     out = mod.talk(shuru)
#     print(out)
    # print(mod.messages)
