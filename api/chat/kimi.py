import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# 将所有 selenium 相关的异常类放在一起导入
from selenium.common.exceptions import (
    NoSuchElementException, 
    TimeoutException, 
    StaleElementReferenceException
)



def refresh_textarea(driver):
    return WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[contenteditable="true'))
    )


def convert_to_single_line(text):
    # 使用 splitlines() 来分割文本为多行，然后使用 join() 将它们重新连接为一行
    single_line_text = '|'.join(text.splitlines())
    return single_line_text



def wait1(driver, message, timeout=120):
    try:
        # 使用WebDriverWait等待指定的时间
        wait = WebDriverWait(driver, timeout)
        
        # 检查message长度，并获取最后10个字符或整个message
        last_chars = message[-30:] if len(message) >= 30 else message
        
        # 定义等待条件：页面上的某个元素包含message的最后10个字符或整个message
        condition = lambda d: last_chars in d.page_source
        
        # 等待直到条件满足，或者超时
        wait.until(condition)
        
        print(f"The last characters of the message '{last_chars}' have appeared on the page.")
        return True
    except TimeoutException:
        print(f"The last characters of the message '{last_chars}' did not appear within {timeout} seconds.")
        return False


def send_message(driver, message):


    # 将消息转换为单行文本
    message = convert_to_single_line(message)

    # 重新定位 textarea 元素
    textarea = refresh_textarea(driver)

    # 清除 textarea 中已有的文本（如果有）
    textarea.clear()

    # 使用 JS 脚本点击 textarea 以确保其聚焦

    driver.execute_script("arguments[0].click();", textarea)
    
    # 在 textarea 中输入文本
    textarea.send_keys(message)


    
    # 定位到div内部的img元素
    img_element = driver.find_element(By.ID, 'send-button')
    
    # 使用 JS 脚本点击 img 元素发送消息
    img_element.click()
    return message

def text_stabilized(driver):
    try:
        # 定义新的等待条件：页面上出现class为“MuiTypography-root MuiTypography-body1 label___TPWYH css-17cnyc1”的元素
        condition = EC.presence_of_element_located((By.CSS_SELECTOR, ".MuiTypography-root.MuiTypography-body1.label___TPWYH.css-17cnyc1"))
        
        # 设置WebDriverWait，并等待条件满足
        wait = WebDriverWait(driver, 300)  # 200秒的等待时间
        wait.until(condition)
        
        # 如果条件满足，返回True
        return True
    except TimeoutException:
        # 如果在指定时间内条件未满足，返回False
        return False
def getaq(driver, message1):
    try:
        wait = WebDriverWait(driver, 400)

        # 首先调用text_stabilized函数检查文本是否稳定
        if not text_stabilized(driver):
            print("文本未稳定")
            return None

        # 等待页面上所有具有data-index属性的元素
        data_index_elements = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-index]'))
        )

        # 找到data-index属性的最大值
        data_indices = [int(el.get_attribute('data-index')) for el in data_index_elements]
        max_index = max(data_indices)

        # 使用最大data-index值寻找对应的元素
        max_index_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-index="{max_index}"]'))
        )

        # 在max_index_element的所有多级子集元素中查找class为.markdown___vuBDJ的元素
        markdown_elements = max_index_element.find_elements(By.XPATH, 
            ".//*[contains(@class, 'markdown___vuBDJ')]")

        # 检查markdown_elements变量是否包含元素
        if markdown_elements:
            element = markdown_elements[-1]  # 假设我们只关心最后一个找到的.markdown___vuBDJ类的元素
            return element.text
        else:
            print(f"在data-index为{max_index}的元素的子集中没有找到.markdown___vuBDJ类的元素。")
            return None

    except TimeoutException:
        print("在指定时间内未能找到元素")
        return None


def kimisend_and_update(driver, message):
    message1 = send_message(driver, message)
    if wait1(driver, message1):
        element_text = getaq(driver, message1)
        return element_text
    else:
        print("消息未在指定时间内出现。")  


def kimiclick_create_text_element(driver):
    try:
        # 使用CSS选择器定位具有指定类的元素
        create_text_element = driver.find_element(By.CSS_SELECTOR, '.myAgentToolIcon___gaAKI.myAgentToolIconNew___DBZrW')
        
        
        # 执行点击操作
        create_text_element.click()
        
        print("新建对话成功。")
    except Exception as e:
        print(f"点击元素时发生错误：{e}")

def kimitalk():

    # 初始化浏览器
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # 打开网页
    driver.get("https://kimi.moonshot.cn/") 
    return driver


def test(driver):

    while True:
        try:
            # 获取用户输入
            message = input("请输入消息（输入'退出'结束程序）: ")

            if message == "退出":
                print("程序结束。")
                break  # 退出循环

            if message == "新建对话":
                kimiclick_create_text_element(driver)
                continue  # 跳过循环的剩余部分，直接回到循环的开始
            
            # 调用 send_and_update 函数
            element_text = kimisend_and_update(driver, message)
            
            # 打印返回的清洗后的元素文本
            if element_text:  # 检查 element_text 是否为 None 或其他无效值
                print(element_text)
                message = "" 

        except Exception as e:
            print(f"发生错误：{e}")
            driver.quit()  # 发生异常时关闭浏览器
            break  # 退出循环

    # 如果程序正常结束循环，也关闭浏览器
    driver.quit()




