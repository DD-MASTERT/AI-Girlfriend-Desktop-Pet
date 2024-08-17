import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
import os

def wait_until_upload_complete(driver, timeout=60):
    try:
        # 等待文件列表容器显示
        file_list_box = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.file-list-box.isSmall'))
        )
        
        # 等待文件信息显示
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.file-box .file-info .name'))
        )
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.file-box .file-info .status .type'))
        )
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.file-box .file-info .status .size'))
        )
        
        print("文件上传完成")
        return True
    except Exception as e:
        print(f"文件上传失败或超时: {e}")
        return False
    
def upimg(driver):
    # 定位<input>元素
    input_element = driver.find_element(By.CSS_SELECTOR, 'input.el-upload__input')
    # 获取当前工作目录
    current_directory = os.getcwd()

    # 定义文件名
    filename = "config/123.jpg"

    # 拼接为绝对路径
    absolute_path = os.path.join(current_directory, filename)
    # 上传文件
    input_element.send_keys(absolute_path)
    wait_until_upload_complete(driver)

def refresh_textarea(driver):
    return WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'textarea.scroll-display-none'))
    )


def convert_to_single_line(text):
    # 使用 splitlines() 来分割文本为多行，然后使用 join() 将它们重新连接为一行
    single_line_text = '|'.join(text.splitlines())
    return single_line_text

def send_message(driver, message):

    # 将消息转换为单行文本
    message = convert_to_single_line(message)

    # 重新定位 textarea 元素
    textarea = refresh_textarea(driver)

    # 清除 textarea 中已有的文本（如果有）
    textarea.clear()

    # 使用 JS 脚本点击 textarea 以确保其聚焦

    driver.execute_script("arguments[0].click();", textarea)

    textarea.click()
    
    # 在 textarea 中输入文本
    textarea.send_keys(message)

    upimg(driver)    

    # 等待发送按钮可点击
    div_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.enter'))
    )

    # 定位到 div 内部的 img 元素
    img_element = div_element.find_element(By.CSS_SELECTOR, 'img.enter_icon')

    # 使用 JS 脚本点击 img 元素发送消息
    driver.execute_script("arguments[0].click();", img_element)

def text_stabilized(driver):
    try:
        # 定义图片的URL
        image_src = "/img/pause_session.c3f2da00.svg"
        

        # 等待直到具有指定src属性的图片元素消失
        element_present = EC.presence_of_element_located((By.XPATH, f"//img[@src='{image_src}']"))
        WebDriverWait(driver, 200).until_not(element_present)
        # 如果元素消失，返回True
        return True
    except TimeoutException:
        # 如果在指定的超时时间内元素没有消失，则返回False
        return False

def getaq(driver, initial_count):
    try:
        # 设置显式等待的超时时间，例如60秒，检查频率为0.2秒
        wait = WebDriverWait(driver, 200, poll_frequency=0.2)
        
        # 等待直到具有指定类名的元素数量增加
        wait.until(lambda d: len(d.find_elements(By.CLASS_NAME, "markdown-body.md-body.tl")) > initial_count)
        
        # 条件满足后的操作
        current_count = len(driver.find_elements(By.CLASS_NAME, "markdown-body.md-body.tl"))
        new_elements = driver.find_elements(By.CLASS_NAME, "markdown-body.md-body.tl")[
            initial_count:
        ]
        
        element_texts = []  # 用于存储新元素的文本
        for new_element in new_elements:
            new_id_str = new_element.get_attribute('id')
            if new_id_str:  # 检查ID是否存在
             #   print(f"New element with ID: {new_id_str}")
                
                # 使用 XPath 定位元素
                try:
                    # 使用xpath选择器定位元素
                    xpath_selector = f"//*[@id='{new_id_str}']"
                    element = driver.find_element(By.XPATH, xpath_selector)

                    # 等待文本稳定
                    is_stabilized = text_stabilized(driver)

                    if is_stabilized:
                        # 如果文本稳定，存储元素的文本
                        element_texts.append(element.text)
                    else:
                        # 如果文本不稳定，可以在这里处理超时的情况，例如重试或记录日志
                        print("Text stabilization timed out.")

                    
                except NoSuchElementException:
                    print(f"没有找到ID为 {new_id_str} 的元素")
        
        # 返回所有新元素的文本和当前计数
        return element_texts, current_count

    except TimeoutException:
        # 超时时返回失败信息和原始计数
        print("在指定时间内元素数量没有增加")
        return [], initial_count


def clean_text(text):
    # 如果 text 是列表，则取第一个元素
    if isinstance(text, list):
        text = text[0]
    
    # 去掉字符串开头和结尾的指定内容
    if text.startswith("['") and text.endswith("\n选择「段落」\n可继续追问～']"):
        text = text[2:-len("\n选择「段落」\n可继续追问～")+1]
    
    # 移除中间的 "选择「段落」" 和 "可继续追问～"
    text = text.replace("\n选择「段落」\n可继续追问～", "")
    
    return text




def send_and_update(driver, message):
    initial_count = len(driver.find_elements(By.CLASS_NAME, "markdown-body.md-body.tl"))
    send_message(driver, message)
    element_text, updated_count = getaq(driver, initial_count)
    element_text = clean_text(element_text)
    # 返回清洗后的元素文本
    return element_text



def click_create_text_element(driver):
    try:
        # 使用CSS选择器定位具有指定类的元素
        create_text_element = driver.find_element(By.CSS_SELECTOR, '.create-text')
        
        # 等待直到元素可点击
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        WebDriverWait(create_text_element, 10).until(EC.element_to_be_clickable(create_text_element))
        
        # 执行点击操作
        create_text_element.click()
        
        print("新建对话成功。")
    except Exception as e:
        return(f"点击元素时发生错误：{e}")


def talk(optionss, token):

    if optionss:
        # 设置 Chrome 选项以启用无头模式
        options = Options()
        options.add_argument("--headless")  # 启用无头模式
        options.add_argument("--disable-gpu")  # 禁用GPU硬件加速，某些系统上可能需要
        options.add_argument("--no-sandbox")  # 禁用沙盒模式，某些系统上可能需要
    else:
        options = Options()

    options.page_load_strategy = 'eager' 
    # 初始化浏览器

    # 指定 Chrome 浏览器的安装路径
    chrome_binary_path = "./sensvoice/Chrome/App/chrome.exe"
    options.binary_location = chrome_binary_path

    # 指定 ChromeDriver 的路径
    chromedriver_path = "./sensvoice/Chrome/App/chromedriver.exe"
    service = Service(executable_path=chromedriver_path)
    # 初始化浏览器
    driver = webdriver.Chrome(service=service, options=options)

    # 打开网页
    driver.get("https://chatglm.cn") 
    # 定义一个cookie字典
    cookie = {'name': 'chatglm_refresh_token', 'value': token, 'domain': 'chatglm.cn', 'path': '/'}

    # 添加cookie到浏览器
    driver.add_cookie(cookie)

    # 刷新页面使cookies生效
    driver.refresh()
    return driver

def updata(driver):
    # 定位元素
    element = driver.find_element_by_class_name('upload-image-btn upload-image-btn-dark')

    # 使用JavaScript执行点击操作
    driver.execute_script('arguments[0].click()', element)

def closedriver(driver):
    # 关闭Web驱动实例
    driver.quit()



