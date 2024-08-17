# 项目名称
AI桌宠2.2（用网页端用户token白嫖服务器api，支持本地ollama模型聊天）（可用token的模型有glm4，kimi，deepseekv2）（桌面live2d模型2.0和3.0，支持主流国产大模型api对接）（屏幕识别自动发送，语音识别）
## 项目简介
基于live2d-py项目实现的live2d桌面AI女友软件，（可用模型glm4，kimi，deepseekv2）（这三个国产大模型可以稳定回答我的跨语种角色扮演），可语音联动GPT-sovits（要替换安装一下我改过的补丁包，没有大改动，不影响原项目的使用），除外，还有edge-tts语音模式（edge-tts项目）多语言的需要在ui填写自己的api，可联动CosyVoice语音。（CosyVoice部分对标v3ucn大佬的整合包，我微改了他的api.py，用补丁替换原项目即可）



## 安装教程
### 环境
- 操作系统：Windows可运行，其他系统可能不行，核心包live2d-py是用python-win32编译的，可去原项目拉取源码自行编译其他版本，作者提供了编译好的32位
- 编程语言： Python 3.10.11 32-bit （这个是必须的live2d-py只能用这个）和 你的默认解释器（建议3.10以上。我单独封装api部分用的默认解释器是3.10.6，其他版本安转依赖是否成功未知）（依赖是我 手写的，可能有遗漏，未经测试）

### 安装步骤（全部封装为exe使用，避免问题，因为双版本python解释器导致此过程随着代码的复杂而变的过于繁琐。建议直接下载整合包使用，代码只用来参考实现即可）（另，封装用的nuitka我并未写进依赖，请自行安装）
1. 克隆项目到本地
```
git clone https://github.com/DD-MASTERT/AI-Girlfriend-Desktop-Pet.git
 ```
2. main.py安装依赖（注意，此时用 Python 3.10.11 32-bit解释器安装依赖，替换为你的实际路径，main.py是用此32位解释器运行的，原因是live-py的pyd扩展是该解释器编译的，其他版本用不了）（E:\Program Files\python.exe是我Python 3.10.11 32-bit解释器的路径）
 ```
cd AI-Girlfriend-Desktop-Pet
"E:\Program Files\python.exe" -m pip install -r requirements.txt
 ```
封装主程序和live2d辅助程序live2d_model_test
 ```
"E:\Program Files\python.exe" -m nuitka --standalone --onefile --include-module=comtypes.stream --mingw64 --python-flag=-OO --windows-icon-from-ico=a.ico --show-scons --remove-output -j3 --enable-plugin=pyside2 main.py
"E:\Program Files\python.exe" -m nuitka --standalone --onefile --mingw64 --python-flag=-OO --windows-icon-from-ico=1.ico --windows-disable-console --show-scons --remove-output -j3 --enable-plugin=pyside2 live2d_model_test.py
 ``` 
3. 单独安装依赖并封装api部分，python版本依赖支持即可（我这里用的默认python解释器，避免依赖冲突，可以用虚拟环境安装）命令如下。注意--include-data-file的路径替换为你的默认解释器实际路径）
 ```
cd api
pip install -r requirements.txt
nuitka --onefile --mingw64 --standalone --python-flag=-OO --windows-icon-from-ico=a.ico --show-scons --remove-output -j4 --enable-plugin=no-qt --include-data-file="C:\\Program Files\\Python310\\Lib\\site-packages\\gradio_client\\types.json=gradio_client\\types.json" api2.py

 ```
封装test.py为exe（可选，不影响运行）
 ```
nuitka --onefile --mingw64 --standalone --python-flag=-OO --windows-icon-from-ico=a.ico --show-scons --remove-output -j4 --enable-plugin=no-qt test.py
  ```
封装ui.py为API_KEY配置.exe
 ```
nuitka --onefile --mingw64 --standalone --python-flag=-OO --show-scons --plugin-enable=pyside6 --windows-console-mode=disable --remove-output -j3 ui.py
rename ui.exe API_KEY配置.exe
   ```
封装gugeapi.py为exe
 ```
nuitka --onefile --mingw64 --standalone --python-flag=-OO --windows-icon-from-ico=1.ico --show-scons --remove-output -j3 --enable-plugin=no-qt gugeapi.py
   ```
封装autoexe.py为脚本执行器.exe,封装mouse.py为实时鼠标坐标.exe
 ```
cd ../config
nuitka --onefile --mingw64 --standalone --include-module=comtypes.stream --python-flag=-OO --show-scons --remove-output --plugin-enable=pyside6 --windows-console-mode=disable -j3 autoexe.py
rename autoexe.exe 脚本执行器.exe
nuitka --onefile --mingw64 --standalone --python-flag=-OO --show-scons --remove-output --plugin-enable=tk-inter --windows-console-mode=disable -j4 mouse.py
rename mouse.exe 实时鼠标位置.exe
   ```
4. 克隆安装语音识别SenseVoice的分支仓库安装依赖（注意，这里我没下载模型。所以第一次启动会自动下载模型到缓存目录）
 ```
 cd ../
 git clone https://github.com/DD-MASTERT/SenseVoice.git
rename SenseVoice sensvoice
cd sensvoice
pip install -r requirements.txt
 
 ```

5. 下载ffmpeg的压缩包，把bin文件夹放到sensvoice/ffmpeg文件夹中(或自行设置环境变量),修改sensvoice里的api.bat里的"py310/python.exe" web.py命令，替换为你的实际安装解释器的路径，下载特定版本谷歌浏览器和插件的便携版（[123网盘下载链接](https://www.123pan.com/s/2sl5jv-zNMJ3 "123网盘下载链接")），解压后把Chrome文件夹放置到sensvoice文件夹
 ```
 双击启动main.exe。在系统图盘打开配置菜单，参考战2.0视频教程填写配置

  ```

6. （智谱清言cookie获取方法）在任意浏览器打开智谱清言网页版，登录账号，右键检查或者f12打开开发者菜单，在上方工具栏应用部分点开“Cookie”，找到chatglm_refresh_token，复制它的值，在右下角系统托盘找到雷姆图标的ui，右键打开配置，把chatglm_refresh_token的值粘贴到对应位置，然后浏览器开发者菜单切换到网络，请求过滤里选择“Fetch/XHR”,在网页随便发送一句话，找到下面的增加的名称为'stream'的网络请求，点开，在右边切换响应，随便找一句内容在里边找“assistant_id”的值，然后复制到刚刚配置界面的相应位置，最后点击下方的保存全部按钮

7. （kimi和deepseek的cookie）同上，kimi的网页登录后，开发者菜单-应用-本地存储空间-refresh_token，复制这个值，填写到ui保存，同上，deepseek网页登录后，开发者菜单-应用-本地存储空间-userToken，复制这个值，填写到ui保存

8. GPT-SOVITS的补丁直接复制到原项目目录然后选择同名替换，点击运行额外安装依赖的bat即可，bat命令对应的是整合包环境，否则要自行改python解释器为默认命令或者其他解释器路径

9. coysvoice的补丁替换掉整合包里的api.py即可。

10. b站配置教程视频：
[2.0教程视频](https://www.bilibili.com/video/BV1Wxe8eTEfz/?vd_source=8d2d389c5bdd776c8292cc488f7c0506 "2.0教程视频")
[2.1更新说明](https://www.bilibili.com/video/BV18Cv8eUE9y/?spm_id_from=333.788&vd_source=8d2d389c5bdd776c8292cc488f7c0506 "2.1更新说明")
[2.2更新说明](https://www.bilibili.com/video/BV1t8ePeBE2m/?vd_source=8d2d389c5bdd776c8292cc488f7c0506 "2.2更新说明")（暂略）
