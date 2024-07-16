import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep  # 导入sleep函数
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from . utils import send_and_update, click_create_text_element



def main(optionss, token):

    if optionss:
        # 设置 Chrome 选项以启用无头模式
        options = Options()
        options.add_argument("--headless")  # 启用无头模式
        options.add_argument("--disable-gpu")  # 禁用GPU硬件加速，某些系统上可能需要
        options.add_argument("--no-sandbox")  # 禁用沙盒模式，某些系统上可能需要
    else:
        pass

    options.page_load_strategy = 'eager' 
    # 初始化浏览器

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # 打开网页
    driver.get("https://chatglm.cn") 
    # 定义一个cookie字典
    cookie = {'name': 'chatglm_refresh_token', 'value': token, 'domain': 'chatglm.cn', 'path': '/'}

    # 添加cookie到浏览器
    driver.add_cookie(cookie)

    # 刷新页面使cookies生效
    driver.refresh()

    while True:
        try:
            # 获取用户输入
            message = input("请输入消息（输入'退出'结束程序）: ")

            if message == "退出":
                print("程序结束。")
                break  # 退出循环

            if message == "新建对话":
                click_create_text_element(driver)
                continue  # 跳过循环的剩余部分，直接回到循环的开始
            
            # 调用 send_and_update 函数
            element_text = send_and_update(driver, message)
            
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




if __name__ == "__main__":
    main(optionss, token)