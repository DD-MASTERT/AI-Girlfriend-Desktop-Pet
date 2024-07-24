from PySide2.QtCore import QTimer, Qt, QEvent, QPoint, QTimerEvent, Signal
from PySide2.QtGui import QMouseEvent, QCursor,QIcon
# from PySide2.QtOpenGLWidgets import QOpenGLWidget
# from PySide2.QtOpenGL import QOpenGLWidget
from PySide2.QtWidgets import QOpenGLWidget
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtWidgets import QLabel, QVBoxLayout,QHBoxLayout
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtWidgets import QSpacerItem
from PySide2.QtGui import QSurfaceFormat
from OpenGL.GL import glEnable, GL_MULTISAMPLE
import asyncio
import glob
import time
import os
import json
import pygame
import re
import random
import threading
import live2d.v3 as live2dv3
import live2d.v2 as live2dv2
import wave
import struct
from pydub import AudioSegment
# import live2d.v2 as live2d

global_motion_dict = {}

live2dver = None
def check_model_version(name):
    global live2dver
    # 构建目标文件夹的路径
    folder_path = os.path.join(os.getcwd(), 'Resources', name)
    
    # 检查文件夹是否存在
    if not os.path.isdir(folder_path):
        print(f"没有找到名为 {name} 的文件夹。")
        return
    
    # 检查是否存在name.model3.json文件
    model3_pattern = os.path.join(folder_path, f'{name}.model3.json')
    model3_file = glob.glob(model3_pattern)
    
    if model3_file:
        live2dver = 3
        print(f"找到了 {name}.model3.json 文件，live2d版本设置为 3。")
    else:
        # 检查是否存在name.model.json文件
        model_pattern = os.path.join(folder_path, f'{name}.model.json')
        model_file = glob.glob(model_pattern)
        
        if model_file:
            live2dver = 2
            print(f"找到了 {name}.model.json 文件，live2d版本设置为 2。")
        else:
            # 如果没有找到任何文件，打印消息
            print("没有找到模型文件。")

# 定义一个全局变量来存储default值
conf = {}

def read_config_file_and_save_defaults(file_path ='config/config.json'):
    global conf
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
      
# read_config_file_and_save_defaults()
# check_model_version(conf["Live2DModel"]).

            
stopmotiontime = False
lock = threading.Lock()
def starmotion():
    global stopmotiontime
    with lock:
        stopmotiontime = True

def stopmotion():
    global stopmotiontime
    with lock:
        stopmotiontime = False

class AudioPlayerThread1(threading.Thread):
    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path  # 存储音频文件路径
        self.stop_event = threading.Event()  # 初始化stop_event

    def run(self):
        starmotion()
        time.sleep(0.45)
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
class AudioPlayerThread(threading.Thread):
    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path  # 存储音频文件路径
        self.stop_event = threading.Event()  # 初始化stop_event

    def run(self):
        starmotion()
        # 确保在新线程中初始化pygame mixer
        pygame.mixer.init()
        # 加载音频文件
        pygame.mixer.music.load(self.audio_path)
        # 播放音频
        pygame.mixer.music.play()
        # 等待音频播放结束或停止事件被设置
        while pygame.mixer.music.get_busy() and not self.stop_event.is_set():
            pygame.time.Clock().tick(10)
        time.sleep(1)    
        stopmotion()

    def stop(self):
        self.stop_event.set()  # 设置stop_event，请求线程停止
          

class Win(QOpenGLWidget):
    read_config_file_and_save_defaults()
    check_model_version(conf["Live2DModel"])    
    if live2dver == 3:
        model: live2dv3.LAppModel
    elif live2dver == 2:
        model: live2dv2.LAppModel
    else:
        pass
    # model: live2dv3.LAppModel
    # 定义信号时使用小写，保持一致性
    mouth_signal = Signal()
    mouth_signal1 = Signal()
    lasttime = conf["BubbleDuration"]
    lasttime = int(lasttime)*1000
    modelname = conf["Live2DModel"]
    size_str = conf["CharacterSize"]
    width, height = size_str.split()  # 使用split默认以空格分割
    width = int(width)
    height = int(height)
    mou = conf["MouthSync"]
    mou = int(mou)
    motionname = conf["AutoPlayAction"]
    motiontime = conf["PlayFrequency"]
    left = conf["MouseThrough"]
    top = conf["Top"]
    winqt = None
    live2dlook = True
    tmotion = True
    aumotion = True
    fps =int (30)
    caiyang =int (32)
    talkkuan = conf["talkkuan"]
    talksize = conf["talksize"]   

    if (top == '开启') and (left == '开启'):
        winqt = Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput
    elif (top == '关闭') and (left == '开启'):
        winqt = Qt.WindowType.FramelessWindowHint | Qt.WindowTransparentForInput
    elif (top == '开启') and (left == '关闭'):
        winqt = Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint
    else:  # Assuming both top and left are '关闭'
        winqt = Qt.WindowType.FramelessWindowHint


    def __init__(self, parent=None):
        super(Win, self).__init__(parent)
        check_model_version(self.modelname)
        if live2dver == 3:
            self.model: live2dv3.LAppModel
        elif live2dver == 2:
            self.model: live2dv2.LAppModel
        else:
            pass
        # 尝试设置一个较高的MSAA采样率
        max_samples = self.caiyang  # 尝试设置为16x MSAA
        format = QSurfaceFormat()
        format.setSamples(max_samples)
        QSurfaceFormat.setDefaultFormat(format)
        self.setFormat(format)

        # 检查实际应用的采样率
        applied_samples = self.format().samples()
        if applied_samples < max_samples:
            print(f"系统支持的最大MSAA采样率为: {applied_samples}")
        self.setWindowFlags(self.winqt)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowTitle('live2D模型')
        self.setWindowIcon(QIcon('ico/1.jpg'))



        self.a = 0
        self.resize(self.width, self.height)
        self.dragging = False
        self.last_mouse_pos = QPoint()

         # 连接信号到槽函数，这里使用 lambda 表达式来避免绑定问题
        self.mouth_signal.connect(lambda: self.mouth())
        self.mouth_signal1.connect(lambda: self.mouth1())

        # 创建QTimer实例
        self.timer = QTimer(self)
        # 连接信号和槽
        self.timer.timeout.connect(self.update_model_gaze_to_cursor)
        # 启动定时器，例如每100毫秒更新一次
        self.timer.start(50)

        # 创建一个 QVBoxLayout 实例
        self.layout = QHBoxLayout()
        # 创建一个 QLabel 实例
        self.message_label = QLabel("")
        self.message_label2 = QLabel("")
        self.message_label3 = QLabel("")

        self.layout.addWidget(self.message_label2)
        self.layout.addWidget(self.message_label)
        self.layout.addWidget(self.message_label3)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中显示文本

        # 创建一个 QTimer 实例
        self.message_timer = QTimer(self)
        self.message_timer.timeout.connect(self.hide_message)  # 连接定时器信号到槽函数

                # 创建一个 QTimer 实例
        self.motion_timer = QTimer(self)
        self.motion_timer.timeout.connect(self.audomotion1)  # 连接定时器信号到槽函数
        motiontime = int(self.motiontime)

        self.motion_timer.start(motiontime*1000)



        # 设置窗口的布局
        self.setLayout(self.layout)
 
    def uptop(self, top, left):
        if (top == '开启') and (left == '开启'):
            self.winqt = Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput
        elif (top == '关闭') and (left == '开启'):
            self.winqt = Qt.WindowType.FramelessWindowHint | Qt.WindowTransparentForInput
        elif (top == '开启') and (left == '关闭'):
            self.winqt = Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint
        else:  # Assuming both top and left are '关闭'
            self.winqt = Qt.WindowType.FramelessWindowHint

        self.hide()
        self.setWindowFlags(self.winqt)
        self.show()


    def updata(self,motiontime,mou,motionname,lasttime,fps,caiyang,talkkuan,talksize):
        self.motiontime = motiontime
        self.motion_timer.stop()
        motiontime = int(self.motiontime)
        self.motion_timer.start(motiontime*1000)
        self.mou = mou
        self.motionname = motionname
        self.lasttime = int(lasttime)*1000
        self.fps = fps
        self.caiyang = caiyang
        self.talkkuan =talkkuan
        self.talksize =talksize


    def initializeGL(self) -> None:
        glEnable(GL_MULTISAMPLE)
        self.makeCurrent()

        if live2dver == 3:
            live2dv3.glewInit()
            live2dv3.setGLProperties()
            self.model = live2dv3.LAppModel()
            self.model.LoadModelJson("./Resources/"+self.modelname+"/"+self.modelname+".model3.json")
        else: 
            self.model = live2dv2.LAppModel()
            self.model.LoadModelJson("./Resources/"+self.modelname+"/"+self.modelname+".model.json")

        self.model.SetLipSyncN(self.mou)
        self.startTimer(int(1000 / self.fps))
    

    def resizeGL(self, w: int, h: int) -> None:
        if self.model:
            self.model.Resize(w, h)

    def paintGL(self) -> None:
        if live2dver == 3:
            live2dv3.clearBuffer()
        else:
            live2dv2.clearBuffer()    
        self.model.Update()

    def timerEvent(self, a0: QTimerEvent) -> None:
        if self.a == 0:
            self.audomotion(first=True)   
            self.a += 1
        self.update()


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

    def update_model_drag(self, event: QMouseEvent):
        # Make the model look at the mouse cursor
        # self.model.Drag(int(event.pos().x()), int(event.pos().y()))
        self.model.Drag(int(event.pos().x()*0.5), int(event.pos().y()*0.5))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:

            self.dragging = True
            self.last_mouse_pos = event.globalPos()
            if self.tmotion:
                self.audomotion(first=False)
            else: 
                pass
                # self.model.Touch(event.pos().x(), event.pos().y())
            # 可以在这里添加其他开始拖动时需要执行的代码
        else:
            # 如果点击位置不在区域内，可以执行其他逻辑或不执行任何操作
            pass
    # 可以在这里处理其他鼠标按钮的点击事件
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.dragging:
            # Move the window
            delta = QPoint(event.globalPos() - self.last_mouse_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.last_mouse_pos = event.globalPos()
        else:
            # Update the model's gaze in real-time
            if self.live2dlook:
                self.update_model_drag(event)
            else:
                pass    

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            # Update the model's gaze after releasing the mouse button
            if self.live2dlook:
                self.update_model_drag(event)
            else:
                pass

            # def a(): 
            #     self.newmotion('audio.wav')
            # motion_thread = threading.Thread(target=a)
            # motion_thread.start()               
    def newmotion(self,audio_path):

        # def start_motion():
            motion_values = segment_audio_and_classify(audio_path)
            # 定义数组
            # motion_values = [0, 0, 0, 0, 0, 3, 9, 10, 10, 10, 10, 10, 10, 9, 8, 9, 10, 10, 10, 10, 10, 10, 10, 8, 8, 10, 10, 10, 10, 9, 9, 8, 5, 0, 0, 0, 0, 0]

            # 遍历数组
            for value in motion_values:
                # 执行循环语句
                self.model.StartMotion("mytalk", value, live2dv3.MotionPriority.FORCE.value)
                start_time = time.time()
                # 循环直到时间间隔超过32毫秒
                while True:
                    current_time = time.time()
                    interval = (current_time - start_time) * 1000  # 将秒转换为毫秒
                    if interval >= 32:
                        # print(f"Interval reached or exceeded 32ms: {interval}ms")
                        break
                    # 调用StartMotion方法
            self.model.StartMotion("mytalk", 0, live2dv3.MotionPriority.FORCE.value)      
        # motion_thread = threading.Thread(target=start_motion)
        # motion_thread.start()
        # audio_path = '123.wav'
        # audio_player_thread = AudioPlayerThread1(audio_path)
        # audio_player_thread.start()
  

    # def mouth(self):
    #     if live2dver == 3:
    #         self.model.StartMotion("my", 0, live2dv3.MotionPriority.FORCE.value)
    #     else:
    #         self.model.StartMotion("my", 0, live2dv2.MotionPriority.FORCE.value)           
    #     #self.model.StartMotion("TapBody", 4, live2d.MotionPriority.FORCE.value)
    # def mouth1(self):
    #     if live2dver == 3:        
    #         self.model.StartMotion("TapBody", 0, live2dv3.MotionPriority.FORCE.value)
    #     else:
    #         self.model.StartMotion("TapBody", 0, live2dv2.MotionPriority.FORCE.value)
    def wrap_text(self, text, wrap_length=20):
        # 删除文本中所有的换行符和空格
        text = text.replace("\n", "").replace(" ", "")
        
        # 按wrap_length长度分割文本
        wrapped_parts = [text[i:i + wrap_length] for i in range(0, len(text), wrap_length)]
        
        # 使用换行符将分割后的文本部分连接起来
        wrapped_text = "\n".join(wrapped_parts)

        return wrapped_text

    def show_message_with_timeout(self, message, timeout):  # timeout 默认为10秒
        timeout = timeout+self.lasttime
        # 设置尺寸策略为固定
        # message = self.wrap_text(message)
        policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.message_label.setSizePolicy(policy)

        # 设置新样式，包括背景色、边框阴影等
        new_style = (
            f"font: bold {self.talksize}px; "
            "font-family: Microsoft YaHei;"
            "color: black; "
            "border-radius: 10px; "
            "text-align: center; "
            "background-color: rgba(255, 255, 255, 0.7); "  # 设置半透明白色背景
            f"min-width: {self.talkkuan}px; "
            "min-height: 50px; "
            "padding: 12px;"       # 添加内边距
            #"border: 2px solid rgba(255, 255, 255, 0.5);" 
        )
  
        
        self.message_label.setStyleSheet(new_style)
 


        self.message_label.setText(message)
        self.message_label.setAlignment(Qt.AlignCenter)  # 设置 QLabel 的对齐方式
        # self.message_label.adjustSize()

        # self.layout.addStretch(1)
        # self.message_label.addStretch(1)
        # 将 QLabel 添加到布局中
        self.layout.addWidget(self.message_label2)
        self.message_label.setWordWrap(True)

   
        self.layout.addWidget(self.message_label)
        self.layout.addWidget(self.message_label3) 
        # self.layout.addStretch(1)

        self.message_label.show()  # 确保标签是可见的
        self.message_timer.start(timeout)  # 启动定时器

    def hide_message(self):
        """
        隐藏消息标签。
        """
        self.message_label.clear()  # 清空文本
        self.message_label.hide()  # 隐藏标签
        self.message_timer.stop()  # 停止定时器


    # def on_start_motion_handler():
    #     print("动作开始！")

    # def on_finish_motion_handler():
    #     print("动作结束。")

    def audomotion(self,first):
        global stopmotiontime
        if not stopmotiontime:    
            # 调用 random_motion_selection 函数
            selected_motion = self.random_motion_selection(first)
            
            # 检查 selected_motion 是否为 None
            if selected_motion is None:
                print("随机选择失败，请检查数据字典是否正确加载。")
                return  # 退出方法，因为没有有效的运动数据

            # 从 selected_motion 字典中获取值
            motion, id, file, sound, text = selected_motion['motion'], selected_motion['id'], selected_motion['file'], selected_motion['sound'], selected_motion['text']
            

                # 启动 Live2D 模型的运动
            if live2dver == 3:
                self.model.StartMotion(motion, id, live2dv3.MotionPriority.FORCE.value)
            else: 
                self.model.StartMotion(motion, id, live2dv2.MotionPriority.FORCE.value)
            self.update()    
            
            # 检查 sound 是否存在，如果存在则播放音频
            if sound:  # 这里使用 truthy check 而不是 None 检查
                audio_player_thread = AudioPlayerThread(sound)
                audio_player_thread.start()
            
            # 检查 text 是否存在，如果存在则显示文本
            if text:  # 这里使用 truthy check 而不是 None 检查
                self.show_message_with_timeout(text, 0)
        else:
            print('播放中')
    def audomotion1(self):
        global stopmotiontime

        if not stopmotiontime:
            # 调用 random_motion_selection 函数
            selected_motion = self.random_motion_selection1(self.motionname)
            
            # 检查 selected_motion 是否为 None
            if selected_motion is None:
                print("随机选择失败，请检查数据字典是否正确加载。")
                return  # 退出方法，因为没有有效的运动数据

            # 从 selected_motion 字典中获取值
            motion, id, file, sound, text = selected_motion['motion'], selected_motion['id'], selected_motion['file'], selected_motion['sound'], selected_motion['text']

                # 启动 Live2D 模型的运动
            if live2dver == 3:
                self.model.StartMotion(motion, id, live2dv3.MotionPriority.FORCE.value)
            else: 
                self.model.StartMotion(motion, id, live2dv2.MotionPriority.FORCE.value)   
            self.update() 
            # 检查 sound 是否存在，如果存在则播放音频
            if sound:  # 这里使用 truthy check 而不是 None 检查
                audio_player_thread = AudioPlayerThread(sound)
                audio_player_thread.start()
            
            # 检查 text 是否存在，如果存在则显示文本
            if text:  # 这里使用 truthy check 而不是 None 检查
                self.show_message_with_timeout(text, 0)
        else:
            print('播放中')

    def yulan(self,motionname,path):
        parts = motionname.split('_')
        if len(parts) < 3:
            print("键名格式不正确，无法解析模型名、动作和编号。")
            return None
        name = self.modelname
        id_str = parts[-1]  # 最后一部分是 id
        motion = '_'.join(parts[1:-1])  # 中间部分是 motion
        id = int(id_str)  # 将编号转换为整数  
        self.model.StartMotion(motion, id, live2dv2.MotionPriority.FORCE.value)
        if path: 
            file = f"Resources/{name}/{path}"            
            audio_player_thread = AudioPlayerThread(file)
            audio_player_thread.start()         

    def widnowsize(self, w, h):
        self.width = w
        self.height = h
        self.resize(w, h)
        self.model.Resize(self.width,self.height)


    def reload_model(self, new_model_name, width, height):
        global stopmotiontime
        stopmotiontime = False
        self.motion_timer.stop()
        # 更新模型相关属性
        self.modelname = new_model_name
        self.width = width
        self.height = height
         

        # 调整窗口大小

        check_model_version(self.modelname)
        if live2dver == 3:
            self.model: live2dv3.LAppModel
        elif live2dver == 2:
            self.model: live2dv2.LAppModel
        else:
            pass        
        # # 销毁当前模型
        # self.model = None

        # 重新加载新模型
        if live2dver == 3:
            live2dv3.glewInit()
            live2dv3.setGLProperties()
            self.model = live2dv3.LAppModel()
            self.model.LoadModelJson("./Resources/"+self.modelname+"/"+self.modelname+".model3.json")
        else: 
            self.model = live2dv2.LAppModel()
            self.model.LoadModelJson("./Resources/"+self.modelname+"/"+self.modelname+".model.json")

        self.model.SetLipSyncN(self.mou)
        self.model.Resize(self.width,self.height)
        self.startTimer(int(1000 / self.fps))
        self.resize(self.width, self.height)

            # 重新连接信号和槽
        self.mouth_signal.connect(lambda: self.mouth())
        self.mouth_signal1.connect(lambda: self.mouth1())

        # 更新定时器
        self.timer.timeout.connect(self.update_model_gaze_to_cursor)
        self.timer.start(50)

        self.message_timer.timeout.connect(self.hide_message)

        self.motion_timer.timeout.connect(self.audomotion1)  # 连接定时器信号到槽函数
        motiontime = int(self.motiontime)

        self.motion_timer.start(motiontime*1000)
 
        # 更新显示

        self.update()

    def load_motion_config(self,motion_file_path=r"config/motion.json"):
        global global_motion_dict
        # 读取motion.json文件
        if os.path.exists(motion_file_path):
            with open(motion_file_path, 'r', encoding='utf-8') as f:
                global_motion_dict = json.load(f)
            print("motion.json文件已加载到全局字典中")
        else:
            print(f"未找到{motion_file_path}文件")

    def random_motion_selection(self,first):
        # 确保全局字典已经被加载
        if not global_motion_dict:
            print("全局字典尚未加载数据，请先调用load_motion_config函数加载数据。")
            return None
        if first:
            random_key = list(global_motion_dict.keys())[0]
        else:    
            # 随机选择一个键
            random_key = random.choice(list(global_motion_dict.keys()))

        # 分割键名以获取模型名、动作和编号
        parts = random_key.split('_')
        if len(parts) < 3:
            print("键名格式不正确，无法解析模型名、动作和编号。")
            return None

        model_name = self.modelname  # 直接赋值为参数 self.modelname
        id_str = parts[-1]  # 最后一部分是 id
        motion = '_'.join(parts[1:-1])  # 中间部分是 motion
        id = int(id_str)  # 将编号转换为整数

        # 获取对应的值
        motion_data = global_motion_dict[random_key]

        # 重新拼接文件路径
        file = f"Resources/{model_name}/{motion_data['File']}"

        # 提取声音信息，如果 sound 字段为空，则不拼接路径
        sound_path = motion_data.get('Sound')
        if sound_path:
            sound = f"Resources/{model_name}/{sound_path}"
        else:
            sound = ''

        # 提取文本信息
        text = motion_data.get('Text', '')

        # 返回处理后的变量
        return {
            'motion': motion,
            'id': id,
            'file': file,
            'sound': sound,
            'text': text
        }


    def random_motion_selection1(self, motion_type):
        # 确保全局字典已经被加载
        if not global_motion_dict:
            print("全局字典尚未加载数据，请先调用load_motion_config函数加载数据。")
            return None

        # 过滤出所有键名中动作类型与 motion_type 参数匹配的键
        filtered_keys = [key for key in global_motion_dict if '_'.join(key.split('_')[1:-1]) == motion_type]

        # 如果没有找到匹配的键，返回 None
        if not filtered_keys:
            print(f"没有找到动作类型为 '{motion_type}' 的数据。")
            return None

        # 随机选择一个过滤后的键
        random_key = random.choice(filtered_keys)

        # 分割键名以获取模型名和编号
        parts = random_key.split('_')
        if len(parts) < 3:
            print("键名格式不正确，无法解析模型名和编号。")
            return None

        model_name = self.modelname  # 直接赋值为参数 self.modelname
        id_str = parts[-1]  # 最后一部分是 id
        id = int(id_str)  # 将编号转换为整数

        # 获取对应的值
        motion_data = global_motion_dict[random_key]

        # 重新拼接文件路径
        file = f"Resources/{model_name}/{motion_data['File']}"

        # 提取声音信息，如果 sound 字段为空，则返回空字符串
        sound_path = motion_data.get('Sound', '')
        sound = f"Resources/{model_name}/{sound_path}" if sound_path else ''

        # 提取文本信息
        text = motion_data.get('Text', '')

        # 返回处理后的变量
        return {
            'motion': motion_type,  # 确保返回的动作类型与传入的参数匹配
            'id': id,
            'file': file,
            'sound': sound,
            'text': text
        }

def segment_audio_and_classify(file_path):
    # 载入音频文件
    audio = AudioSegment.from_file(file_path)
    
    # 定义片段长度，1000ms/30 即每段33.33ms
    segment_length_ms = 1000 / 30
    
    # 拆分音频
    segments = [audio[i * int(segment_length_ms):(i + 1) * int(segment_length_ms)] for i in range(int(len(audio) / segment_length_ms) + 1)]
    
    # 计算每个片段的响度
    loudnesses = []
    for seg in segments:
        # 用pydub的dBFS值计算响度，dBFS值越小，响度越大
        loudness = seg.dBFS
        loudnesses.append(loudness)
 
    # 移除 -inf 响度值，因为它们对应于完全静音的片段
    filtered_loudnesses = [l for l in loudnesses if l > -float('inf')]
    
    # 寻找最大和最小响度值
    max_loudness = max(filtered_loudnesses) if filtered_loudnesses else 0
    min_loudness = min(filtered_loudnesses) if filtered_loudnesses else 0
    # print(max_loudness,min_loudness)
    
    # 将响度值标准化到0-1区间
    normalized_loudnesses = [(l - min_loudness) / (max_loudness - min_loudness) if l > -float('inf') else 0 for l in loudnesses]
    
    # 识别静音片段
    silent_threshold = 0.1  # 可调整这个阈值来识别静音片段
    silent_segments = [i for i, l in enumerate(normalized_loudnesses) if l < silent_threshold]
    
    # 将每个非静音片段的响度值映射到1至5的范围内
    classified_segments = []
    for index, l in enumerate(normalized_loudnesses):
        if index in silent_segments:
            classified_segments.append(0)
        else:
            # 这里可以调整区间划分的方式，这里使用的是简单的线性映射
            classified_segments.append(min(int((l * 10) // 1) + 1, 10))
    
    # 打印结果
    return classified_segments




def upmotions(config_file_path=r"config/config.json"):
    global global_motion_dict
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
        

    # 在匹配的文件夹中查找.model3.json文件
    # 假设只处理找到的第一个.json文件
    json_files = [f for f in os.listdir(model_dir) if f.endswith('.model3.json')]
    model = 3
    if not json_files:
        json_files = [f for f in os.listdir(model_dir) if f.endswith('.model.json')]
        model = 2
        if not json_files:
            modle = 0
            print("没有找到.model3.json或.model.json文件")
            return  # 如果没有找到文件，则退出函数
    print(model)
    if json_files:  # 如果找到了.json文件
        selected_json_file = os.path.join(model_dir, json_files[0])
        with open(selected_json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # 根据模型类型处理motions
        if model == 3:
            # 从'FileReferences'下的'Motions'获取motions
            motions = json_data.get('FileReferences', {}).get('Motions', {})
        elif model == 2:
            # 直接从顶层获取motions
            motions = json_data.get('motions', {})

        # 确保motions已经被赋值
        if motions:
            auto_play_options = [name for name, motions_list in motions.items() if name != 'mytalk' and motions_list]

            # 更新AutoPlayAction的options列表
            config_data['AutoPlayAction']['options'] = auto_play_options

            # 存储Motions中的内容（忽略mytalk键）
            motion_content = {}
            for motion_name, motion_list in motions.items():
                if motion_name == 'mytalk':
                    continue
                for index, motion in enumerate(motion_list):
                    # 根据模型类型，使用正确的键来获取数据
                    file_key = 'File' if model == 3 else 'file'
                    sound_key = 'Sound' if model == 3 else 'sound'
                    # 对于model == 2，使用'msg_id'作为键，这里我们假设要使用它作为'Text'的值

                    # 生成key
                    if model == 3:
                        replace_extension = '.model3.json'
                    elif model == 2:
                        replace_extension = '.model.json'

                    base_name = os.path.basename(selected_json_file).replace(replace_extension, '')

                    key = f"{base_name}_{motion_name}_{index}"
                    motion_content[key] = {
                        "File": motion.get(file_key, ""),
                        "Sound": motion.get(sound_key, ""),
                        "Text": motion.get('Text', "") if model == 2 else motion.get("Text", "")
                    }

        else:
            print("JSON文件中没有找到motions数据")
    else:
        print("没有找到.model3.json或.model.json文件")
        model = 0


    # 保存内容到新的json文件
    new_motion_file_path = os.path.join("config", "motion.json")
    with open(new_motion_file_path, 'w', encoding='utf-8') as f:
        json.dump(motion_content, f, ensure_ascii=False, indent=4)

    # 写入更新后的配置数据到文件
    with open(config_file_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

    print("配置文件已更新，并已将Motions内容保存到新的motion.json文件中")






