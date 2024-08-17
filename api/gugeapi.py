from chat.utils import talk, click_create_text_element, send_and_update, closedriver
import json
import uvicorn
from fastapi import FastAPI, Request
import time
from pydantic import BaseModel
import asyncio
import os

llm = 'glm'
driver = None

def getdriver():
    global driver
    with open('api/gsv.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    TOKEN = data['chatglm_refresh_token']
    OPTIONS = True
    driver = talk(OPTIONS, TOKEN)

getdriver()

def after():
    global driver
    time.sleep(1)
    click_create_text_element(driver)

app = FastAPI()

class Data(BaseModel):
    message: str

@app.post("/run/")
async def run_model_inference(data: Data):
    global driver
    try:
        result = send_and_update(driver, data.message)
        # 创建一个后台任务来执行 after 函数
        asyncio.create_task(asyncio.to_thread(after))
        return result
    except Exception as e:
        return {"error": str(e)}

# 用于关闭服务的路由
@app.post("/shutdown")
async def shutdown(request: Request):
    global driver
    try:
        closedriver(driver)
        server = request.app.state.server
        server.should_exit = True
        return {"message": "Shutting down server."}
    except Exception as e:
        return {"error": str(e)}

# 主函数，用于启动Uvicorn服务器
if __name__ == "__main__":
    server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=2001))
    app.state.server = server
    server.run()

    # while True:
    #     i = input('输入：')
    #     if i!='退出':
    #         out = send_and_update(driver,i)
    #         print(out)
    #     else:
    #         closedriver(driver)    
