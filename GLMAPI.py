import requests
from zhipuai import ZhipuAI
from pathlib import Path
import json
import pyautogui
from PIL import Image
class imagesent:
    def __init__(self) -> None:
        self.api_key = None
        self.client = None
        self.text = None
        self.url = None
        self.token = None
        self.file = 'config/123.jpg'
        self.senttext = None
        self.timeout = None
    def creatclient(self):
        with open('config/img.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        self.api_key = config_data['api_key']
        self.text = config_data['text'] 
        self.urltu = config_data['url']
        self.token = config_data['token']
        self.timeout = config_data['timeout']       
        self.client = ZhipuAI(api_key = self.api_key) # 填写您自己的APIKey            
    def talk(self):
        self.client = ZhipuAI(api_key = self.api_key) # 填写您自己的APIKey
        response = self.client.chat.completions.create(
            model="glm-4v",  # 填写需要调用的模型名称
            messages=[
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": self.text
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url" : self.url
                    }
                }
                ]
            }
            ]
        )
        self.senttext = f"({response.choices[0].message.content})"
        # print(response.choices[0].message.content)

    def upload_image(self, permission=1, strategy_id=None, album_id=None, expired_at=None):
        """
        上传本地图片并返回图片的URL链接

        :param api_url: 接口URL，例如：https://picui.cn/api/v1
        :param token: 授权Token，例如：Bearer 1|1bJbwlqBfnggmOMEZqXT5XusaIwqiZjCDs7r1Ob5
        :param file_path: 本地图片文件路径
        :param permission: 权限，1=公开，0=私有
        :param strategy_id: 储存策略ID
        :param album_id: 相册ID
        :param expired_at: 图片过期时间(yyyy-MM-dd HH:mm:ss)
        :return: 图片的URL链接
        """
        url = self.urltu
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
        files = {
            "file": open(self.file, "rb")
        }
        data = {
            "permission": permission,
            "strategy_id": strategy_id,
            "album_id": album_id,
            "expired_at": expired_at
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            response_data = response.json()
            if response_data["status"]:
                self.url = response_data["data"]["links"]["url"]
                # return response_data["data"]["links"]["url"]
            else:
                raise Exception(f"上传失败: {response_data['message']}")
        else:
            raise Exception(f"请求失败，状态码: {response.status_code}, 响应: {response.text}")
    
    def screen_and_save(self,filename='config/123.jpg'):
        # 截取屏幕
        screenshot = pyautogui.screenshot()
        
        # 将截图转换为Pillow图像对象
        image = Image.frombytes(
            'RGB',
            (screenshot.width, screenshot.height),
            screenshot.tobytes()
        )
        
        # 保存图像到文件
        image.save(filename)
        print(f'Screenshot saved as {filename}')   


# token = '397|adC40pkmL2Gu5q1YOfDMaLTRbO9G2UwVa9pycV2y'
# image_path = '123.jpg'
# try:
#     url = upload_image(token,image_path)
#     print(f"图片上传成功，URL: {url}")
# except Exception as e:
#     print(str(e))

# imgup = imagesent()
# imgup.screen_and_save()
# imgup.file = "123.jpg"
# imgup.creatclient()
# imgup.upload_image()
# imgup.talk()
# print(imgup.senttext)


