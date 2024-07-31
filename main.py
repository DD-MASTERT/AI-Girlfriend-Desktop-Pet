# my3.py
# 标准库模块
# import ctypes
# # 定义一个函数来隐藏控制台窗口
# def hide_console_window():
#     console_window = ctypes.windll.kernel32.GetConsoleWindow()
#     if console_window != 0:
#         ctypes.windll.user32.ShowWindow(console_window, 0)

import io
import math
import os
import queue
import sys
import threading
import time
import random
import string
import json
import signal
import webbrowser



# 设置 FFMPEG_PATH 环境变量
ffmpeg_path = os.path.join(os.getcwd(), 'sensvoice', 'ffmpeg', 'bin')
os.environ['FFMPEG_PATH'] = ffmpeg_path

# 将 FFMPEG_PATH 临时添加到 PATH 环境变量中
os.environ['PATH'] += os.pathsep + ffmpeg_path


# 第三方库模块
import pygame
import pydub
from pydub.playback import play
from pydub import AudioSegment
import requests
from requests.exceptions import RequestException
from functools import partial
import shutil
import subprocess
from my4 import update_and_copy_folders
import sounddevice as sd
import numpy as np
import soundfile as sf
from GLMAPI import  imagesent




# PySide6 相关模块
from PySide2.QtCore import Signal, QTimer,QObject,Qt,QPoint,QEvent
from PySide2.QtWidgets import QApplication, QHBoxLayout, QPushButton, QLineEdit, QVBoxLayout, QWidget, QStyle, QLabel,QDialog, QComboBox,QSystemTrayIcon, QSlider, QMainWindow,QShortcut
from PySide2.QtGui import QPalette, QPen,QPainter
from PySide2.QtGui import QFont, QColor,QKeySequence
from PySide2.QtGui import QMouseEvent, QCursor,QIcon, QBrush 
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtWidgets import QMenu, QFileDialog,QAction





# live2d_window 项目特定模块
from live2d_window import Win,upmotions,live2dver,check_model_version,starmotion,stopmotion

from live2d_window import live2dv3,live2dv2

# 创建一个线程类
class HiddenWindowThread(threading.Thread):
    def run(self):
        # 在线程执行任何操作之前隐藏窗口
        # hide_console_window()
        super(HiddenWindowThread, self).run()
 
class AudioPlayerThread1(threading.Thread):
    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path  # 存储音频文件路径
        self.stop_event = threading.Event()  # 初始化stop_event

    def run(self):
        starmotion()
        a = float(conf['sleeptime'])
        time.sleep(a)
        # 确保在新线程中初始化pygame mixer
        pygame.mixer.init()
        # 加载音频文件
        pygame.mixer.music.load(self.audio_path)
        # 播放音频
        pygame.mixer.music.play()
        # 等待音频播放结束或停止事件被设置
        while pygame.mixer.music.get_busy() and not self.stop_event.is_set():
            pygame.time.Clock().tick(10)
        time.sleep(0.5)    
        stopmotion()

    def stop(self):
        self.stop_event.set()  # 设置stop_event，请求线程停止

multiples = 0
# audio0 =  r"E:\2\my\GPT-SoVITS-beta0217\moys\temp\audio.wav"
# audio =  r"E:\2\my\GPT-SoVITS-beta0217\moys\temp\audio1.wav"
audio0 =  None
audio =  None
audio1 =  None
outtext = None
live2dlook_state = None
live2dtmotion_state = None
aumotion_state = None
# 定义一个全局变量来存储default值
conf = {}

def gsvpath(config_path = 'api/gsv.json'):
    global audio0,audio,aumotion_state,live2dlook_state,live2dtmotion_state 
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)

    live2dlook_state = not config['live2dlook_state']
    live2dtmotion_state = not config['live2dtmotion_state']
    aumotion_state = not config['aumotion_state']
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        gsvpath = config.get('gsv')  # 使用get方法以避免KeyError
        if gsvpath and os.path.exists(gsvpath):  # 检查gsvpath是否非空并且路径存在
            audio0 = os.path.join(gsvpath, "moys", "temp", "audio.wav")
            audio = os.path.join(gsvpath, "moys", "temp", "audio1.wav")
        else:
            print("配置中未指定有效的'gsv'路径，或路径不存在。")
    except FileNotFoundError:
        print(f"配置文件 {config_path} 未找到。")
    except json.JSONDecodeError:
        print(f"配置文件 {config_path} 格式错误，无法解析JSON。")
    except Exception as e:
        print(f"发生了一个错误：{e}")

def read_config_file_and_save_defaults(file_path ='config/config.json'):
    global conf,live2dver
    """
    读取JSON格式的配置文件并保存所有default值到全局变量。

    :param file_path: 配置文件的路径。
    """
    # 读取配置文件
    with open(file_path, 'r', encoding='utf-8') as file:
        config_data = json.load(file)
    
    # 遍历配置字典，提取每个配置项的default值
    for key, value in config_data.items():
        if "default" in value:
            # 保存default值到全局变量
            conf[key] = value["default"]
    # check_model_version(conf["Live2DModel"])
appwindow = None            


class AudioPlayerThread(threading.Thread):
    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path  # 存储音频文件路径
        self.stop_event = threading.Event()


    def run(self):
        # 确保在新线程中初始化pygame mixer
        pygame.mixer.init()
        # 加载音频文件
        pygame.mixer.music.load(self.audio_path)
        # 播放音频
        pygame.mixer.music.play()
        # 等待音频播放结束或停止事件被设置
        while pygame.mixer.music.get_busy() and not self.stop_event.is_set():
            pygame.time.Clock().tick(10)

  

    def stop(self):
        self.stop_event.set()  # 设置stop_event，请求线程停止

config_file_path = r"config/config.json"
apiid = None
class SettingsDialog(QDialog):
    def __init__(self, model_window: Win):
        super().__init__()
        self.init_ui()
        self.model_window = model_window
        self.server_process = None


    def init_ui(self):
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.api = False
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowTitle('设置菜单')
        main_layout = QHBoxLayout()
        # self.mousePosition = QPoint(0, 0)
        # self.dragging = False
        # self.last_mouse_pos = QPoint()
        self.setWindowIcon(QIcon('ico/1.ico'))

        # self.setStyleSheet("""
        #     /* ... 样式表 ... */
        #     background-color: black; /* 窗口背景颜色 */
        #     border: 1px solid black; /* 窗口边框 */
        #     border-radius: 50px; /* 窗口圆角 */
        # """)

        # 第一行控件的布局
        top_layout = QVBoxLayout()

        top_layout11 = QHBoxLayout()

        top_layout11.addWidget(QLabel('Live2D模型:'))
        self.live2d_model = QComboBox()
        self.live2d_model.addItems(['模型1', '模型2', '模型3'])
        top_layout11.addWidget(self.live2d_model)

        top_layout.addLayout(top_layout11)

    # 保存并更新按钮1
        self.save_and_update3 = QPushButton('更新live2D模型')
        self.save_and_update3.clicked.connect(self.on_save_and_update2)
        top_layout.addWidget(self.save_and_update3)

        top_layout12 = QHBoxLayout()
        top_layout12.addWidget(QLabel('画布大小:'))
        self.character_size = QLineEdit()
        top_layout12.addWidget(self.character_size)
        top_layout.addLayout(top_layout12)

        top_layout30 = QHBoxLayout()
        top_layout30.addWidget(QLabel('帧率(刷新模型生效):'))
        self.fps = QLineEdit()
        top_layout30.addWidget(self.fps)
        # top_layout.addLayout(top_layout30)
        top_layout.addLayout(top_layout30)

        top_layout31 = QHBoxLayout()
        top_layout31.addWidget(QLabel('采样率(重启生效)'))
        self.caiyang = QLineEdit()
        top_layout31.addWidget(self.caiyang)
        top_layout.addLayout(top_layout31)

        top_layout13 = QHBoxLayout()  
        # 气泡停留时长输入框
        self.bubble_duration = QLineEdit()
        top_layout13.addWidget(QLabel('气泡/秒'))
        top_layout13.addWidget(self.bubble_duration)

        self.mouseinterv = QLineEdit()
        top_layout13.addWidget(QLabel('口/毫秒25帧'))
        top_layout13.addWidget(self.mouseinterv)

        top_layout.addLayout(top_layout13)

        top_layout132 = QHBoxLayout()
        top_layout132.addWidget(QLabel('气泡宽度'))
        self.talkkuan = QLineEdit()
        top_layout132.addWidget(self.talkkuan)
        top_layout132.addWidget(QLabel('字体尺寸'))
        self.talksize = QLineEdit()
        top_layout132.addWidget(self.talksize)
        top_layout.addLayout(top_layout132)  

        top_layout133 = QHBoxLayout()
        top_layout133.addWidget(QLabel('语音延迟'))
        self.sleeptime = QLineEdit()
        top_layout133.addWidget(self.sleeptime)
        top_layout133.addWidget(QLabel('视线缩放'))
        self.lookbili = QLineEdit()
        top_layout133.addWidget(self.lookbili)
        top_layout.addLayout(top_layout133)  

        self.live2d = QPushButton('视线追踪/关闭')
        self.live2d.clicked.connect(self.live2dlook)
        top_layout.addWidget(self.live2d)


        top_layout14 = QHBoxLayout()
         # 鼠标穿透下拉菜单
        self.mouse_through = QComboBox()
        self.mouse_through.addItems(['开启', '关闭'])
        top_layout14.addWidget(QLabel('鼠标穿透'))
        top_layout14.addWidget(self.mouse_through)
        top_layout.addLayout(top_layout14)

        top_layout15 = QHBoxLayout()
        self.top = QComboBox()
        self.top.addItems(['开启', '关闭'])
        top_layout15.addWidget(QLabel('窗口置顶'))
        top_layout15.addWidget(self.top)
        top_layout.addLayout(top_layout15)

        top_layout16 = QHBoxLayout()

        # 口型同步幅度输入框
        self.mouth_sync = QLineEdit()
        top_layout16.addWidget(QLabel('口型同步幅度(1到10)'))
        top_layout16.addWidget(self.mouth_sync)
        top_layout.addLayout(top_layout16)

        top_layout33 = QHBoxLayout()
        self.yulan = QPushButton('点击预览动作：')
        self.yulan.clicked.connect(self.yulanm)
        self.yulanmotion = QComboBox()
        self.yulanmotion.addItems(['动作1', '动作2'])
        top_layout33.addWidget(self.yulan)
        top_layout33.addWidget(self.yulanmotion)
        top_layout.addLayout(top_layout33)        

        self.live2d = QPushButton('点击随机动作/关闭')
        self.live2d.clicked.connect(self.livedtmotion)
        top_layout.addWidget(self.live2d)

        # 按钮
        self.aution = QPushButton('自动随机动作/关闭')
        self.aution.clicked.connect(self.aumotion)
        top_layout.addWidget(self.aution)

        top_layout17 = QHBoxLayout()        # 自动播放动作下拉菜单
        self.auto_play_action = QComboBox()
        self.auto_play_action.addItems(['动作1', '动作2'])
        top_layout17.addWidget(QLabel('自动播放随机动作'))
        top_layout17.addWidget(self.auto_play_action)
        top_layout.addLayout(top_layout17)
        # 播放频率输入框
        top_layout18 = QHBoxLayout()         
        self.play_frequency = QLineEdit()
        top_layout18.addWidget(QLabel('播放频率(秒)'))
        top_layout18.addWidget(self.play_frequency)
        top_layout.addLayout(top_layout18)



        # 保存并更新按钮1
        self.save_and_update1 = QPushButton('保存应用(左边部分)')
        self.save_and_update1.clicked.connect(self.on_save_and_update1)
        top_layout.addWidget(self.save_and_update1)






        


        main_layout.addLayout(top_layout)  # 将第一行的布局添加到主布局

        # 第二行控件的布局
        bottom_layout = QVBoxLayout()

        # 保存并更新按钮
        self.openapi = QPushButton('启动api/关闭')
        self.openapi.clicked.connect(self.winapi)
        bottom_layout.addWidget(self.openapi)

        #         # 保存并更新按钮
        # self.closeapi = QPushButton('关闭api')
        # self.closeapi.clicked.connect(self.close_server)
        # bottom_layout.addWidget(self.closeapi)


        bottom_layout21 = QHBoxLayout()
        bottom_layout21.addWidget(QLabel('GSV模型:'))
        self.gsv_model = QComboBox()
        self.gsv_model.addItems(['GSV模型1', 'GSV模型2'])
        bottom_layout21.addWidget(self.gsv_model)
        bottom_layout.addLayout(bottom_layout21)

        # 保存并更新按钮
        self.opengsv = QPushButton('打开gpt-sovits推理窗口')
        self.opengsv.clicked.connect(self.run_bat_file)
        bottom_layout.addWidget(self.opengsv)  
        
        bottom_layout22 = QHBoxLayout()
        bottom_layout22.addWidget(QLabel('预设模版:'))
        self.presets = QComboBox()
        self.presets.addItems(['模版1', '模版2', '模版3'])
        bottom_layout22.addWidget(self.presets)
        bottom_layout.addLayout(bottom_layout22)


        bottom_layout24 = QHBoxLayout()
        # 推理语种下拉菜单
        self.infer_language = QComboBox()
        self.infer_language.addItems(['中文', '英文', '日文'])
        bottom_layout24.addWidget(QLabel('推理语种'))
        bottom_layout24.addWidget(self.infer_language)
        bottom_layout.addLayout(bottom_layout24)

        bottom_layout23 = QHBoxLayout()
        # 停顿输入框
        self.pause = QLineEdit()
        bottom_layout23.addWidget(QLabel('GSV停顿间隔'))
        bottom_layout23.addWidget(self.pause)
        bottom_layout.addLayout(bottom_layout23)


        bottom_layout25 = QHBoxLayout()
        # 翻译下拉菜单
        self.translation = QComboBox()
        self.translation.addItems(['翻译1', '翻译2'])
        bottom_layout25.addWidget(QLabel('翻译'))
        bottom_layout25.addWidget(self.translation)
        bottom_layout.addLayout(bottom_layout25)

        bottom_layout26 = QHBoxLayout()
        # 回复下拉菜单
        self.reply = QComboBox()
        self.reply.addItems(['回复1', '回复2'])
        bottom_layout26.addWidget(QLabel('回复'))
        bottom_layout26.addWidget(self.reply)
        bottom_layout.addLayout(bottom_layout26)


        bottom_layout28 = QHBoxLayout()
        self.cosy = QComboBox()
        self.cosy.addItems(['回复1', '回复2'])
        bottom_layout.addWidget(QLabel('CosyVoice音色'))
        bottom_layout28.addWidget(self.cosy)
        bottom_layout.addLayout(bottom_layout28)
        # bottom_layout.addLayout(bottom_layout28)

        self.upcosy = QPushButton('刷新CosyVoice音色列表')
        self.upcosy.clicked.connect(self.on_upcosy)
        bottom_layout.addWidget(self.upcosy)        

        # bottom_layout28 = QHBoxLayout()
        # api模式下拉菜单
        self.edge = QComboBox()
        self.edge.addItems(['回复1', '回复2'])
        bottom_layout.addWidget(QLabel('微软tts角色名称'))
        bottom_layout.addWidget(self.edge)
        # bottom_layout.addLayout(bottom_layout28)

                # 按钮
        self.edgebioa = QPushButton('打开微软语音参考表,表里有的是免费使用的')
        self.edgebioa.clicked.connect(self.edgebiaoge)
        bottom_layout.addWidget(self.edgebioa)

      
        self.reshdata1 = QPushButton('刷新全部配置')
        self.reshdata1.clicked.connect(self.reshdata)
        bottom_layout.addWidget(self.reshdata1)        

        bottom_layout27 = QHBoxLayout()
        # api模式下拉菜单
        self.talk = QComboBox()
        self.talk.addItems(['回复1', '回复2'])
        bottom_layout.addWidget(QLabel('聊天模式'))
        bottom_layout27.addWidget(self.talk)
        bottom_layout.addLayout(bottom_layout27)
        # 保存并更新按钮
        self.save_and_update = QPushButton('保存应用(右边部分)')
        self.save_and_update.clicked.connect(self.on_save_and_update)
        bottom_layout.addWidget(self.save_and_update)  


        main_layout.addLayout(bottom_layout)  # 将第二行的布局添加到主布局
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setLayout(main_layout)  # 使用QDialog的setLayout方法

        self.lineEdit = QLineEdit()
        self.lineEdit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 设置文本水平居中
        # 设置样式


        self.setStyleSheet("""   
            QWindoww {
                background-color: rgba(0 , 0 , 0, 1);
            }                                                             
            QGroupBox {
                font-family: Microsoft YaHei;
                background-color: rgba(0 , 0 , 0, 1.0);
                font: bold 18px;
                border-radius: 62.5px;           
                margin-top: 30px;
            }
            QPushButton {
                font-family: Microsoft YaHei;
                background-color: rgba(0, 0, 0, 1.0);
                font: bold 18px;
                border: 2px solid black;
                border-radius: 12.5px;
                padding: 8px;
                color: white;
                text-align: center;
                min-width: 10px;
            }
            QPushButton:hover {
                color: black;
                background-color: rgba(255, 255, 255, 1);
            }
            QLineEdit {
                font-family: Microsoft YaHei;
                background-color: rgba(255, 255, 255, 1.0);
                font: bold 18px;
                border-radius: 12.5px;
                padding: 5px;
                color: black;
                max-width: 100px;
            }
            QLineEdit:hover {
                background-color: rgba(0, 0, 0, 1);

                color: white;

            }
            QComboBox {
                font-family: Microsoft YaHei;
                background-color: rgba(255, 255, 255, 1.0);
                font: bold 18px;
                text-align: center;
                border-radius: 12.5px;
                padding: 6px;
                color: black;
                min-width: 4px;
                text-align: center;           
            }
            QComboBox:hover {
                background-color: rgba(0, 0 , 0, 1);
                color: white;           
                           
            }
            QComboBox QAbstractItemView {
                background-color: rgba(0, 0, 0, 1.0);           
                font-family: Microsoft YaHei;
                font: bold 18px;
                background-color: white;
                text-align: center;
                padding: 6px;
                border: none;
                color: black;            
                text-align: center;           
                selection-background-color:black;
                selection-color:white;
            }
            QLabel {
                font-family: Microsoft YaHei;
                font: bold 18px;
                text-align: center;           
                color: black;
                text-align: center;
                /* 其他样式属性 */
            }
        """)


          

        self.load_config(config_file_path)
        self.setLayout(main_layout)
        # 创建QTimer实例
        # self.timer = QTimer(self)
        # # 连接信号和槽
        # self.timer.timeout.connect(self.update_model_gaze_to_cursor)
        # # 启动定时器，例如每100毫秒更新一次
        # self.timer.start(100)

        self.timerapi = QTimer(self)
        self.timerapi.timeout.connect(self.apitest)
        self.conut = 0
        # self.timerapi.start(100)
        self.apire = None
        self.apiretime = QTimer(self)
        self.apiretime.timeout.connect(self.apiret)

    def run_bat_file(self):
        audio_player_thread = AudioPlayerThread('config/tsaudio/audio(9).wav')
        audio_player_thread.start()  
        config_path = 'api/gsv.json'
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
            gsvpath = config.get('gsv')  # 使用get方法以避免KeyError
            if gsvpath and os.path.exists(gsvpath):  # 检查gsvpath是否非空并且路径存在
                bat_file_path = os.path.join(gsvpath, "直接推理.bat")
            else:
                print("配置中未指定有效的'gsv'路径，或路径不存在。")
        except FileNotFoundError:
            print(f"配置文件 {config_path} 未找到。")
        except json.JSONDecodeError:
            print(f"配置文件 {config_path} 格式错误，无法解析JSON。")
        except Exception as e:
            print(f"发生了一个错误：{e}")
        # 获取批处理文件的目录
        # bat_file_path = r"E:/2/GPT-sovits/GPT-SoVITS-beta0706fix1/GPT-SoVITS-beta0706/直接推理.bat"
        bat_file_dir = os.path.dirname(bat_file_path)

        # 在新窗口中运行批处理文件，并设置工作目录
        subprocess.Popen(f'start cmd /K "cd /D {bat_file_dir} && {bat_file_path}"', shell=True)
        # 返回到当前工作目录
        os.chdir(os.getcwd())   

    def yulanm(self):
        motion = self.yulanmotion.currentText()       
        config_file_path = 'config/motion.json'
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        audiopath = config_data[motion]['Sound']        
        self.model_window.yulan(motion,audiopath)
    def loadyulan(self):
        config_file_path = 'config/motion.json'
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        self.yulanmotion.clear()


        for motion_name in config_data.keys():
            # 将每个键名添加到下拉菜单
            self.yulanmotion.addItem(motion_name)

  
            
            
    def on_upcosy(self):

        def up():
            # 发送GET请求到指定的URL
            response = requests.get('http://localhost:9880/speakers_list')
            
            # 确保响应状态码为200（成功）
            if response.status_code == 200:
                # 解析JSON数据
                speakers_list = response.json()
                
                # 假设下拉菜单的名称是self.comboBox
                comboBox = self.cosy  # 你需要根据实际情况替换为正确的变量名
                
                # 清空下拉菜单并添加新的选项
                comboBox.clear()
                comboBox.addItems(speakers_list)  # 假设返回的JSON数据是一个列表
                
                # 如果需要设置默认值，你可以在这里添加逻辑
                # 例如，设置第一个选项为默认值
                if speakers_list:
                    comboBox.setCurrentIndex(0)  # 设置第一个选项为默认值
            else:
                print(f"Failed to retrieve data: {response.status_code}")
        thread = threading.Thread(target=up)
        thread.start() 
    def edgebiaoge(self):
        # 定义 HTML 文件的相对路径
        relative_file_path = 'config/edge.html'
        # 获取当前工作目录
        current_working_directory = os.getcwd()
        # 构建绝对路径
        file_path = os.path.join(current_working_directory, relative_file_path)
        # 转换为适用于 URL 的路径格式
        file_url = 'file://' + '/'.join(file_path.split('\\'))  # 替换为 '/' 以适应 URL 格式
        # 打开默认浏览器并导航到文件 URL
        webbrowser.open(file_url)

    def openapiexe(self):
        audio_player_thread = AudioPlayerThread('config/tsaudio/audio(6).wav')
        audio_player_thread.start()          
        exe_path = 'api/api2.exe'

        # 启动exe应用程序
        subprocess.Popen(exe_path)
    def closeapiexe(self):
        global isimg
        url = "http://localhost:8000/shutdown"
        try:
            response = requests.post(url)
            print(response.status_code)
            print(response.text)
            if response.status_code == 200:
                audio_player_thread = AudioPlayerThread('config/audio5.wav')
                audio_player_thread.start()
                isimg = False
                appwindow.timer4.stop()
                appwindow.cheaktmer4.stop()
                appwindow.oldisimg = False                
            else:
                print("错误")
        except requests.RequestException as e:
            print(f"请求错误: {e}")

    def open_server(self):
        thread = threading.Thread(target=self.openapiexe)
        thread.start()            
        self.apire = False
        self.timerapi.start(400)
        self.apiretime.start(50)
        

    def close_server(self):
        thread = threading.Thread(target=self.closeapiexe)
        thread.start()
        self.timerapi.stop()
        self.apiretime.stop()

         
 

    def winapi(self):
        print("启动或关闭中，请等待直到看到绿色字样出现(除开gpt-sovits语音模式只需要几秒钟)")
    
        global conf
        config_file_path = 'config/config.json'
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        config_data['TALK']['default'] = self.talk.currentText()
        with open(config_file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)

        read_config_file_and_save_defaults()

        config_file_path1 = 'api/api.json'
        with open(config_file_path1, 'r', encoding='utf-8') as f:
            config_data1 = json.load(f)
        if conf['TALK'] == 'GPT-SOVITS语音请求':
            config_data1['GSV'] = True
        else:
            config_data1['GSV'] = False
        with open(config_file_path1, 'w', encoding='utf-8') as f:
            json.dump(config_data1, f, ensure_ascii=False, indent=4)

        if not self.api:
            self.open_server()
            self.api = not self.api
        else:
            self.close_server() 
            self.api = not self.api

    
    def apiret(self):
        global isimg
        if self.apire:
            self.timerapi.stop()
            audio_player_thread = AudioPlayerThread('config/audio3.wav')
            audio_player_thread.start()
            self.apiretime.stop()
            self.conut = 0
            appwindow.cheaktmer4.start(300)
            isimg =True
 

    def apitest(self):
        if not self.apire:
            if self.conut <= 300:
                thread = threading.Thread(target=self.check_api_started)
                thread.start()
                self.conut = self.conut + 1  
            else:
                self.apiretime.stop()
                self.timerapi.stop()
                self.conut = 0 
    def check_api_started(self):
        url = "http://localhost:8000/onlyglm4/"
        text_input = "这是一条测试信息"
        
        # 请求数据
        data = {
            'text': text_input,
            'weiruan': 10
        }
        
        try:
            # 向指定URL发送POST请求
            response = requests.post(url, json=data)
            
            # 检查响应状态码是否为200（成功）
            if response.status_code == 200:
                # 检查响应内容是否包含"api启动成功"
                if "api启动成功" in response.json().get('out', ''):
                    self.apire =  True
                else:
                    self.apire = False
            else:
                self.apire = False
        except requests.RequestException as e:
            # 如果请求过程中发生错误，返回False
            print(f"请求失败：{e}")
            self.apire = False
            
    def save(self, config_path = 'api/gsv.json'):
        global audio0,audio,aumotion_state,live2dlook_state,live2dtmotion_state 
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        config['live2dlook_state'] = live2dlook_state
        config['live2dtmotion_state'] = live2dtmotion_state 
        config['aumotion_state'] = aumotion_state
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(config, file, ensure_ascii=False, indent=4)

    def duault(self):
        global aumotion_state,live2dtmotion_state,live2dlook_state
        aumotion_state = not aumotion_state
        self.model_window.aumotion = aumotion_state        
        motiontime = int(self.model_window.motiontime)
        if aumotion_state:
            self.model_window.motion_timer.start(motiontime*1000)           
        else:
            self.model_window.motion_timer.stop()                
        live2dtmotion_state = not live2dtmotion_state
        self.model_window.tmotion = live2dtmotion_state
        live2dlook_state = not live2dlook_state
        self.model_window.live2dlook = live2dlook_state
        self.save()        
    def aumotion(self):
        global aumotion_state
        aumotion_state = not aumotion_state
        self.model_window.aumotion = aumotion_state
        motiontime = int(self.model_window.motiontime)
        if aumotion_state:
            self.model_window.motion_timer.start(motiontime*1000)
            audio_player_thread = AudioPlayerThread('config/tsaudio/audio(1).wav')
            audio_player_thread.start()            
        else:
            self.model_window.motion_timer.stop() 
            audio_player_thread = AudioPlayerThread('config/tsaudio/audio.wav')
            audio_player_thread.start()               
        self.save()    

    def livedtmotion(self):
        global live2dtmotion_state
        live2dtmotion_state = not live2dtmotion_state
        # 根据状态更新 self.model_window 中的 live2dlook 属性
        self.model_window.tmotion = live2dtmotion_state
        if live2dtmotion_state:
            audio_player_thread = AudioPlayerThread('config/tsaudio/audio(2).wav')
            audio_player_thread.start()   
        else:
            audio_player_thread = AudioPlayerThread('config/tsaudio/audio(3).wav')
            audio_player_thread.start()   
        self.save() 
    def live2dlook(self):
        global live2dlook_state
        # 切换 live2dlook 的状态
        live2dlook_state = not live2dlook_state
        
        # 根据状态更新 self.model_window 中的 live2dlook 属性
        self.model_window.live2dlook = live2dlook_state
        if live2dlook_state:
            audio_player_thread = AudioPlayerThread('config/tsaudio/audio(5).wav')
            audio_player_thread.start()   
        else:
            audio_player_thread = AudioPlayerThread('config/tsaudio/audio(4).wav')
            audio_player_thread.start()   
        self.save() 
    # def update_model_gaze_to_cursor(self):
    #     # 获取当前鼠标的全局位置
    #     cursor_pos = QCursor.pos()
    #     # 将全局位置转换为相对于窗口的位置
    #     local_pos = self.mapFromGlobal(cursor_pos)
    #     # 创建一个假的QMouseEvent对象
    #     mouse_event = QMouseEvent(QEvent.Type.MouseMove, 
    #                               local_pos, 
    #                               Qt.MouseButton.LeftButton, 
    #                               Qt.MouseButton.LeftButton, 
    #                               Qt.KeyboardModifier.NoModifier)
    #      # 将事件发送到事件处理队列
    #     QApplication.postEvent(self, mouse_event)  


    # def mousePressEvent(self, event: QMouseEvent) -> None:
    #     if event.button() == Qt.MouseButton.LeftButton:
    #             self.dragging = True
    #             self.last_mouse_pos = event.globalPosition().toPoint()

    # def mouseMoveEvent(self, event: QMouseEvent) -> None:
    #     if self.dragging:
    #         # Move the window
    #         delta = QPoint(event.globalPosition().toPoint() - self.last_mouse_pos)
    #         self.move(self.x() + delta.x(), self.y() + delta.y())
    #         self.last_mouse_pos = event.globalPosition().toPoint()



    # def mouseReleaseEvent(self, event: QMouseEvent) -> None:
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         self.dragging = False


    def reshdata(self):

        update_config_and_options()
        update_config_with_file_names()
        self.load_config(config_file_path)


    def load_config(self, file_path):
        self.loadyulan()
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 定义一个辅助函数来设置下拉菜单的默认值
        def set_comboBox_defaults(comboBox, config_key):
            options = config_data.get(config_key, {}).get('options', [])
            default = config_data.get(config_key, {}).get('default')
            comboBox.clear()
            comboBox.addItems(options)
            if default:
                comboBox.setCurrentText(default)

        # 设置所有下拉菜单的默认值
        set_comboBox_defaults(self.live2d_model, 'Live2DModel')
        set_comboBox_defaults(self.gsv_model, 'GSVModel')
        set_comboBox_defaults(self.presets, 'Presets')
        set_comboBox_defaults(self.infer_language, 'InferLanguage')
        set_comboBox_defaults(self.translation, 'Translation')
        set_comboBox_defaults(self.reply, 'Reply')
        set_comboBox_defaults(self.talk, 'TALK')
        set_comboBox_defaults(self.edge, 'Edgevoice')
        set_comboBox_defaults(self.auto_play_action, 'AutoPlayAction')
        set_comboBox_defaults(self.cosy, 'cosyvoice')

        # MouseThrough和其他用相同控件的情况应该分别处理
        set_comboBox_defaults(self.mouse_through, 'MouseThrough')
        # 注意：如果'AutoPlayAction'应该使用不同的控件，确保调用set_comboBox_defaults时使用正确的控件和配置键
        set_comboBox_defaults(self.top, 'Top')
        # 对于输入框，直接设置默认值
        self.character_size.setText(config_data.get('CharacterSize', {}).get('default', ''))
        self.fps.setText(config_data.get('FPS', {}).get('default', ''))
        self.caiyang.setText(config_data.get('CAI', {}).get('default', ''))
        self.talkkuan.setText(config_data.get('talkkuan', {}).get('default', '')) 
        self.talksize.setText(config_data.get('talksize', {}).get('default', ''))
        self.sleeptime.setText(config_data.get('sleeptime', {}).get('default', '')) 
        self.lookbili.setText(config_data.get('lookbili', {}).get('default', ''))                             
        self.bubble_duration.setText(config_data.get('BubbleDuration', {}).get('default', ''))
        self.mouseinterv.setText(config_data.get('mouseinter', {}).get('default', ''))        
        self.mouth_sync.setText(config_data.get('MouthSync', {}).get('default', ''))
        self.play_frequency.setText(config_data.get('PlayFrequency', {}).get('default', ''))
        self.pause.setText(config_data.get('Pause', {}).get('default', ''))

        # 打印配置已加载的消息
        print("配置已加载")
    def on_save_and_update(self):
           
        config_file_path = r"config/config.json"
        # 保存设置的逻辑
        # 读取当前控件的值或选择
        current_values = {
            "Live2DModel": self.live2d_model.currentText(),
            "CharacterSize": self.character_size.text(),
            "FPS": self.fps.text(),
            "CAI": self.caiyang.text(),
            "talkkuan": self.talkkuan.text(),
            "talksize": self.talksize.text(),
            "sleeptime": self.sleeptime.text(),
            "lookbili": self.lookbili.text(),                           
            "MouseThrough": self.mouse_through.currentText(),
            "BubbleDuration": self.bubble_duration.text(),
            "mouseinter": self.mouseinterv.text(),
            "MouthSync": self.mouth_sync.text(),
            "AutoPlayAction": self.auto_play_action.currentText(),
            "PlayFrequency": self.play_frequency.text(),
            "GSVModel": self.gsv_model.currentText(),
            "Presets": self.presets.currentText(),
            "InferLanguage": self.infer_language.currentText(),
            "Pause": self.pause.text(),
            "Translation": self.translation.currentText(),
            "Reply": self.reply.currentText(),
            "TALK": self.talk.currentText(),
            "Edgevoice": self.edge.currentText(),
            "cosyvoice": self.cosy.currentText()                       
        }

        # 读取现有的配置文件
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，初始化一个新的配置字典
            config_data = {key: {"options": [], "default": value} for key, value in current_values.items()}
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            return

        # 更新配置文件中的"default"值
        for key, value in current_values.items():
            if key in config_data:
                # 仅更新"default"值，保留原有的"options"列表
                config_data[key]['default'] = value
            else:
                # 如果配置项不存在，添加新的配置项（这种情况在本次更新中应该不会发生）
                config_data[key] = {"options": [value], "default": value}

        # 将更新后的配置写回文件
        try:
            with open(config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            print("配置已更新并保存到:", config_file_path)
        except IOError as e:
            print(f"保存配置时发生错误: {e}")
        self.update_config_from_file()
        read_config_file_and_save_defaults()

    def on_save_and_update1(self):
        global conf
           
        config_file_path = r"config/config.json"
        # 保存设置的逻辑
        # 读取当前控件的值或选择
        current_values = {
            "Live2DModel": self.live2d_model.currentText(),
            "CharacterSize": self.character_size.text(),
            "FPS": self.fps.text(),
            "CAI": self.caiyang.text(),
            "talkkuan": self.talkkuan.text(),
            "talksize": self.talksize.text(), 
            "sleeptime": self.sleeptime.text(),
            "lookbili": self.lookbili.text(),                       
            "MouseThrough": self.mouse_through.currentText(),
            "Top": self.top.currentText(),
            "BubbleDuration": self.bubble_duration.text(),
            "mouseinter": self.mouseinterv.text(),
            "MouthSync": self.mouth_sync.text(),
            "AutoPlayAction": self.auto_play_action.currentText(),
            "PlayFrequency": self.play_frequency.text(),
            "GSVModel": self.gsv_model.currentText(),
            "Presets": self.presets.currentText(),
            "InferLanguage": self.infer_language.currentText(),
            "Pause": self.pause.text(),
            "Translation": self.translation.currentText(),
            "Reply": self.reply.currentText(),
            "TALK": self.talk.currentText(),
            "Edgevoice": self.edge.currentText(),
            "cosyvoice": self.cosy.currentText()  
        }

        # 读取现有的配置文件
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，初始化一个新的配置字典
            config_data = {key: {"options": [], "default": value} for key, value in current_values.items()}
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            return

        # 更新配置文件中的"default"值
        for key, value in current_values.items():
            if key in config_data:
                # 仅更新"default"值，保留原有的"options"列表
                config_data[key]['default'] = value
            else:
                # 如果配置项不存在，添加新的配置项（这种情况在本次更新中应该不会发生）
                config_data[key] = {"options": [value], "default": value}

        # 将更新后的配置写回文件
        try:
            with open(config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            print("配置已更新并保存到:", config_file_path)
            audio_path = r"config/audio.wav"
        except IOError as e:
            print(f"保存配置时发生错误: {e}")
            audio_path = r"config/audio2.wav"
            # 检查响应并处理

        # 创建并启动播放音频的线程
        audio_player = AudioPlayerThread(audio_path)
        audio_player.start()
        read_config_file_and_save_defaults()
        # if current_values["Live2DModel"] != config_data["Live2DModel"]['default']:

        self.modelwindow()
        mou = conf["MouthSync"]
        mou = int(mou)
        motionname = conf["AutoPlayAction"]
        motiontime = conf["PlayFrequency"]
        lasttime = conf["BubbleDuration"]
        top = conf["Top"]
        left = conf["MouseThrough"]
        fps = int(conf["FPS"])
        caiyang = int (conf["CAI"])       
        talkkuan = conf["talkkuan"]
        talksize = conf["talksize"]
        lookbili = conf["lookbili"]
        mouseinter = conf["mouseinter"] 
        self.model_window.updata(motiontime,mou,motionname,lasttime,fps,caiyang,talkkuan,talksize,lookbili,mouseinter)
        self.model_window.uptop(top,left)

    # def talkset(self):
    #     global onlytalk
    #     if conf["TALK"]=='GPT-SOVITS语音请求':
    #         onlytalk = False
    #     else:
    #         onlytalk = True
    def on_save_and_update2(self): 
        global conf

        size_str = self.live2d_model.currentText()
        # size_str = conf["Live2DModel"]
        size_str1 = self.character_size.text()


        # size_str1 = conf["CharacterSize"]
        width, height = size_str1.split()  # 使用split默认以空格分割
        width = int(width)
        height = int(height)  

        self.on_save_and_update1()
        update_config_and_options()
        update_config_with_file_names()
        self.load_config(config_file_path)
        read_config_file_and_save_defaults()
        # if current_values["Live2DModel"] != config_data["Live2DModel"]['default']:
        self.modelwindow()
        mou = conf["MouthSync"]
        mou = int(mou)
        motionname = conf["AutoPlayAction"]
        motiontime = conf["PlayFrequency"]
        lasttime = conf["BubbleDuration"]
        top = conf["Top"]
        left = conf["MouseThrough"]
        fps = conf["FPS"]
        caiyang = conf["CAI"]
        talkkuan = conf["talkkuan"]
        talksize = conf["talksize"]
        lookbili = conf["lookbili"] 
        mouseinter = conf["mouseinter"]         
        self.model_window.reload_model(size_str, width, height)
        self.model_window.updata(motiontime,mou,motionname,lasttime,fps,caiyang,talkkuan,talksize,lookbili,mouseinter)
        self.model_window.uptop(top,left)
        self.loadyulan()
        upmotions()
        self.load_config(config_file_path)
        self.model_window.load_motion_config()
        self.model_window.audomotion(first=True)
        self.model_window.update()     


    def modelwindow(self):
        global conf
        size_str = conf["CharacterSize"]
        width, height = size_str.split()  # 使用split默认以空格分割
        width = int(width)
        height = int(height)
        self.model_window.widnowsize(width,height)

      
    def update_config_from_file(self):
        # 这是线程的目标函数
        def thread_target(config_file_path, api_url):
            with open(config_file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # 从配置文件中读取特定的默认值
            gsv_model = config_data.get('GSVModel', {}).get('default', '')
            presets = config_data.get('Presets', {}).get('default', '')
            infer_language = config_data.get('InferLanguage', {}).get('default', '')
            translation = config_data.get('Translation', {}).get('default', '')
            pause = config_data.get('Pause', {}).get('default', '0')  # 确保pause有一个默认值用于转换
            reply = config_data.get('Reply', {}).get('default', '')
            talk = config_data.get('TALK', {}).get('default', '')
            Edgevoice = config_data.get('Edgevoice', {}).get('default', '')
            Vosyspeaker = config_data.get('cosyvoice', {}).get('default', '')
            print(Edgevoice)
            if talk =='GPT-SOVITS语音请求':
                gsv = True
            else:
                gsv = False

            # 准备发送的数据
            data = {
                "TTS": gsv_model,          # 假设GSVModel的display name是TTS
                "MB": presets,            # 假设Presets的display name是MB
                "Text_language": infer_language,
                "Interval": float(pause),  # 确保pause转换为浮点数
                "R": translation,         # 假设Translation的display name是R
                "T": reply,
                "GSV": gsv,
                "Edgevoive": Edgevoice,
                "Vosyspeaker":Vosyspeaker                            
            }

            # 发送POST请求到后端API
            response = requests.post(api_url, json=data)

            # 检查响应并处理
            if response.ok:
                print('配置更新成功:', response.json())
                audio_path = r"config/audio.wav"
            else:
                print('更新配置失败，响应码:', response.status_code)
                print('错误信息:', response.text)
                audio_path = r"config/audio2.wav"

            # 创建并启动播放音频的线程
            audio_player = AudioPlayerThread(audio_path)
            audio_player.start()

        # 配置文件路径和API URL
        config_file_path = r"config/config.json"
        api_url = 'http://localhost:8000/update_config/'

        # 创建线程对象
        thread = threading.Thread(target=thread_target, args=(config_file_path, api_url))

        # 启动线程
        thread.start()



    def open_settings(self):
        self.open()  # 这将创建一个模态的非阻塞对话框

    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     painter.begin(self)  # 开始绘制
        
    #     # 设置外边距为50px
    #     margin = 50
        
    #     # 使用Qt.GlobalColor设置带有透明度的黑色背景
    #     background_brush = QBrush(QColor(0, 0, 0, 170))  # 黑色背景
    #     painter.setBrush(background_brush)
        
    #     # 设置笔为透明，这样就不会有边框绘制出来
    #     painter.setPen(QPen(Qt.transparent))
        
        
    #     painter.end()  # 结束绘制


isimg = None
openisimg = False
class AppWindow(QWidget):
    updated = Signal()
    timeout = None


    def __init__(self, model_window: Win ,set: SettingsDialog):
        super().__init__()
        self.model_window = model_window
        self.set = set

        self.init_ui()
        self.setWindowTitle('聊天框')
        self.setWindowIcon(QIcon('ico/1.jpg'))
        self.dragging = False
        self.last_mouse_pos = QPoint(0, 0)
        self.trigger_count = multiples  # 初始化计数器，总共触发5次
        self.timer = QTimer(self)  # 创建一个 QTimer 实例
        self.timer2 = QTimer(self)
        self.timer.timeout.connect(self.on_timeout) 
        self.timer2.timeout.connect(self.on_timeout2) # 连接信号和槽
        self.audtime_queue = queue.Queue()  # 创建一个线程安全的队列来存储
        self.audtime_event = threading.Event()  # 创建一个事件对象
        self.updated.connect(self.update_ui_slot)
        # self.model_window.widnowsize(800,800)
        # self.model_window.load_new_model("ATRI")
                # 创建QTimer实例
        self.timer3 = QTimer(self)
        # 连接信号和槽
        self.timer3.timeout.connect(self.update_model_gaze_to_cursor)
        # 启动定时器，例如每100毫秒更新一次
        self.timer3.start(100)
        self.imagesent = imagesent()
        self.imagesent.creatclient()
        self.timer4 = QTimer(self)
        self.timer4.timeout.connect(self.imgsent)
        self.cheaktmer4 = QTimer(self)
        self.cheaktmer4.timeout.connect(self.cheakimg)
        self.oldisimg = isimg
        # self.timer4.start(self.imagesent.timeout)          



    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        # self.mousePosition = QPoint(0, 0)  # 初始化鼠标位置

        # self.last_mouse_pos = QPoint()
        self.resize(450 , 190)

        self.layout = QHBoxLayout()  # 或者 QHBoxLayout(), 取决于您的需求

  
        self.buttontalk = QPushButton("讲话")
        self.buttontalk.setCheckable(True)  # 设置按钮为可选中状态
        self.buttontalk.setChecked(False)   # 默认不选中
        self.buttontalk.clicked.connect(self.saytalk)
    
        # 设置按钮样式
        self.buttontalk.setStyleSheet("""
            QPushButton {
                font-family: WenQuanYi Zen Hei; /* 字体 */
                background-color: rgba(0, 0, 0, 0.01); /* 背景颜色和透明度 */
                font: bold 20px; /* 字体大小和粗细 */
                border-radius: 10px; /* 边框圆角 */
                padding: 13px; /* 内边距 */
                color: rgba(255, 255, 255, 0.01); /* 文本颜色 */
                text-align: center; /* 文本对齐方式 */
                width: 37.5px; /* 按钮宽度 */
                height: 30px;                      
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.7); /* 选中时的背景颜色和透明度 */
                color: black; /* 文本颜色 */
                /* 其他选中时的样式属性 */
            }
            QPushButton:Checked {
                background-color: rgba(0, 0, 0, 1.0); /* 选中时的背景颜色和透明度 */
                color: white; /* 文本颜色 */
                /* 其他选中时的样式属性 */
            }                                      
        """)


        # 创建发送按钮
        self.button = QPushButton("发送")
        # self.button.setCheckable(True)  # 设置按钮为可选中状态
        # self.button.setChecked(False)   # 默认不选中

        # 设置按钮样式
        self.button.setStyleSheet("""
            QPushButton {
                font-family: WenQuanYi Zen Hei; /* 字体 */
                background-color: rgba(0, 0, 0, 0.7); /* 背景颜色和透明度 */
                font: bold 20px; /* 字体大小和粗细 */
                border-radius: 10px; /* 边框圆角 */
                padding: 13px; /* 内边距 */
                color: white; /* 文本颜色 */
                text-align: center; /* 文本对齐方式 */
                width: 37.5px; /* 按钮宽度 */
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.7); /* 选中时的背景颜色和透明度 */
                color: black; /* 文本颜色 */
                /* 其他选中时的样式属性 */
            }
        """)
        #self.button.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        # 创建输入框
        self.input_box = QLineEdit()
        self.input_box.setStyleSheet("QLineEdit { font-family: WenQuanYi Zen Hei;background-color: rgba(255, 255, 255, 0.9);font: bold 20px;border-radius: 10px; padding: 12.5px;color: black;text-align: center;width:300px }")
        self.input_box.setPlaceholderText("'发送预设，'发送模版内容，'新建对话'重新开始对话")
        # 将输入框和按钮添加到布局中
        self.layout.addWidget(self.buttontalk)       
        self.layout.addWidget(self.input_box)
        self.layout.addWidget(self.button)

        # 连接输入框的 textChanged 信号到一个槽函数，用于获取输入内容
        self.input_box.textChanged.connect(self.update_input)

        # 连接按钮的 clicked 信号到发送函数
        self.button.clicked.connect(self.send_input)

        self.buttontalkkey = QShortcut(QKeySequence("Up"), self)
        self.buttontalkkey.activated.connect(self.buttontalk.click)  

        # 创建一个快捷键，绑定回车键到按钮的点击事件
        self.return_shortcut = QShortcut(QKeySequence("Return"), self)
        self.return_shortcut.activated.connect(self.button.click)
        # 添加设置按钮
        self.settings_button = QPushButton("设置")
        #self.settings_button.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        self.settings_button.clicked.connect(self.open_settings)
        self.settings_button.setCheckable(True)  # 设置按钮为可选中状态
        self.settings_button.setChecked(False)   # 默认不选中

        # 设置按钮样式
        self.settings_button.setStyleSheet("""
            QPushButton {
                font-family: WenQuanYi Zen Hei; /* 字体 */
                background-color: rgba(0, 0, 0, 0.7); /* 背景颜色和透明度 */
                font: bold 20px; /* 字体大小和粗细 */
                border-radius: 10px; /* 边框圆角 */
                padding: 12.5px; /* 内边距 */
                color: white; /* 文本颜色 */
                text-align: center; /* 文本对齐方式 */
                width: 37.5px; /* 按钮宽度 */
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.7); /* 选中时的背景颜色和透明度 */
                color: black; /* 文本颜色 */
                /* 其他选中时的样式属性 */
            }
        """)
  
        # # 添加按钮
        # self.movewindow_button = QPushButton("移动")
        # self.movewindow_button.setCheckable(True)
        # self.movewindow_button.setChecked(False)
        # self.movewindow_button.clicked.connect(self.movewindow1)



        self.layout.addWidget(self.settings_button)
        self.label = QLabel("拖动")
        self.label.setObjectName("myLabel")
        self.label.setStyleSheet("""
            #myLabel {
                font-family: WenQuanYi Zen Hei; /* 字体 */
                background-color: rgba(0, 0, 0, 0); /* 背景颜色和透明度 */
                font: bold 50px; /* 字体大小和粗细 */
                border-radius: 10px; /* 边框圆角 */
                padding: 0px; /* 内边距 */
                color: rgba(0, 0, 0, 0.1); /* 文本颜色 */
                text-align: center; /* 文本对齐方式 */
                width: 37.5px; /* 按钮宽度 */
                height: 100px; /* 按钮宽度 */
            }
            #myLabel:hover {
                background-color: rgba(255, 255, 255, 1); /* 选中时的背景颜色和透明度 */
                color: black; /* 文本颜色 */
                /* 其他选中时的样式属性 */
            }
        """)
        self.layout.addWidget(self.label)  # 确保添加的是设置了样式的label
        # self.layout.addWidget(self.movewindow_button)

        # 设置窗口的布局
        self.setLayout( self.layout)


    def cheakimg(self):
        global isimg
        if isimg!=self.oldisimg:
            if not isimg:
                self.timer4.stop()
            else:
                self.timer4.start(self.imagesent.timeout)    
        self.oldisimg = isimg        
    def imgsent(self):
        global isimg
        if openisimg:
            isimg = False
            def a():
                appwindow.imagesent.screen_and_save()
                appwindow.imagesent.upload_image()
                appwindow.imagesent.talk()
                appwindow.send_text_to_server(appwindow.imagesent.senttext, appwindow.callback)
            th = threading.Thread(target=a)
            th.start()            
        # self.timer4.stop()    
    def saytalk(self):
        def star():
            output_folder = 'sensvoice/recorded_audios'
            filename = "audio.wav"
            filename1 = "audio1.wav"            
            sample_rate = 44100
            audio_data = []
            
            def callback(indata, frames, time, status):
                """这是录音的回调函数"""
                if status:
                    print(status)
                audio_data.append(indata.copy())
            
            stream = sd.InputStream(samplerate=sample_rate, channels=2, callback=callback)
            
            # 检查按钮是否被选中
            if self.buttontalk.isChecked():
                print("开始录音...")
               
                with stream:
                    while self.buttontalk.isChecked():  # 保持录音直到按钮未选中
                        pass  # 循环等待，直到按钮状态改变
                print("录音结束。")
                
                audio_data = np.concatenate(audio_data, axis=0)
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                
                # 保存音频数据到指定文件
                output_path = os.path.join(output_folder, filename)
                output_path1 = os.path.join(output_folder, filename1)                
                sf.write(output_path, audio_data, sample_rate)
                sf.write(output_path1, audio_data, sample_rate)
                print(f"音频已保存到 {output_path}")
                url = "http://localhost:1111/run/"
                response = requests.post(url)
                print(response.status_code)
                print(response)
                # self.input_box.setText(response.text)
                self.send_text_to_server(response.text, self.callback)

            else:
                print('录音未开始')
        starth = threading.Thread(target=star) 
        starth.start() 

    def uppos(self):
        global x, y
        current_pos = self.pos()
        y = current_pos.y()
        x = current_pos.x()
        write_position_to_file()

    def update_model_gaze_to_cursor(self):
        # 获取当前鼠标的全局位置
        cursor_pos = QCursor.pos()
        # 将全局位置转换为相对于窗口的位置
        local_pos = self.mapFromGlobal(cursor_pos)
        # 创建一个假的QMouseEvent对象
        mouse_event = QMouseEvent(QEvent.Type.MouseMove, 
                                  local_pos, 
                                  Qt.MouseButton.LeftButton, 
                                  Qt.MouseButton.LeftButton, 
                                  Qt.KeyboardModifier.NoModifier)
         # 将事件发送到事件处理队列
        QApplication.postEvent(self, mouse_event)  


    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
                self.dragging = True
                self.last_mouse_pos = event.globalPos()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.dragging:
            # Move the window
            delta = QPoint(event.globalPos() - self.last_mouse_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.last_mouse_pos = event.globalPos()


    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.uppos()



    def open_settings(self):


        # 根据 QAction 的选中状态来显示或隐藏窗口
        if self.set.isVisible():
            self.set.close()
        else:
            self.set.open_settings()
  

    def update_input(self, text):
        # 这个槽函数会在输入框内容变化时被调用
        # 你可以在这里处理获取到的输入内容
        print("Input updated:", text)

    def send_input(self):

        # 这个槽函数会在按钮被点击时被调用
        # 发送 input_box 的当前输入内容
        current_input = self.input_box.text()
        print("Sending input:", current_input)
        self.send_text_to_server(current_input, self.callback)
        self.input_box.clear()  # 清空输入框内容

    def start_mouth_motions(self, last):
        global multiples
        multiples = last // 680
        multiples = multiples - 1
        self.model_window.mouth()        
        if not self.timer.isActive():  # 如果定时器未激活，则开始
            self.trigger_count = multiples  # 重置计数器
            self.timer.start(680)  # 设置定时器超时时间为 1000 毫秒（1秒）

        if not self.timer2.isActive(): 
            if last >= 1500:
                self.timer2.start(last-1500)
            else:
                print("这句话小于1500毫秒")

    def start_mouth_motions0 (self): 
        global audio1, outtext    
        self.model_window.mouth()
        # if conf["TALK"]=='微软语音':
        #     audio_path = 'api/edge/audio.mp3'
        # else:             
        audio_path = audio1
        if outtext == '开始新对话了':
            audio_path = 'api/audio.wav'
            
        audio_player_thread = AudioPlayerThread(audio_path)
        audio_player_thread.start()
        self.model_window.show_message_with_timeout(outtext, self.timeout)

        
    def on_timeout2(self):
        self.model_window.mouth()
        self.timer2.stop() 

    def on_timeout(self):
        # 每当定时器超时时，调用 model_window 的 mouth 方法
        self.model_window.mouth() 
        # 递减计数器
        self.trigger_count -= 1
        # 检查是否达到触发次数限制
        if self.trigger_count <= 1:
            self.timer.stop()  # 停止定时器
            
    def download_audio(self, url, filename):
        global audio
        audio = filename
        def _download():
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                with open(audio, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)

        download_thread = threading.Thread(target=_download)
        download_thread.start()


    def autime(self, aupath):
        def _autime_thread(aupath):
            try:
                # 直接从本地文件路径加载音频文件
                self.audio = AudioSegment.from_file(aupath)
                audtime = len(self.audio)   # pydub 使用毫秒，转换为秒
                # 将结果放入队列
                self.audtime_queue.put(audtime)
                self.audtime_event.set()  # 操作完成，设置事件
            except Exception as e:
                print(f"Failed to read audio file: {e}")
                self.audtime_queue.put(None)  # 如果读取失败，放入None
            finally:
                self.audtime_event.set()  # 确保无论如何事件都被设置

        # 确保 aupath 是有效的文件路径
        if os.path.isfile(aupath):
            # 创建并启动新线程来计算音频时长
            threading.Thread(target=_autime_thread, args=(aupath,)).start()
        else:
            print(f"The specified audio path does not exist: {aupath}")
            # 可以在这里将None放入队列，表示没有文件可供处理
            self.audtime_queue.put(None)
    
  #   def on_timeout2(self):

    #     self.timer2.stop()
           
    def play(self, url):
        global audio
        if conf["TALK"]=='微软语音':
            edgeaudio = r'api/edge/audio.mp3'
            # audio_player_thread = AudioPlayerThread(edgeaudio)
            # audio_player_thread.start()
            audio = 'api/edge/audio1.mp3'
            self.copy_audio_file(edgeaudio, audio)
            self.autime(audio)
            self.audtime_event.wait()
            audtime = self.audtime_queue.get()
            self.timeout = audtime 
            audio_path = audio1
            if outtext == '开始新对话了':
                audio_path = 'api/audio.wav'            
            def a():
                self.model_window.newmotion(audio_path)
            motion_thread = HiddenWindowThread(target=a)
            motion_thread.start()

            audio_player_thread = AudioPlayerThread1(audio_path)
            audio_player_thread.start()            
            self.model_window.show_message_with_timeout(outtext, self.timeout)           
            # self.start_mouth_motions(audtime)
            # self.start_mouth_motions0()
        elif conf["TALK"]=='CosyVoice语音':
            cosyaudio = r'api/cosy/audio.wav'
            audio = 'api/cosy/audio1.wav'
            self.copy_audio_file(cosyaudio, audio)
            self.autime(audio)
            self.audtime_event.wait()
            audtime = self.audtime_queue.get()
            self.timeout = audtime 
            audio_path = audio1
            if outtext == '开始新对话了':
                audio_path = 'api/audio.wav'            
            def a():
                self.model_window.newmotion(audio_path)
            motion_thread = HiddenWindowThread(target=a)
            motion_thread.start()
            audio_player_thread = AudioPlayerThread1(audio_path)
            audio_player_thread.start() 
            self.model_window.show_message_with_timeout(outtext, self.timeout)                 
        else:
            #self.download_audio(url, audio)
            self.copy_audio_file(audio0, audio)
            self.autime(audio)
            self.audtime_event.wait()
            audtime = self.audtime_queue.get()
            self.timeout = audtime 
            audio_path = audio1
            if outtext == '开始新对话了':
                audio_path = 'api/audio.wav'            
            def a():
                self.model_window.newmotion(audio_path)
            motion_thread = HiddenWindowThread(target=a)
            motion_thread.start()
            audio_player_thread = AudioPlayerThread1(audio_path)
            audio_player_thread.start()           
            self.model_window.show_message_with_timeout(outtext, self.timeout)
        def aa():
            global isimg
            # print(appwindow.timeout)
            time0 = appwindow.timeout*0.001
            time.sleep(time0)    
            isimg = True
        staraa = threading.Thread(target=aa)  
        staraa.start()        

    # def audioplay(self):
    #     # 初始化pygame
    #     pygame.mixer.init()
    #     # 加载音频文件
    #     pygame.mixer.music.load(audio)
    #     # 播放音频
    #     pygame.mixer.music.play()
    #     # 等待音频播放结束
    #     while pygame.mixer.music.get_busy():
    #         pygame.time.Clock().tick(10)

    # def test(self):
    #     url = "http://localhost:9872/file=C:/Users/ASUS/AppData/Local/Temp/gradio/03cbb82b1f5403c44c0d87848b9ff79a7b0e8d55/audio.wav"
    #     self.play(url)

    def send_text_to_server(self, text, callback):
        global isimg
        isimg = False
        if  conf["TALK"]=='无语音请求':
            url = "http://localhost:8000/onlyglm4/" 
        elif conf["TALK"]=='微软语音':
            url = "http://localhost:8000/onlyglm4/" 
        elif conf["TALK"]=='CosyVoice语音':
            url = "http://localhost:8000/onlyglm4/"   
        else:   
            url = "http://localhost:8000/multi_round_conversation/"
        headers = {
            'Content-Type': 'application/json',
        }
        if conf["TALK"]=='GPT-SOVITS语音请求':
            data = {
                'text': text
            }
        elif conf["TALK"]=='无语音请求':
            data = {
                'text': text,
                'weiruan': 2
            }
        elif conf["TALK"]=='CosyVoice语音':
            data = {
                'text': text,
                'weiruan': 3
            }
        else:
             data = {
                'text': text,
                'weiruan': 1
            }
        result_queue = queue.Queue() 


        def thread_function(text, callback, queue):
            try:
                response = requests.post(url, json=data, headers=headers)
                response.raise_for_status()  # 将触发HTTPError，如果状态码不是200
                result = response.json().get('out', None)
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                result = None
            queue.put(result)  # 将结果放入队列
            callback(result)  # 调用回调函数并传递结果

        # 使用 partial 确保 self 能够正确引用
        thread = threading.Thread(target=partial(thread_function, text, callback, result_queue))
        thread.start()

    def callback(self, result):
        global outtext
        if result is not None:
            outtext = result
            self.updated.emit()  # 发射信号
        else:
            print("No response received")

    def onlytalkshowmeeeage(self):
        if outtext == '开始新对话了':
            sound = 'api/audio.wav'
            audio_player_thread = AudioPlayerThread(sound)
            audio_player_thread.start()
        self.model_window.show_message_with_timeout(outtext, 0)

    def update_ui_slot(self):
 
       if conf["TALK"]=='无语音请求':
            self.onlytalkshowmeeeage()
       elif conf["TALK"]=='CosyVoice语音':
            self.play(audio)     
       else: 
            self.play(audio)

    def wait_for_file(self, file_path, timeout=10, check_interval=0.1):
        start_time = time.time()
        while True:
            if os.path.exists(file_path):
                return True
            if time.time() - start_time > timeout:
                return False
            time.sleep(check_interval)        

    def random_string(self, length):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    def copy_audio_file(self, source_path, destination_path):
        # 尝试删除目标文件，如果它存在
        max_attempts = 5  # 设置最大尝试次数
        attempts = 0
        while attempts < max_attempts:
            try:
                os.remove(destination_path)
                # print(f"已删除旧文件 {destination_path}")
                break  # 成功删除，跳出循环
            except PermissionError as e:
                # print(f"无法删除目标文件: {e}，重试第 {attempts + 1} 次")
                attempts += 1  # 增加尝试次数
                time.sleep(1)  # 等待1秒钟后重试

        if attempts >= max_attempts:
            print(f"已尝试 {max_attempts} 次删除文件，但仍然失败。")

        # 复制新文件
        try:
            shutil.copyfile(source_path, destination_path)
            # print(f"文件已复制从 {source_path} 到 {destination_path}")
        except IOError as e:
            # 如果复制过程中发生错误，打印错误信息
            print(f"复制文件时出错: {e}")
            return
        if conf["TALK"]=='微软语音':
            houhzui = ".mp3"
        else:    
            houhzui = ".wav"
        # 创建新的随机命名音频文件
        audio_folder = "audio"  # 存储随机命名音频文件的文件夹
        os.makedirs(audio_folder, exist_ok=True)  # 确保文件夹存在
        random_filename = self.random_string(10) + houhzui  # 生成随机文件名
        audio1_path = os.path.join(audio_folder, random_filename)

        # 复制音频文件到新的随机命名文件
        try:
            shutil.copyfile(destination_path, audio1_path)
            # print(f"已创建随机命名文件: {audio1_path}")
        except IOError as e:
            # 如果复制过程中发生错误，打印错误信息
            print(f"创建随机命名文件时出错: {e}")
            return

        # 更新全局变量 audio1
        global audio1
        audio1 = audio1_path

def update_config_with_file_names(config_file_path='config/config.json'):
    # 读取配置文件
    with open(config_file_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    # 获取moys文件夹中所有txt文件的文件名（不含扩展名）
    moys_dir = 'moys'
    moys_file_names = [os.path.splitext(file)[0] for file in os.listdir(moys_dir) if file.endswith('.txt')]

    # 获取moban文件夹中所有txt文件的文件名（不含扩展名）
    moban_dir = 'moban'
    moban_file_names = [os.path.splitext(file)[0] for file in os.listdir(moban_dir) if file.endswith('.txt')]

    # 更新GSVModel和Presets的options列表
    config_data['GSVModel']['options'] = moys_file_names
    config_data['Presets']['options'] = moban_file_names

    # 写入更新后的配置数据到文件
    with open(config_file_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

    print("配置文件已更新") 

def update_config_and_options(config_file_path=r"config/config.json"):
    # 读取配置文件
    with open(config_file_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    # 读取当前目录Resources文件夹中所有文件夹的名字
    resources_dir = os.path.join(os.getcwd(), 'Resources')
    folder_names = [d for d in os.listdir(resources_dir) if os.path.isdir(os.path.join(resources_dir, d))]

    # 更新Live2DModel的options列表
    config_data['Live2DModel']['options'] = folder_names


    
    # 找到与Live2DModel默认值匹配的文件夹
    default_model_folder = config_data['Live2DModel'].get('default', None)
    model_dir = None  # 初始化model_dir为None

    if default_model_folder and os.path.isdir(os.path.join(resources_dir, default_model_folder)):
        model_dir = os.path.join(resources_dir, default_model_folder)
    else:
        # 默认文件夹不存在，从options中随机选择一个
        options = config_data['Live2DModel'].get('options', [])
        if options:
            selected_folder = random.choice(options)
            model_dir = os.path.join(resources_dir, selected_folder)
            # 更新配置文件中的默认值
            config_data['Live2DModel']['default'] = selected_folder
        else:
            # 如果options列表为空，抛出异常
            raise FileNotFoundError("没有找到有效的模型文件夹")

    # 保存更新后的配置文件
    with open(config_file_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)
        
    # 在匹配的文件夹中查找.model3.json或.model.json文件
    json_files_model3 = [f for f in os.listdir(model_dir) if f.endswith('.model3.json')]
    if not json_files_model3:
        json_files_model2 = [f for f in os.listdir(model_dir) if f.endswith('.model.json')]
        if not json_files_model2:
            print("没有找到.model3.json或.model.json文件")
            return  # 如果没有找到文件，则退出函数
        else:
            selected_json_file = os.path.join(model_dir, json_files_model2[0])
            model = 2  # 设置模型类型为2
    else:
        selected_json_file = os.path.join(model_dir, json_files_model3[0])
        model = 3  # 设置模型类型为3

    # 读取JSON文件
    with open(selected_json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # 根据模型类型处理motions
    if model == 3:
        # 模型类型为3，从'FileReferences'下的'Motions'获取motions
        motions = json_data.get('FileReferences', {}).get('Motions', {})
    elif model == 2:
        # 模型类型为2，直接从顶层获取motions
        motions = json_data.get('motions', {})

    # 确保motions不为空
    if motions:
        # 遍历motions中的所有内容，并生成自动播放选项
        auto_play_options = []
        for motion_name, motion_list in motions.items():
            if motion_name == 'mytalk':
                continue  # 忽略'my'键
            for motion in motion_list:
                auto_play_options.append(motion_name)  # 假设这里只需要motion_name

        # 更新AutoPlayAction的options列表
        config_data['AutoPlayAction']['options'] = auto_play_options
    else:
        print("JSON文件中没有找到motions数据")
        model = 0  # 设置模型类型为0，表示没有找到有效的motions

    # 写入更新后的配置数据到文件
    if model:  # 如果模型类型不为0，才写入文件
        try:
            with open(config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            print("配置文件已更新")
        except Exception as e:
            print(f"写入配置文件时发生错误: {e}")

    print("配置文件已更新")


def delate(path ='audio'):
    if os.path.exists(path):
        # 遍历路径下的所有文件
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                # 如果是文件，则删除
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    # 如果是目录，则递归删除
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
        print("The specified path does not exist.")    

class MainWindow(QMainWindow):
    def __init__(self, app_window: AppWindow, qapp):
        super().__init__()
        self.init_ui()
        self.app_window = app_window
        self.qapp = qapp  # 存储 QApplication 实例的引用

    def init_ui(self):
        self.setWindowTitle("AI桌宠")
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)

        # 加载自定义图标
        tray_icon = QIcon('ico/1.jpg')

        # 设置系统托盘图标
        self.tray_icon.setIcon(tray_icon)
        self.menu = QMenu(self)  # 设置 MainWindow 为菜单的父窗口
        # 为菜单项添加图标和样式
        self.top_action = QAction(QIcon('ico/4.png'), "置顶/关闭", self)
        self.top_action.setCheckable(True)
        self.top_action.setChecked(False)
        self.top_action.triggered.connect(self.widtop)
        self.menu.addAction(self.top_action)


        move_action = QAction(QIcon('ico/3.png'), "配置", self)
        move_action.triggered.connect(self.movewin)
        self.menu.addAction(move_action)

        self.toggle_action = QAction(QIcon('ico/1.png'), "显示/隐藏", self)
        self.toggle_action.setCheckable(True)
        self.toggle_action.setChecked(True)
        self.toggle_action.triggered.connect(self.toggle_window)
        self.menu.addAction(self.toggle_action)

        self.sayapi = QAction(QIcon('ico/1.png'), "语音/关闭", self)
        self.sayapi.setCheckable(True)
        self.sayapi.setChecked(False)
        self.sayapi.triggered.connect(self.opensayapi)
        self.menu.addAction(self.sayapi) 

        self.sentimg = QAction(QIcon('ico/1.png'), "自动发送/关闭", self)
        self.sentimg.setCheckable(True)
        self.sentimg.setChecked(False)
        self.sentimg.triggered.connect(self.onsentimg)
        self.menu.addAction(self.sentimg)                

        exit_action = QAction(QIcon('ico/2.png'), "退出", self)
        exit_action.triggered.connect(self.exit_app)
        self.menu.addAction(exit_action)

        # 设置菜单样式
        self.menu.setStyleSheet("""
            QMenu {
                /* 设置菜单的样式 */
                background-color: rgba(255, 255, 255, 0);
                padding: 0px; 
                                               
            }
            QMenu::item {
                /* 设置菜单项的样式 */
                background-color: rgba(255, 255, 255, 1);
                color: black;
                font-family: WenQuanYi Zen Hei;
                width: 100px; 
                height: 35px;               
                border-radius: 0px;               
                font: bold 16px;
                padding: 10px;                              
                text-align: center; /* 文本右对齐 */
            }
            QMenu::item:selected {
                /* 设置选中的菜单项的样式 */
                color: white;
                background-color: rgba(0, 0, 0, 1);
            }
            QMenu::item:Checked {
                /* 设置选中的菜单项的样式 */
                color: white;
                background-color: rgba(0, 0, 0, 1);
            }
        """)

        # 将菜单连接到系统托盘图标
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self.show_menu)

        # 显示系统托盘图标
        self.tray_icon.show()



        # 创建中心小部件
        self.widget = QWidget(self)  
        # 创建主窗口的布局
        self.main_layout = QVBoxLayout(self.widget)

        # 创建水平布局
        self.buju = QHBoxLayout()

        # 添加组件到水平布局
        self.buju.addWidget(QLabel('GPT-SOVITS根目录路径'))
        self.kuang = QLineEdit()
        self.buju.addWidget(self.kuang)

        # 创建选择文件夹的按钮
        self.buto2 = QPushButton('选择路径')
        self.buto2.clicked.connect(self.selectDirectory)
        self.buju.addWidget(self.buto2)

        # # 创建选择文件夹的按钮
        # self.setup = QPushButton('安装额外依赖')
        # self.setup.clicked.connect(self.gsvup)
        # self.buju.addWidget(self.setup)

        self.bujulast = QHBoxLayout()
        # 创建保存按钮
        self.buto1 = QPushButton('保存所有')
        self.buto1.clicked.connect(self.update_config_from_widgets)
        self.bujulast.addWidget(self.buto1)


        self.buju2 = QHBoxLayout()
        self.buju2.addWidget(QLabel('glm4的refresh_token和assistant_id'))
        self.kuang2 = QLineEdit()
        self.buju2.addWidget(self.kuang2)
        self.kuang21 = QLineEdit()
        self.buju2.addWidget(self.kuang21)
        self.buto3 = QPushButton('打开网站')
        self.buto3.clicked.connect(self.openweb)
        self.buju2.addWidget(self.buto3) 

        self.buju3 = QHBoxLayout()
        self.llm = QComboBox()
        self.llm.addItems(['glm4', 'kimi' ,'deepseekv2','ollama'])
        self.ollamabut = QPushButton('加载ollama模型(注意ollama端口要在运行)')
        self.ollamabut.clicked.connect(self.configollama)        
        self.buju3.addWidget(QLabel('聊天模型'))
        self.buju3.addWidget(self.llm)
        self.buju3.addWidget(self.ollamabut)

        self.buju4 = QHBoxLayout()
        self.buju4.addWidget(QLabel('kimi的refresh_token'))
        self.k1 = QLineEdit()
        self.buju4.addWidget(self.k1)
        self.b1 = QPushButton('打开网站')
        self.b1.clicked.connect(self.openwebkimi)
        self.buju4.addWidget(self.b1)

        self.buju41 = QHBoxLayout()
        self.buju41.addWidget(QLabel('deepseekv2的usertoken'))
        self.k2 = QLineEdit()
        self.buju41.addWidget(self.k2)
        self.b2 = QPushButton('打开网站')
        self.b2.clicked.connect(self.openwebdeep)
        self.buju41.addWidget(self.b2)        

        self.buju5 = QHBoxLayout()
        self.buju5.addWidget(QLabel('腾讯翻译SecretId和SecretKey'))
        self.kuang3 = QLineEdit()
        self.kuang4 = QLineEdit()
        self.buju5.addWidget(self.kuang3)
        self.buju5.addWidget(self.kuang4)

        self.buju6 = QHBoxLayout()
        self.buju6.addWidget(QLabel('腾讯翻译源语种和翻译语种'))
        self.kuang5 = QLineEdit()
        self.kuang6 = QLineEdit()
        self.buju6.addWidget(self.kuang5)
        self.buju6.addWidget(self.kuang6)

        self.buju7 = QHBoxLayout()
        self.buju7.addWidget(QLabel('百度翻译的APPID和SECRET'))
        self.kuang7 = QLineEdit()
        self.kuang8 = QLineEdit()
        self.buju7.addWidget(self.kuang7)
        self.buju7.addWidget(self.kuang8)

        self.buju8 = QHBoxLayout()
        self.buju8.addWidget(QLabel('百度翻译源语种和翻译语种'))
        self.kuang9 = QLineEdit()
        self.kuang10 = QLineEdit()
        self.buju8.addWidget(self.kuang9)
        self.buju8.addWidget(self.kuang10)

        self.buju9 = QHBoxLayout()
        self.buju9.addWidget(QLabel('百度ai翻译的access_token'))
        self.kuang11 = QLineEdit()
        self.buju9.addWidget(self.kuang11)

        self.buju10 = QHBoxLayout()
        self.buju10.addWidget(QLabel('百度ai翻译源语种和翻译语种'))
        self.kuang12 = QLineEdit()
        self.kuang13 = QLineEdit()
        self.buju10.addWidget(self.kuang12)
        self.buju10.addWidget(self.kuang13) 

        self.buju11 = QHBoxLayout()
        self.buju11.addWidget(QLabel('微软Azure的speech_key和service_region'))
        self.kuang14 = QLineEdit()
        self.kuang15 = QLineEdit()
        self.buju11.addWidget(self.kuang14)
        self.buju11.addWidget(self.kuang15)         

        self.dashang = QHBoxLayout()
        self.ds = QPushButton('打赏up，我们都有美好的未来')
        self.ds.clicked.connect(self.dsup)
        self.dashang.addWidget(self.ds)         

        
        # 将水平布局添加到中心小部件的垂直布局中
        self.main_layout.addLayout(self.buju)
        self.main_layout.addLayout(self.buju3)
        self.main_layout.addLayout(self.buju2)
        self.main_layout.addLayout(self.buju4)
        self.main_layout.addLayout(self.buju41)        
        self.main_layout.addLayout(self.buju5)
        self.main_layout.addLayout(self.buju6)
        self.main_layout.addLayout(self.buju7)
        self.main_layout.addLayout(self.buju8)
        self.main_layout.addLayout(self.buju9)
        self.main_layout.addLayout(self.buju10)
        self.main_layout.addLayout(self.buju11)              
        self.main_layout.addLayout(self.bujulast)
        self.main_layout.addLayout(self.dashang)
        self.setStyleSheet("""   
            QWindoww {
                background-color: rgba(0 , 0 , 0, 1);
            }                                                             
            QGroupBox {
                font-family: Microsoft YaHei;
                background-color: rgba(0 , 0 , 0, 1.0);
                font: bold 18px;
                border-radius: 62.5px;           
                margin-top: 30px;
            }
            QPushButton {
                font-family: Microsoft YaHei;
                background-color: rgba(0, 0, 0, 1.0);
                font: bold 18px;
                border: 2px solid black;
                border-radius: 12.5px;
                padding: 8px;
                color: white;
                text-align: center;
                min-width: 10px;
            }
            QPushButton:hover {
                color: black;
                background-color: rgba(255, 255, 255, 1);
            }
            QLineEdit {
                font-family: Microsoft YaHei;
                background-color: rgba(255, 255, 255, 1.0);
                font: bold 18px;
                border-radius: 12.5px;
                padding: 5px;
                color: black;
                min-width: 17px;
            }
            QLineEdit:hover {
                background-color: rgba(0, 0, 0, 1);

                color: white;

            }
            QComboBox {
                font-family: Microsoft YaHei;
                background-color: rgba(255, 255, 255, 1.0);
                font: bold 18px;
                text-align: center;
                border-radius: 12.5px;
                padding: 6px;
                color: black;
                min-width: 4px;
                text-align: center;           
            }
            QComboBox:hover {
                background-color: rgba(0, 0 , 0, 1);
                color: white;           
                           
            }
            QComboBox QAbstractItemView {
                background-color: rgba(0, 0, 0, 1.0);           
                font-family: Microsoft YaHei;
                font: bold 18px;
                background-color: white;
                text-align: center;
                padding: 6px;
                border: none;
                color: black;            
                text-align: center;           
                selection-background-color:black;
                selection-color:white;
            }
            QLabel {
                font-family: Microsoft YaHei;
                font: bold 18px;
                text-align: center;           
                color: black;
                text-align: center;
                /* 其他样式属性 */
            }
        """)



 
        # 设置中心小部件
        self.setWindowIcon(QIcon('ico/1.ico'))
        self.setCentralWidget(self.widget)
        self.load_config_and_set_widgets()

        self.setWindowTitle("配置菜单")
    def configollama(self): 
        audio_player_thread = AudioPlayerThread('config/tsaudio/audio(7).wav')
        audio_player_thread.start()          
        def generate_response(config_file="api/ollama.json"):
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
                audio_player_thread = AudioPlayerThread('config/tsaudio/audio(8).wav')
                audio_player_thread.start()          
                print(response.text)
            else:
                raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
        ollama = threading.Thread(target=generate_response)
        ollama.start()
    def dsup(self):
        # 定义 HTML 文件的相对路径
        relative_file_path = 'config/dsup.html'
        # 获取当前工作目录
        current_working_directory = os.getcwd()
        # 构建绝对路径
        file_path = os.path.join(current_working_directory, relative_file_path)
        # 转换为适用于 URL 的路径格式
        file_url = 'file://' + '/'.join(file_path.split('\\'))  # 替换为 '/' 以适应 URL 格式
        # 打开默认浏览器并导航到文件 URL
        webbrowser.open(file_url)

    def update_config_from_widgets(self):
        # 读取api/api.json配置文件
        with open('api/api.json', 'r', encoding='utf-8') as file:
            api_config = json.load(file)
        
        # 读取api/gsv.json配置文件
        with open('api/gsv.json', 'r', encoding='utf-8') as file:
            gsv_config = json.load(file)
        
        # 更新api/api.json配置
        api_config['TOKEN'] = self.kuang2.text()
        api_config['LLM'] = (
            'glm' if self.llm.currentIndex() == 0 else
            'kimi' if self.llm.currentIndex() == 1 else
            'deepseek' if self.llm.currentIndex() == 2 else
            'ollama'  # 假设 currentIndex 为 2 时代表 'ollama'
        )

        api_config['TXSecretId'] = self.kuang3.text()
        api_config['TXSecretKey'] = self.kuang4.text()
        api_config['TXS'] = self.kuang5.text()
        api_config['TXT'] = self.kuang6.text()
        api_config['APPID'] = self.kuang7.text()
        api_config['SECRET'] = self.kuang8.text()
        api_config['BDTS'] = self.kuang9.text()
        api_config['BDTT'] = self.kuang10.text()
        api_config['BDaccess_token'] = self.kuang11.text()
        api_config['BDS'] = self.kuang12.text()
        api_config['BDT'] = self.kuang13.text()
        api_config['speech_key'] = self.kuang14.text()        
        api_config['service_region'] = self.kuang15.text()        
        # 写回api/api.json配置文件
        with open('api/api.json', 'w', encoding='utf-8') as file:
            json.dump(api_config, file, ensure_ascii=False, indent=4)
        
        # 更新api/gsv.json配置
        gsv_config['gsv'] = self.kuang.text()
        gsv_config['chatglm_refresh_token'] = self.kuang2.text()
        gsv_config['assistant_id'] = self.kuang21.text()                
        gsv_config['refresh_token'] = self.k1.text() 
        gsv_config['usertoken'] = self.k2.text()                
        # 写回api/gsv.json配置文件
        with open('api/gsv.json', 'w', encoding='utf-8') as file:
            json.dump(gsv_config, file, ensure_ascii=False, indent=4)
        gsvpath()
        copy_moys_folder()    


    def load_config_and_set_widgets(self, config_path ='api/api.json'):
        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)

        # 设置glm4的token
        self.kuang2.setText(config['TOKEN'])

        # 设置聊天模型
        if config['LLM'] == 'glm':
            self.llm.setCurrentIndex(0)  # 选择glm4
        elif config['LLM'] == 'kimi':
            self.llm.setCurrentIndex(1)  # 选择kimi
        elif config['LLM'] == 'deepseekv2':
            self.llm.setCurrentIndex(2) 
        else:
            self.llm.setCurrentIndex(3)               


        # 设置腾讯翻译SecretId和SecretKey
        self.kuang3.setText(config['TXSecretId'])
        self.kuang4.setText(config['TXSecretKey'])

        # 设置腾讯翻译源语种和翻译语种
        self.kuang5.setText(config['TXS'])
        self.kuang6.setText(config['TXT'])

        # 设置百度翻译的APPID和SECRET
        self.kuang7.setText(str(config['APPID']))
        self.kuang8.setText(config['SECRET'])

        # 设置百度翻译源语种和翻译语种
        self.kuang9.setText(config['BDTS'])
        self.kuang10.setText(config['BDTT'])

        # 设置百度ai翻译的access_token
        self.kuang11.setText(config['BDaccess_token'])

        # 设置百度ai翻译源语种和翻译语种
        self.kuang12.setText(config['BDS'])
        self.kuang13.setText(config['BDT'])
        self.kuang14.setText(config['speech_key'])
        self.kuang15.setText(config['service_region'])        

        config_path1 = 'api/gsv.json'
        with open(config_path1, 'r', encoding='utf-8') as file:
            config1 = json.load(file)
            self.kuang.setText(config1['gsv'])
            self.kuang2.setText(config1['chatglm_refresh_token'])
            self.kuang21.setText(config1['assistant_id'])              
            self.k1.setText(config1['refresh_token'])
            self.k2.setText(config1['usertoken'])               

    def openweb(self):
        try:
            webbrowser.open('https://chatglm.cn/')
        except Exception as e:
            self.kuang2.setText(f"An error occurred: {e}")
    def openwebkimi(self):
        try:
            webbrowser.open('https://kimi.moonshot.cn/')
        except Exception as e:
            self.kuang2.setText(f"An error occurred: {e}")
    def openwebdeep(self):
        try:
            webbrowser.open('https://chat.deepseek.com/')
        except Exception as e:
            self.kuang2.setText(f"An error occurred: {e}")            
    def selectDirectory(self):
        # 弹出文件夹选择对话框
        directory = QFileDialog.getExistingDirectory(self, "选择目录")
        if directory:
            self.kuang.setText(directory)  # 将选择的路径填充到QLineEdit中



    def widtop(self):
        # 根据 QAction 的选中状态来显示或隐藏窗口
        if self.top_action.isChecked():
            self.app_window.hide()
            self.app_window.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            self.app_window.show()
        else:
            self.app_window.hide()
            self.app_window.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.app_window.show()




    # def on_value_changed(self, value):
    #     global y
    #     self.value_label.setText(f"垂直: {value}")
    #     current_pos = self.app_window.pos()  # 获取当前窗口的位置
    #     new_y = value  # 新的 Y 坐标值
    #     self.app_window.move(current_pos.x(), new_y)  # 保持 X 坐标不变，设置新的 Y
    #     y = value  
    #     write_position_to_file()
    # def on_value_changed1(self, value):
    #     global x
    #     self.value_label1.setText(f"水平: {value}")
    #     current_pos = self.app_window.pos()  # 获取当前窗口的位置
    #     new_X = value  # 新的 x 坐标值
    #     self.app_window.move(new_X, current_pos.y())  # 保持 X 坐标不变，设置新的 x         
    #     x = value  
    #     write_position_to_file()
    def show_menu(self, reason):
        # 显示菜单的逻辑
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.Context):
            cursor_pos = QCursor.pos()  # 获取当前鼠标的位置
            menu_height = self.menu.sizeHint().height()  # 获取菜单的高度
            menu_width = self.menu.sizeHint().width()  # 获取菜单的宽度
            pos = QPoint(cursor_pos.x()- menu_width, cursor_pos.y() - menu_height)  # 调整 Y 坐标
            self.menu.popup(pos)  # 在调整后的位置显示菜单
    def opensayapi(self):
        no = os.getcwd() 
        bat_file_path = os.path.join(no,"sensvoice", "api.bat")
        bat_file_dir = os.path.dirname(bat_file_path)
        if self.sayapi.isChecked():
            def s():
                try:
                    # bat_file_dir = os.path.dirname(batch_file_path)

                    # 在新窗口中运行批处理文件，并设置工作目录
                    subprocess.Popen(f'start cmd /K "cd /D {bat_file_dir} && {bat_file_path}"', shell=True)
                    # 返回到当前工作目录
                    os.chdir(os.getcwd())  
                except subprocess as e:
                    print("An error")

            ss = threading.Thread(target=s)
            ss.start()        
        else:
            def d():
                try:
                    url = "http://localhost:1111/shutdown"
                    response = requests.post(url)

                    print(response.status_code)
                    print(response.text)  
                except requests as e:
                    # 打印错误信息
                    print("error", e) 
            dd = threading.Thread(target=d)
            dd.start() 
    def onsentimg(self):
        global openisimg
        if self.sentimg.isChecked(): 
            openisimg = True
        else:
            openisimg = False       
    def toggle_window(self):
        # 根据 QAction 的选中状态来显示或隐藏窗口
        if self.toggle_action.isChecked():
            self.app_window.show()
        else:
            self.app_window.hide()
        

    def show_tray_icon(self):
        self.tray_icon.show()

    def qApp(self):
        return self.qapp  # 返回 QApplication 实例

    def exit_app(self):
        app = self.qApp()
        try:
            sys.exit(app.exec_())
        finally:
            live2dv3.dispose() 
    def movewin(self):
        self.show()
        # self.app_window.move(200, 200)

x = None
y = None

def read_position_from_file():
    global x, y  # 声明全局变量
    try:
        with open('config/pos.txt', 'r') as file:  # 打开文件
            lines = file.readlines()  # 读取所有行
            x = int(lines[0].strip())  # 将第一行转换为整数并去除空白字符
            if len(lines) > 1:  # 确保文件有第二行
                y = int(lines[1].strip())  # 将第二行转换为整数并去除空白字符
    except FileNotFoundError:
        print("文件未找到，请确保 'config/pos.txt' 文件存在于正确的路径。")
    except IndexError:
        print("文件内容不足两行，请确保文件有两行内容。")
    except ValueError:
        print("文件中的值无法转换为整数，请确保第一行和第二行是有效的整数。")

def write_position_to_file():
    global x, y  # 声明全局变量
    try:
        with open('config/pos.txt', 'w') as file:  # 打开文件用于写入
            file.write(f"{x}\n")  # 写入x的值，后跟换行符
            file.write(f"{y}\n")  # 写入y的值，后跟换行符
        print("位置已保存。")
    except IOError as e:
        print(f"写入文件时发生错误: {e}")

def copy_moys_folder():
    config_path = 'api/gsv.json'
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        gsvpath = config.get('gsv', '')  # 使用get方法提供默认值，以防'gsv'键不存在
    except FileNotFoundError:
        print(f"配置文件 {config_path} 未找到。")
        return
    except json.JSONDecodeError:
        print(f"配置文件 {config_path} 格式错误，无法解析JSON。")
        return

    if not gsvpath:
        print("配置中未指定有效的'gsv'路径。")
        return

    src_folder = os.path.join(gsvpath, 'moys')
    if not os.path.exists(src_folder):
        print(f"源文件夹 {src_folder} 不存在。")
        return

    current_dir = os.getcwd()
    dst_folder = os.path.join(current_dir, 'moys')
    if os.path.exists(dst_folder):
        shutil.rmtree(dst_folder)
        print(f"已删除当前目录下的原有文件夹 {dst_folder}")

    shutil.copytree(src_folder, dst_folder)
    print(f"文件夹 {src_folder} 已成功复制到当前目录。")


def main():
    global appwindow

    # if live2dver == 3:
    live2dv3.init()
    # else:
    live2dv2.init()
    delate()
    gsvpath()
    copy_moys_folder()

    update_config_and_options()
    update_config_with_file_names()
    delate('api/audio')
    upmotions()
    update_and_copy_folders()

    read_config_file_and_save_defaults()

    # read_config_file_and_save_defaults()
    read_position_from_file()

    app = QApplication(sys.argv)
    
    app.setWindowIcon(QIcon('1.ico'))

    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    scale_factor = 120 / 96.0
    app.setDesktopSettingsAware(False)

    # 创建 Win 类的实例
    model_window = Win()

    model_window.load_motion_config()
    set = SettingsDialog(model_window)

    # 创建 AppWindow 实例并传递 Win 类的实例
    app_window = AppWindow(model_window, set)
    appwindow = app_window

    main_window = MainWindow(app_window, app)
    set.duault()
    app_window.move(x, y)
    app_window.show()

    model_window.show()

    try:
        sys.exit(app.exec_())
    finally:
        live2dv3.dispose() 
        live2dv2.dispose() 
        # 这将被执行，因为它在 finally 块中
    os._exit()    

if __name__ == "__main__":
    # hide_console_window()
    main()