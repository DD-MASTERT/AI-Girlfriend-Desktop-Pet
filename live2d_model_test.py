from PySide2.QtGui import QMouseEvent
import live2d.v3 as live2dv3
import live2d.v2 as live2dv2

from PySide2.QtCore import QTimerEvent
from PySide2.QtWidgets import QApplication, QMainWindow,QHBoxLayout, QPushButton, QLineEdit, QVBoxLayout, QWidget, QStyle, QLabel,QDialog, QComboBox,QSystemTrayIcon, QSlider, QMainWindow,QShortcut
from PySide2.QtWidgets import QOpenGLWidget
import json
import os
import glob
import sys


def callback():
    print("motion end")
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

class Win(QOpenGLWidget):  

    def __init__(self,modelname) -> None:
        super().__init__()
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.a = 0
        self.resize(570, 600)
        self.modelname = modelname
        check_model_version(self.modelname)
        if live2dver == 3:
            self.model: live2dv3.LAppModel
        elif live2dver == 2:
            self.model: live2dv2.LAppModel
        else:
            pass  
        self.modelpath = None     

    def initializeGL(self) -> None:

        # 将当前窗口作为 OpenGL 的上下文
        # 图形会被绘制到当前窗口
        self.makeCurrent()

        if live2dver == 3:
            live2dv3.glewInit()
            live2dv3.setGLProperties()
            self.model = live2dv3.LAppModel()
            self.modelpath ="./Resources/"+self.modelname+"/"+self.modelname+".model3.json"
            self.model.LoadModelJson(self.modelpath)
        else: 
            self.model = live2dv2.LAppModel()
            self.modelpath ="./Resources/"+self.modelname+"/"+self.modelname+".model.json"
            self.model.LoadModelJson(self.modelpath)

        # 设置口型同步幅度
        self.model.SetLipSyncN(5)

        # 以 fps = 30 的频率进行绘图
        self.startTimer(int(1000 / 30))
  

    def resizeGL(self, w: int, h: int) -> None:
        if self.model:
            # 使模型的参数按窗口大小进行更新
            self.model.Resize(w, h)
    
    def paintGL(self) -> None:
        if live2dver == 3:
            live2dv3.clearBuffer()
        else:
            live2dv2.clearBuffer()    
        self.model.Update()
    def timerEvent(self, a0: QTimerEvent | None) -> None:

        if self.a == 0: # 测试一次播放动作和回调函数
            # self.model.StartMotion("TapBody", 0, live2d.MotionPriority.FORCE.value)
            self.a += 1
        
        self.update() 

    def mousePressEvent(self, event: QMouseEvent) -> None:
        # 传入鼠标点击位置的窗口坐标
        self.model.Touch(event.pos().x(), event.pos().y());

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.model.Drag(event.pos().x(), event.pos().y())
    def cleanlive2dv3(self,file_path):
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 删除Motions中除了mytalk键之外的所有内容
        if 'Motions' in data['FileReferences']:
            motions = data['FileReferences']['Motions']
            keys_to_remove = [key for key in motions if key != 'mytalk']
            for key in keys_to_remove:
                del motions[key]

        # 保存修改后的JSON文件
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4) 
        mainui.edit.setText( '模型'+mainui.live2dcom.currentText()+'模型动作已清除')  
    def cleanlive2dv2(self,file_path):
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 删除motions字典中除了mytalk键以外的所有内容
        if 'motions' in data:
            motions = data['motions']
            keys_to_remove = [key for key in motions if key != 'mytalk']
            for key in keys_to_remove:
                del motions[key]

        # 将修改后的JSON写回文件
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        mainui.edit.setText( '模型'+mainui.live2dcom.currentText()+'模型动作已清除')  
    def upmodel(self,modelname):
        self.modelname = modelname
        check_model_version(self.modelname)
        if live2dver == 3:
            self.model: live2dv3.LAppModel
        elif live2dver == 2:
            self.model: live2dv2.LAppModel
        else:
            pass  
        if live2dver == 3:
            live2dv3.glewInit()
            live2dv3.setGLProperties()
            self.model = live2dv3.LAppModel()
            self.modelpath ="./Resources/"+self.modelname+"/"+self.modelname+".model3.json"
            self.model.LoadModelJson(self.modelpath)
        else: 
            self.model = live2dv2.LAppModel()
            self.modelpath ="./Resources/"+self.modelname+"/"+self.modelname+".model.json"
            self.model.LoadModelJson(self.modelpath)

        # 设置口型同步幅度
        self.model.SetLipSyncN(5)
        self.model.Resize(570,600)

        # 以 fps = 30 的频率进行绘图
        self.startTimer(int(1000 / 30))
        self.resize(570, 600)              
        self.update()
class ui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("live2d模型测试")
        self.layout = QVBoxLayout()

        self.layout1 = QHBoxLayout()
        self.laber1 = QLabel('检测到的live2d模型:')
        self.live2dcom = QComboBox()
        self.layout1.addWidget(self.laber1)
        self.layout1.addWidget(self.live2dcom)
        self.layout.addLayout(self.layout1)

        self.butto1 = QPushButton('点击切换模型')
        self.butto1.clicked.connect(self.changelive2dmodel)
        self.layout.addWidget(self.butto1)

        self.butto2 = QPushButton('删除模型的所有动作配置')
        self.butto2.clicked.connect(self.delatemotion)
        self.layout.addWidget(self.butto2)



        self.edit = QLineEdit()
        self.edit.setReadOnly(True)
        self.layout.addWidget(self.edit)

        self.butto3 = QPushButton('结束程序')
        self.butto3.clicked.connect(self.oobutto3)
        self.layout.addWidget(self.butto3)
        
        self.getallmodelname()
        self.live2dcom.setCurrentIndex(0)
        try:
            self.live2d = Win(self.live2dcom.currentText())
        except Exception as e:
            print(e)  
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

        self.resize(450 , 190)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
    def oobutto3(self):
        live2dv3.dispose()
        live2dv2.dispose()         
        app.quit()
    def getallmodelname(self,config_file_path=r"config/config.json"):
        # 读取配置文件
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 读取当前目录Resources文件夹中所有文件夹的名字
        resources_dir = os.path.join(os.getcwd(), 'Resources')
        folder_names = [d for d in os.listdir(resources_dir) if os.path.isdir(os.path.join(resources_dir, d))]

        self.live2dcom.addItems(folder_names)
    def changelive2dmodel(self):
        self.live2d.upmodel(self.live2dcom.currentText())
        self.edit.setText('模型'+self.live2dcom.currentText()+'更换成功')     
    def delatemotion(self):
        name = self.live2dcom.currentText()
        if live2dver == 3:
            modelpath ="./Resources/"+name+"/"+name+".model3.json"
            self.live2d.cleanlive2dv3(modelpath)
        else:
            modelpath ="./Resources/"+name+"/"+name+".model2.json"
            self.live2d.cleanlive2dv2(modelpath)    




if __name__ == "__main__":

    live2dv3.init()
    live2dv2.init()
    app = QApplication(sys.argv)
    mainui = ui()
    mainui.show()      
    mainui.live2d.show()
    app.exec_()

    if live2dver == 3: 
        live2dv3.dispose()
    else:
        live2dv2.dispose()    


# def clean_motions(file_path):
#     # 读取JSON文件
#     with open(file_path, 'r', encoding='utf-8') as file:
#         data = json.load(file)

#     # 删除Motions中除了mytalk键之外的所有内容
#     if 'Motions' in data['FileReferences']:
#         motions = data['FileReferences']['Motions']
#         keys_to_remove = [key for key in motions if key != 'mytalk']
#         for key in keys_to_remove:
#             del motions[key]

#     # 保存修改后的JSON文件
#     with open(file_path, 'w', encoding='utf-8') as file:
#         json.dump(data, file, ensure_ascii=False, indent=4) 
# clean_motions('./test/model/destroy/destroy.model3.json')              