# 项目名称
AI桌宠（女友）
## 项目简介
基于python-py实现的live2d桌面AI女友软件，无需任何付费api可与GLM4大模型和kimi聊天互动（这两个模型在不用api的情况下跨语种角色扮演），语音联动GPT-sovits（要安装一下我改版过的补丁包），除外，还有edge-tts语音模式，还可联动CosyVoice语音，不建议看我的源码，代码没有可读性，很乱，嗯~，总之能跑了（CosyVoice部分对标v3ucn的整合包，需要改一下api，之后再添补丁，暂略）



## 安装教程
### 环境
- 操作系统：Windows可运行，其他系统可能不行，核心包live2d-py是用python-win32编译的，可去原项目拉取源码自行编译其他版本，反正我是编译64位总失败，放弃了，直接用编译好的32位了
- 编程语言： Python 3.10.11 32-bit （这个是必须的live2d-py只能用这个）和 python 3.12.4 64-bit（单独封装api部分用的版本，其他版本安转依赖没问题就可以）

### 安装步骤
1. 克隆项目到本地
```
git clone https://github.com/DD-MASTERT/AI-Girlfriend-Desktop-Pet.git
 ```
2. 安装依赖（注意，用 Python 3.10.11 32-bit）
 ```
cd AI-Girlfriend-Desktop-Pet
pip install -r requirements.txt
 ```
3.安装依赖并封装api部分，不想封装为exe的话改main.py里的启动api的按钮绑定的函数为运行py即可，这里python版本依赖支持即可，不用强求Python 3.10.11 32-bit
 ```
cd api
pip install -r requirements.txt
#封装exe的命令太长了就省略了
#注意封装exe时要添加这两个文件site-packages\gradio_client\types.json和site-packages\azure\cognitiveservices\speech\Microsoft.CognitiveServices.Speech.core.dll
#否则会运行报错

 ```
4.下载ffmpeg.exe和ffprobe.exe并添加到环境变量，windows放到项目根目录即可，代码中设置了环境变量，可自行添加

5.下载谷歌浏览器并下载对应版本的ChromeDriver（要代理）添加到环境变量，可以不设置，webdriver_manager会自动下载对应版本，一样要开代理，否则下载基本不成功，而且系统缓存容易被删掉，所以，还是自己下载吧

6.在谷歌浏览器打开智谱清言网页版，勾选自动登录，右键检查或者f12打开开发者菜单，在应用部分找到cookie的chatglm_refresh_token，复制它的值填写到api.json里的TOKEN键即可（长期，过期需要重新登录获取一下），其他部分请运行main.py后自行摸索，UI做的还是很完善的

7.已打包版本的下载链接：[AI桌宠1.0](https://www.123pan.com/s/2sl5jv-n3MJ3.html "AI桌宠1.0")（123网盘）（项目很乱，依赖安装未必成功，我也不确定，所以，不想看代码的，建议直接下载打包好的即可）不建议看，我看了都迷，前前后后改的太多了，参数函数一大堆，想到哪写到哪，我懒得改了，反正我看懂了就好

8.GPT-SOVITS的补丁直接覆盖原项目目录然后运行额外安装依赖的bat即可，bat命令对应的是整合包环境，否则要自行改python解释器为默认命令或者其他路径

9.暂略
