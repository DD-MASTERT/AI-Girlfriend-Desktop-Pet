import requests
from pathlib import Path
import json
import pyautogui
from PIL import Image
class imagesent:
    def __init__(self) -> None:
        self.text = None
        self.senttext = None
        self.timeout = None
    def creatclient(self):
        with open('config/img.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        self.text = config_data['text'] 
        self.timeout = config_data['timeout']                
    def talk(self):
        url = 'http://localhost:2001/run/'
        data = {'message': self.text}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            self.senttext = response.text
            out = f"自动发送的图片识别结果：{response.text}"
            print(out)
        else:
            print('图片识别请求失败', response.status_code)

    def upload_image(self, permission=1, strategy_id=None, album_id=None, expired_at=None):
        pass
    
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


