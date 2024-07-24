# 项目名称
AI桌宠2.0（可语音聊天，摆脱了浏览器环境，直接用cookie白嫖服务器api，支持本地ollama模型聊天）（可用cookie的模型有glm4，kimi，deepseekv2）
## 项目简介
基于python-py实现的live2d桌面AI女友软件，（可用模型glm4，kimi，deepseekv2）（这三个国产大模型可以稳定回答我的跨语种角色扮演），可语音联动GPT-sovits（要替换安装一下我改过的补丁包，没有大改动，不影响原项目的使用），除外，还有edge-tts语音模式（edge-tts项目）多语言的需要在ui填写自己的api，可联动CosyVoice语音。（CosyVoice部分对标v3ucn大佬的整合包，我微改了他的api.py，用补丁替换原项目即可）



## 安装教程
### 环境
- 操作系统：Windows可运行，其他系统可能不行，核心包live2d-py是用python-win32编译的，可去原项目拉取源码自行编译其他版本，作者提供了编译好的32位
- 编程语言： Python 3.10.11 32-bit （这个是必须的live2d-py只能用这个）和 python 3.12.4 64-bit（我单独封装api部分用的版本，其他版本安转依赖是否成功未知）

### 安装步骤
1. 克隆项目到本地
```
git clone https://github.com/DD-MASTERT/AI-Girlfriend-Desktop-Pet.git
 ```
2. 安装依赖（注意，此时用 Python 3.10.11 32-bit解释器安装依赖，替换为你的实际路径）
 ```
cd AI-Girlfriend-Desktop-Pet
"E:\Program Files\python.exe" -m pip install -r requirements.txt
 ```
3. 单独安装依赖并封装api部分，如果不想封装为exe的话修改main.py里的openapiexe函数，位置为648行，封装api部分python版本依赖支持即可，不用强求Python 3.10.11 32-bit，64位速度更快
 ```
cd api
pip install -r requirements.txt
pyinstaller --onefile --icon=a.ico api2.py --add-data="C:\Users\ASUS\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\gradio_client\types.json;gradio_client" --add-data "C:\Users\ASUS\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\azure\cognitiveservices\speech\Microsoft.CognitiveServices.Speech.core.dll;."
#注意封装exe时要添加两个文件site-packages\gradio_client\types.json和site-packages\azure\cognitiveservices\speech\Microsoft.CognitiveServices.Speech.core.dll
#命令中的文件位置替换为你的实际位置
#否则会运行报错

 ```
4. 克隆安装语音识别SenseVoice的分支仓库安装依赖
 ```
 cd ../
 git clone https://github.com/DD-MASTERT/SenseVoice.git
rename SenseVoice sensvoice
cd sensvoice
pip install -r requirements.txt
 
 ```

5. 下载ffmpeg的压缩包，把bin文件夹放到sensvoice/ffmpeg文件夹中(或自行设置环境变量),修改sensvoice里的api.bat里的"py310/python.exe" web.py命令，替换为你的实际安装解释器的路径，然后启动ui，填写配置
 ```
 cd ../
"E:\Program Files\python.exe" main.py
  ```

6. （智谱清言cookie获取方法）在任意浏览器打开智谱清言网页版，登录账号，右键检查或者f12打开开发者菜单，在上方工具栏应用部分点开“Cookie”，找到chatglm_refresh_token，复制它的值，在右下角系统托盘找到雷姆图标的ui，右键打开配置，把chatglm_refresh_token的值粘贴到对应位置，然后浏览器开发者菜单切换到网络，请求过滤里选择“Fetch/XHR”,在网页随便发送一句话，找到下面的增加的名称为'stream'的网络请求，点开，在右边切换响应，随便找一句内容在里边找“assistant_id”的值，然后复制到刚刚配置界面的相应位置，最后点击下方的保存全部按钮

7. （kimi和deepseek的cookie）同上，kimi的网页登录后，开发者菜单-应用-本地存储空间-refresh_token，复制这个值，填写到ui保存，同上，deepseek网页登录后，开发者菜单-应用-本地存储空间-userToken，复制这个值，填写到ui保存

8. GPT-SOVITS的补丁直接复制到原项目目录然后选择同名替换，点击运行额外安装依赖的bat即可，bat命令对应的是整合包环境，否则要自行改python解释器为默认命令或者其他解释器路径

9. coysvoice的补丁替换掉整合包里的api.py即可。

10. 其他使用说明可参考b站视频（暂略）
