try:
    import psutil
    import os
    import re
    import time
    from pywinauto.mouse import move, click, double_click, press, release
    from pywinauto import keyboard
    from pywinauto.keyboard import send_keys
    import webbrowser
except Exception as e:
    print(e)    

class auto:
    def __init__(self,file):
        self.shortcut_path = None
        self.file = file
        self.filename = None
        self.can1 = None
        self.can2 = None
        self.can3 = None
    def closeexe(self,name):
         #关闭指定应用
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == name:
                proc.kill()                   
    def open(self):
        # 打开应用快捷方式
        os.startfile(self.shortcut_path) 

    def move_mouse_to(self,x, y):
        """
        移动鼠标到指定坐标 (x, y)
        :param x: 目标位置的x坐标
        :param y: 目标位置的y坐标
        """
        move(coords=(x, y))

    def left_click(self, x, y):
        """
        在指定坐标 (x, y) 处执行左键单击
        :param x: 目标位置的x坐标
        :param y: 目标位置的y坐标
        """
        click(button='left', coords=(x, y))

    def right_click(self, x, y):
        """
        在指定坐标 (x, y) 处执行右键单击
        :param x: 目标位置的x坐标
        :param y: 目标位置的y坐标
        """
        click(button='right', coords=(x, y))

    def double_click(self, x, y):
        """
        在指定坐标 (x, y) 处执行左键双击
        :param x: 目标位置的x坐标
        :param y: 目标位置的y坐标
        """
        double_click(button='left', coords=(x, y))

    def drag_mouse(self, start_x, start_y, end_x, end_y):
        """
        从起始坐标 (start_x, start_y) 拖动鼠标到目标坐标 (end_x, end_y)
        :param start_x: 起始位置的x坐标
        :param start_y: 起始位置的y坐标
        :param end_x: 目标位置的x坐标
        :param end_y: 目标位置的y坐标
        """
        move(coords=(start_x, start_y))
        press(button='left', coords=(start_x, start_y))
        move(coords=(end_x, end_y))
        release(button='left', coords=(end_x, end_y))
    def left_button_down(self, x, y):
        """
        在指定坐标 (x, y) 处按下左键
        :param x: 目标位置的x坐标
        :param y: 目标位置的y坐标
        """
        press(button='left', coords=(int(x), int(y)))

    def left_button_up(self, x, y):
        """
        在指定坐标 (x, y) 处释放左键
        :param x: 目标位置的x坐标
        :param y: 目标位置的y坐标
        """
        release(button='left', coords=(int(x), int(y)))
    # 键盘操作函数
    def press_and_release_key(self, key, duration):
        """
        按下某个键一段时间然后松开

        参数:
        key (str): 要按下的键，例如 'a', 'b', 'enter', 'space' 等。
        duration (float): 按下键的持续时间，以秒为单位。
        """
        # 按下指定的键
        send_keys(f'{{{key} down}}')
        
        # 持续指定的时间
        time.sleep(duration)
        
        # 释放键
        send_keys(f'{{{key} up}}')
    def send_key(self, key):
        """
        发送单个按键
        :param key: 要发送的按键
        """
        send_keys(key)

    def send_combo_key(self, keys):
        """
        发送组合按键
        :param keys: 要发送的组合按键，例如 "Ctrl+C"
        """
        send_keys(keys, with_spaces=True)

    def send_text(self, text, delay=0.1):
        """
        发送文本
        :param text: 要发送的文本
        :param delay: 每次发送后的延迟时间（秒）
        :param chunk_size: 每次发送的字符数
        """
        special_chars = {
            '{': '{{}',
            '}': '{}}',
            '+': '{+}',
            '^': '{^}',
            '%': '{%}',
            '~': '{~}',
            '(': '{(}',
            ')': '{)}'
        }

        def escape_text(text):
            for char, escape in special_chars.items():
                text = text.replace(char, escape)
            return text

        # 分割文本成多行
        lines = text.split('\n')

        for line in lines:
            # 转义每行中的特殊字符
            escaped_line = escape_text(line)
            send_keys(escaped_line, with_spaces=True)
            # 发送换行符
            send_keys('{ENTER}')
            time.sleep(delay)

    def open_website(self, url):
        """
        使用默认的网页浏览器打开指定的URL。

        :param url: 要打开的网站的URL。
        """
        webbrowser.open(url)  
    def pandaun(self, input):
        if '参数1' in input:
            input = input.replace('参数1', str(self.can1))
        if '参数2' in input:
            input = input.replace('参数2', str(self.can2))
        if '参数3' in input:
            input = input.replace('参数3', str(self.can3))
        return input                    
    def fenge(self, text):
        parts = text.split('，')
        for i in range(len(parts)):
            parts[i] = self.pandaun(parts[i])

        if parts[0] == '打开' and len(parts) > 1:
            self.shortcut_path = parts[1]
            self.open()
        elif parts[0] == '等待' and len(parts) > 1:
            t = float(parts[1])
            time.sleep(t)
        elif parts[0] == '关闭' and len(parts) > 1:
            self.closeexe(parts[1])
        elif parts[0] == '移动到' and len(parts) > 2:
            x = int(parts[1])
            y = int(parts[2])
            self.move_mouse_to(x, y)
        elif parts[0] == '按左键' and len(parts) > 2:
            x = int(parts[1])
            y = int(parts[2])
            self.left_button_down(x, y)
        elif parts[0] == '松左键' and len(parts) > 2:
            x = int(parts[1])
            y = int(parts[2])
            self.left_button_up(x, y)
        elif parts[0] == '左键' and len(parts) > 2:
            x = int(parts[1])
            y = int(parts[2])
            self.left_click(x, y)
        elif parts[0] == '右键' and len(parts) > 2:
            x = int(parts[1])
            y = int(parts[2])
            self.right_click(x, y)
        elif parts[0] == '双左键' and len(parts) > 2:
            x = int(parts[1])
            y = int(parts[2])
            self.double_click(x, y)
        elif parts[0] == '选中移动' and len(parts) > 4:
            x1 = int(parts[1])
            y1 = int(parts[2])
            x2 = int(parts[3])
            y2 = int(parts[4])
            self.drag_mouse(x1, y1, x2, y2)
        elif parts[0] == '按住键' and len(parts) > 2:
            t = float(parts[2])
            self.press_and_release_key(parts[1], t)
        elif parts[0] == '单键' and len(parts) > 1:
            self.send_key(parts[1])
        elif parts[0] == '组合键' and len(parts) > 1:
            self.send_combo_key(parts[1])
        elif parts[0] == '文本' and len(parts) > 1:
            self.send_text(parts[1])
        elif parts[0] == '打开网站' and len(parts) > 1:
            self.open_website(parts[1])
        else:
            pass                                                          
    def read(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                content = file.read()
                lines = content.splitlines()
                for line in lines:
                    # # 调用fenge函数处理每一行
                    self.fenge(line)
            print("脚本已执行")        
        except FileNotFoundError:
            print(f"脚本有错误，请检查书写是否正确。")
        except Exception as e:
            print(f"读取文件时发生错误：{e}")
    def order(self, order):
        name = order
        if len(name) > 1:
            name = name[1:-1]
        # 修改正则表达式以匹配多行内容
        pattern = re.compile(r'\*\*\{(.*?)\}\*\*', re.DOTALL)

        contents = []  # 存储匹配到的 **{...}** 内容
        placeholders = []  # 存储替换后的特殊标记

        def replace_with_placeholder(match):
            content = match.group(1)  # 获取匹配到的括号内的内容
            placeholder = f"__{len(contents)}__"  # 创建一个特殊的标记
            contents.append(content)  # 存储内容
            placeholders.append(placeholder)  # 存储特殊标记
            return placeholder

        # 使用正则表达式替换函数
        name_with_placeholders = pattern.sub(replace_with_placeholder, name)

        # 使用 '-' 来分割字符串
        parts = name_with_placeholders.split('-')

        # 将存储的内容按照它们原本的顺序放回分割后的字符串中
        for i, part in enumerate(parts):
            # 替换第一个找到的特殊标记
            part = re.sub(r'__\d+__', lambda m: contents[int(m.group(0)[2:-2])], part, count=1)
            parts[i] = part
            
        # 处理 parts 列表的元素
        if len(parts) > 1 and parts[1]:
            self.find_file_by_name(parts[1])
        if len(parts) > 2 and parts[2]:
            self.can1 = parts[2]
        if len(parts) > 3 and parts[3]:
            self.can2 = parts[3]
        if len(parts) > 4 and parts[4]:
            self.can3 = parts[4]      
        self.read()   

    def find_file_by_name(self, name):
        """
        遍历指定文件夹，找到文件名与给定名称匹配的文件，并返回其路径。

        :param folder_path: 要遍历的文件夹路径。
        :param name: 要查找的文件名（不包含扩展名）。
        :return: 匹配文件的完整路径，如果没有找到则返回None。
        """
        # 遍历文件夹中的所有文件和文件夹
        for root, dirs, files in os.walk(self.file):
            for file in files:
                # 检查文件名（不包含扩展名）是否与给定名称匹配
                if file.split('.')[0] == name:
                    # 返回匹配文件的完整路径
                    path = os.path.join(root, file)
                    self.filename = path
                else:
                    pass                                 

# # 获取当前工作目录
# current_working_directory = os.getcwd()
# # 构建脚本文件的绝对路径
# path = os.path.join(current_working_directory, 'order')    


# try:
#     # 尝试执行订单操作
#     au = auto(path) 
#     str1 = '[-order9-1.py-print("你好")-]'
#     au.order(str1)
# except Exception as e:
#     # 如果发生异常，打印错误信息
#     print(f"An error occurred: {e}")

# # 无论是否发生异常，都等待用户按下任意键再退出
# input("Press any key to exit...")


  