import sys
from PySide6.QtWidgets import QApplication,QLineEdit, QWidget, QVBoxLayout, QComboBox, QPushButton, QTextEdit
from PySide6.QtCore import QDir
import os
from myauto import auto
import threading


def star(roder):
    global ui
    try:
        # 获取当前工作目录
        current_working_directory = os.getcwd()
        # 构建脚本文件的绝对路径
        path = os.path.join(current_working_directory, 'order')
        # 假设auto是一个类，并且它有一个order方法
        au = auto(path)
        au.order(roder)
    except Exception as e:
        # 这里处理异常，e是异常对象
        ui.readOnlyBox.append(f"错误: {e}")
    ui.readOnlyBox.append('脚本执行成功')    
class ScriptRunnerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 创建布局
        layout = QVBoxLayout()

        # 创建下拉框
        self.comboBox = QComboBox(self)
        self.comboBox.setEditable(False)  # 设置为非编辑模式
        self.load_filenames()  # 加载文件名到下拉框
        # 创建输入框
        self.inputBox = QLineEdit(self)
        self.inputBox.setPlaceholderText("输入指令")
        # 创建只读输入框
        self.readOnlyBox = QTextEdit(self)
        self.readOnlyBox.setPlaceholderText("执行结果将显示在这里")
        self.readOnlyBox.setReadOnly(True)

        # 创建按钮
        self.runButton = QPushButton("执行脚本", self)
        self.runButton.clicked.connect(self.run_script)

        # 将控件添加到布局
        layout.addWidget(self.inputBox)       
        layout.addWidget(self.comboBox)
        layout.addWidget(self.readOnlyBox)
        layout.addWidget(self.runButton)
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
                min-width: 100px;
            }
            QLineEdit:hover {
                background-color: rgba(255, 255, 255, 1.0);


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
                max-width: 50px;
                /* 其他样式属性 */
            }
        """)        

        # 设置布局
        self.setLayout(layout)

        # 设置窗口标题和初始大小
        self.setWindowTitle("脚本执行器")
        self.setGeometry(300, 300, 300, 200)

    def load_filenames(self):
        # 加载同级目录下order文件夹中所有.txt文件的名字
        order_dir = QDir(self.directory_path('order'))
        for file in order_dir.entryList(['*.txt']):
            self.comboBox.addItem(file)

    def directory_path(self, folder_name):
        # 获取当前脚本所在目录的路径，并添加文件夹名称

        return os.path.join(os.getcwd(), folder_name)

    def run_script(self):
        name = self.inputBox.text()
        if len(name) > 1:
            name = name[1:-1]
        parts = name.split('-')
        # 获取当前选中的脚本文件名
        selected_script_name = parts[1] + ".txt"

        # 获取当前工作目录
        current_working_directory = os.getcwd()

        # 构建脚本文件的绝对路径
        script_path = os.path.join(current_working_directory, 'order', selected_script_name)
        try:
            with open(script_path, 'r', encoding='utf-8') as file:
                script_content = file.read()
                # 将文件内容作为执行结果显示
                result = "脚本内容：\n" + script_content
                self.readOnlyBox.append(result)
                order = self.inputBox.text()
                print(script_path)
                print(order)
                th = threading.Thread(target=star, args=(order,))
                th.start()
        except FileNotFoundError:
            self.readOnlyBox.append("错误：文件未找到。")
        except Exception as e:
            self.readOnlyBox.append(f"执行脚本时发生错误：{e}")
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