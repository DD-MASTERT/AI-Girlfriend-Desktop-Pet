import sys
from PySide6.QtWidgets import QHBoxLayout,QApplication,QLineEdit, QWidget, QVBoxLayout, QComboBox, QPushButton, QTextEdit,QLabel
import os
import threading
import json
from PySide6.QtCore import QTimer

class ScriptRunnerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        with open('api_key.json', 'r', encoding='utf-8') as file:
            self.data = json.load(file)
        self.oldtype = ''        
        # 创建布局
        self.layout1 =QVBoxLayout()
        self.layouth =QHBoxLayout()        
        # 下拉菜单
        self.modeltype = QComboBox()
        self.modeltype.addItems(['siliconflow', '智普glm', '阿里通义千问','百度千帆文心一言','kimi','MiniMax海螺','字节豆包','讯飞星火','零一万物'])
        self.modeltype.currentIndexChanged.connect(self.creat)
        self.layouth.addWidget(QLabel('API类别(保存时该选项也是当前调用的API)'))
        self.layouth.addWidget(self.modeltype)
        self.layout1.addLayout(self.layouth)

        # 创建按钮
        self.runButton = QPushButton("保存", self)
        self.runButton.clicked.connect(self.save)


        self.laber1 = QLabel('')
        self.edit1 = QLineEdit('')        
        self.laber2 = QLabel('')
        self.edit2 = QLineEdit('')
        self.laber3 = QLabel('')
        self.edit3 = QLineEdit('')  
        self.layout2 =QVBoxLayout()
        self.lah1 = QHBoxLayout()
        self.lah2 = QHBoxLayout()
        self.lah3 = QHBoxLayout()
                                             
        self.layout1.addLayout(self.layout2)  
        self.layout1.addWidget(self.runButton)                   
        # 将控件添加到布局     
        self.startype(self.data['type'])
        self.creat()
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.load)
        # self.timer.start(50)
        self.setStyleSheet("""                                                            
            QGroupBox {
                font-family: Arial;
                background-color: rgba(0 , 0 , 0, 1.0);
                font: bold 25px;
                border-radius: 50px;           
                margin-top: 200px;
            }
            QPushButton {
                font-family: Arial;
                background-color: rgba(0, 0, 0, 1.0);
                font: bold 15spx;
                border: 2px solid black;
                border-radius: 10px;
                padding: 8px;
                color: white;
                text-align: center;
                min-width: 100px;
            }
            QPushButton:hover {
                color: black;
                background-color: rgba(255, 255, 255, 1);
            }
            QLineEdit {
                font-family: Arial;
                background-color: rgba(255, 255, 255, 1.0);
                font: bold 15px;
                border-radius: 10px;
                padding: 5px;
                color: black;
                min-width: 300px;
            }
            QLineEdit:hover {
                background-color: rgba(0, 0, 0, 1.0);
                color: white;


            }
            QComboBox {
                font-family: Arial;
                background-color: rgba(255, 255, 255, 1.0);
                font: bold 15px;
                text-align: center;
                border-radius: 10px;
                padding: 5px;
                color: black;
                min-width: 150px;
                text-align: center;           
            }
            QComboBox:hover {
                background-color: rgba(0, 0 , 0, 1);
                color: white;           
                           
            }
            QComboBox QAbstractItemView {
                background-color: rgba(0, 0, 0, 1.0);           
                font-family: Arial;
                font: bold 15px;
                background-color: white;
                text-align: center;
                padding: 5px;
                border: none;
                color: black;            
                text-align: center;           
                selection-background-color:white;
            }
            QLabel {
                font-family: Arial;
                font: bold 15px;
                text-align: center;           
                color: black;
                text-align: center;
                min-width: 75px;
                /* 其他样式属性 */
            }
        """)

        # 设置布局
        self.setLayout(self.layout1)


        # 设置窗口标题和初始大小
        self.setWindowTitle("模型API-key")
        self.setFixedWidth(500)  # 固定窗口宽度为400像素
        self.resize(500, 250)

    def load(self): 
        if self.oldtype != self.modeltype.currentText():  
            self.creat()
    def creatlah(self):
        self.lah1.addWidget(self.laber1)
        self.lah1.addWidget(self.edit1)
        self.lah2.addWidget(self.laber2)
        self.lah2.addWidget(self.edit2)
        self.lah3.addWidget(self.laber3)
        self.lah3.addWidget(self.edit3)  

    def clear(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)  # 移除 widget 但不删除
                else:
                    # 如果 item 不是 widget，可能是布局或其他类型的项
                    sub_layout = item.layout()
                    if sub_layout:
                        # 移除子布局但不删除
                        sub_layout.setParent(None)
                        self.clear(sub_layout)
                    layout.removeItem(item)
            else:
                # 如果 item 为 None，可能是因为布局中没有项了
                break
        
    def creat(self):
        self.clear(self.layout2) 
        self.creatlah()                           
        mod = self.modeltype.currentIndex() 
        if mod==0:
           self.laber1.setText("API_key:")
           self.laber2.setText("模型名称")
           self.layout2.addLayout(self.lah1)
           self.layout2.addLayout(self.lah2)
           self.edit1.setText(self.data['siliconflow_api_key'])
           self.edit2.setText(self.data['siliconflow_model'])                         
        elif mod==1:    
           self.laber1.setText("API_key:")
           self.laber2.setText("模型名称")          
           self.layout2.addLayout(self.lah1)
           self.layout2.addLayout(self.lah2)
           self.edit1.setText(self.data['zhipu_apikey'])
           self.edit2.setText(self.data['zhipu_model'])             
        elif mod==2:    
           self.laber1.setText("API_key:")
           self.laber2.setText("模型名称")          
           self.layout2.addLayout(self.lah1)
           self.layout2.addLayout(self.lah2)
           self.edit1.setText(self.data['tongyi_apikey'])
           self.edit2.setText(self.data['tongyi_model'])               
        elif mod==3:    
           self.laber1.setText("Accesskey:")
           self.laber2.setText("Secretkey:")
           self.laber3.setText("模型名称")         
           self.layout2.addLayout(self.lah1)
           self.layout2.addLayout(self.lah2)
           self.layout2.addLayout(self.lah3)
           self.edit1.setText(self.data['qianfan_accesskey'])
           self.edit2.setText(self.data['qianfan_secretkey'])
           self.edit3.setText(self.data['qianfan_model'])            
        elif mod==4:    
           self.laber1.setText("API_key:")
           self.laber2.setText("模型名称")         
           self.layout2.addLayout(self.lah1)
           self.layout2.addLayout(self.lah2)
           self.edit1.setText(self.data['kimi_key'])
           self.edit2.setText(self.data['kimi_model'])           
        elif mod==5:    
           self.laber1.setText("API_key:")
           self.laber2.setText("模型名称")         
           self.layout2.addLayout(self.lah1)
           self.layout2.addLayout(self.lah2)
           self.edit1.setText(self.data['minimax_key'])
           self.edit2.setText(self.data['minimax_model'])             
        elif mod==6:    
           self.laber1.setText("API_key:")
           self.laber2.setText("模型名称")         
           self.layout2.addLayout(self.lah1)
           self.layout2.addLayout(self.lah2)
           self.edit1.setText(self.data['doubao_api'])
           self.edit2.setText(self.data['doubao_id'])             
        elif mod==7:    
           self.laber1.setText("Accesskey:")
           self.laber2.setText("Secretkey:")
           self.laber3.setText("模型名称")         
           self.layout2.addLayout(self.lah1)
           self.layout2.addLayout(self.lah2)
           self.layout2.addLayout(self.lah3)
           self.edit1.setText(self.data['xf_ak'])
           self.edit2.setText(self.data['xf_as'])  
           self.edit3.setText(self.data['xf_model'])                  
        elif mod==8:    
           self.laber1.setText("API_key:")
           self.laber2.setText("模型名称")         
           self.layout2.addLayout(self.lah1)
           self.layout2.addLayout(self.lah2)
           self.edit1.setText(self.data['yi_key'])
           self.edit2.setText(self.data['yi_model'])                                                       
        self.oldtype = self.modeltype.currentText() 
        self.data['type']=self.get_model_by_index(mod)           

    def startype(self,model):
        if model=="siliconflow":
            self.modeltype.setCurrentIndex(0)
        elif model=='zhipu':
            self.modeltype.setCurrentIndex(1)
        elif model=='tongyi':
            self.modeltype.setCurrentIndex(2)
        elif model=='qianfan':
            self.modeltype.setCurrentIndex(3)
        elif model=='kimi':
            self.modeltype.setCurrentIndex(4) 
        elif model=='minimax':
            self.modeltype.setCurrentIndex(5)
        elif model=='doubao':
            self.modeltype.setCurrentIndex(6)
        elif model=='xf':
            self.modeltype.setCurrentIndex(7)
        elif model=='yi':
            self.modeltype.setCurrentIndex(8)
        else:
            self.modeltype.setCurrentIndex(0)                                                                        
        self.oldtype = self.modeltype.currentText()
    def get_model_by_index(self, index):
        model_dict = {
            0: "siliconflow",
            1: "zhipu",
            2: "tongyi",
            3: "qianfan",
            4: "kimi",
            5: "minimax",
            6: "doubao",
            7: "xf",
            8: "yi"
        }
        return model_dict.get(index, "unknown")        
    def save(self):
        mod = self.modeltype.currentIndex() 
        if mod == 0:
            self.data['siliconflow_api_key'] = self.edit1.text()
            self.data['siliconflow_model'] = self.edit2.text()

        elif mod == 1:
            self.data['zhipu_apikey'] = self.edit1.text()
            self.data['zhipu_model'] = self.edit2.text()

        elif mod == 2:
            self.data['tongyi_apikey'] = self.edit1.text()
            self.data['tongyi_model'] = self.edit2.text()

        elif mod == 3:
            self.data['qianfan_accesskey'] = self.edit1.text()
            self.data['qianfan_secretkey'] = self.edit2.text()
            self.data['qianfan_model'] = self.edit3.text()

        elif mod == 4:
            self.data['kimi_key'] = self.edit1.text()
            self.data['kimi_model'] = self.edit2.text()

        elif mod == 5:
            self.data['minimax_key'] = self.edit1.text()
            self.data['minimax_model'] = self.edit2.text()

        elif mod == 6:
            self.data['doubao_api'] = self.edit1.text()
            self.data['doubao_id'] = self.edit2.text()

        elif mod == 7:
            self.data['xf_ak'] = self.edit1.text()
            self.data['xf_as'] = self.edit2.text()
            self.data['xf_model'] = self.edit3.text()

        elif mod == 8:
            self.data['yi_key'] = self.edit1.text()
            self.data['yi_model'] = self.edit2.text()       
        self.data['type']=self.get_model_by_index(mod)
        with open('api_key.json', 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)        
        
                       
ui = None
def main():
    global ui
    # 创建应用程序实例
    app = QApplication(sys.argv)

    # 创建 UI 实例
    ui = ScriptRunnerUI()

    # 显示 UI
    ui.show()

    # 运行应用程序
    sys.exit(app.exec())

if __name__ == '__main__':
    main()